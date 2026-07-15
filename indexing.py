# Keep index aligned with markdown on disk (after git sync)

"""
Detecting changes after a pull
Compare the set of file paths on disk vs the set of IDs in the index
- Path on disk but not in index -> new file. Embed, insert
- ID in index but no file on disk -> deleted file. Remove from index
- Path in both -> could be unchanged or edited 
this requires a content hash so we store its has in the vector's metadata
On reindex has the file on disk and compare to the stored hash. D
Different -> re embed and upsert
Same -> skip


"""

# disk = {
#   "memories/likes-spicy-food.md": "a3f9c2...",
#   "memories/go-api-notes.md":     "77b01e...",
# }

import hashlib
from pathlib import Path


def get_file_hash(path: Path) -> str:
    """Return a hash representing the file's current contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_all_metadata(collection) -> dict:
    """
    Return indexed memories as:

    {
        "personal/preferences.md": {
            "content_hash": "...",
            ...
        }
    }
    """
    results = collection.get(include=["metadatas"])

    indexed = {}

    for memory_id, metadata in zip(
        results.get("ids", []),
        results.get("metadatas", []),
    ):
        indexed[memory_id] = metadata or {}

    return indexed


def sync_index(memories_dir: str, collection) -> dict:
    memories_root = Path(memories_dir)

    # Read all markdown files currently on disk.
    disk = {}

    for path in memories_root.rglob("*.md"):
        memory_id = path.relative_to(memories_root).as_posix()

        disk[memory_id] = {
            "path": path,
            "content_hash": get_file_hash(path),
        }

    # Read all existing Chroma records.
    indexed = get_all_metadata(collection)

    disk_ids = set(disk)
    indexed_ids = set(indexed)

    new_ids = disk_ids - indexed_ids
    deleted_ids = indexed_ids - disk_ids

    changed_ids = {
        memory_id
        for memory_id in disk_ids & indexed_ids
        if disk[memory_id]["content_hash"]
        != indexed[memory_id].get("content_hash")
    }

    # Add new files and update changed files.
    for memory_id in new_ids | changed_ids:
        file_info = disk[memory_id]
        content = file_info["path"].read_text(encoding="utf-8")

        collection.upsert(
            ids=[memory_id],
            documents=[content],
            metadatas=[
                {
                    "file_path": memory_id,
                    "content_hash": file_info["content_hash"],
                }
            ],
        )

    # Remove records whose markdown files were deleted.
    if deleted_ids:
        collection.delete(ids=list(deleted_ids))

    return {
        "added": sorted(new_ids),
        "updated": sorted(changed_ids),
        "deleted": sorted(deleted_ids),
        "unchanged": sorted(
            (disk_ids & indexed_ids) - changed_ids
        ),
    }