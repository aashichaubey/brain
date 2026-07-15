from ingestion import add_to_memory

path = add_to_memory(
    memories_dir="./memories",
    title="Campaign service convention",
    text="Campaign business logic should use service objects.",
    metadata={
        "scope": "team",
        "repository": "shop-campaigns",
        "type": "convention",
    },
)

print("Created:", path)
print("\nFile contents:")
print(path.read_text())