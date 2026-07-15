import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def create_filename(title: str) -> str:
    """Convert a title into a safe filename."""
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")

    return f"{slug or 'memory'}-{uuid.uuid4().hex[:8]}.md"


def add_to_memory(
    memories_dir: str,
    title: str,
    text: str,
    metadata: dict | None = None,
) -> Path:
    """
    Create a markdown memory on disk.

    Indexing into ChromaDB happens separately through sync_index().
    """
    if not text.strip():
        raise ValueError("Memory text cannot be empty.")

    metadata = metadata or {}

    scope = metadata.get("scope", "personal")
    repository = metadata.get("repository", "general")
    memory_type = metadata.get("type", "general")

    folder = Path(memories_dir) / scope / repository
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / create_filename(title)

    created_at = datetime.now(timezone.utc).isoformat()

    markdown = f"""---
title: "{title}"
scope: "{scope}"
repository: "{repository}"
type: "{memory_type}"
created_at: "{created_at}"
---

# {title}

{text.strip()}
"""

    file_path.write_text(markdown, encoding="utf-8")

    return file_path