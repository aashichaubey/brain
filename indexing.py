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

def sync_index (memories_dir, collection):
    disk = {}
    for path in glob(f"{memories_dir}/**/*.md", recursive = True):
        disk[path] = hashlib.md5(open(path, "rb").read()).hexdigest()
    
    indexed = get_all_metadata(collection)

