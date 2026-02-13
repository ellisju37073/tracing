"""JSON file storage handler."""

import json
from pathlib import Path
from typing import Any, List, Dict, Union


class JSONStorage:
    """Storage handler for JSON files."""

    def __init__(self, filepath: str):
        """Initialize the JSON storage.

        Args:
            filepath: Path to the JSON file.
        """
        self.filepath = Path(filepath)
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the parent directory exists."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: Union[Dict, List], indent: int = 2) -> None:
        """Save data to JSON file.

        Args:
            data: Data to save (dict or list).
            indent: JSON indentation level.
        """
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    def load(self) -> Union[Dict, List, None]:
        """Load data from JSON file.

        Returns:
            The loaded data, or None if file doesn't exist.
        """
        if not self.filepath.exists():
            return None

        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def append(self, item: Any) -> None:
        """Append an item to a JSON array file.

        Args:
            item: Item to append.
        """
        data = self.load() or []
        if not isinstance(data, list):
            raise ValueError("Cannot append to non-array JSON file")
        data.append(item)
        self.save(data)

    def update(self, key: str, value: Any) -> None:
        """Update a key in a JSON object file.

        Args:
            key: Key to update.
            value: New value.
        """
        data = self.load() or {}
        if not isinstance(data, dict):
            raise ValueError("Cannot update non-object JSON file")
        data[key] = value
        self.save(data)

    def exists(self) -> bool:
        """Check if the JSON file exists.

        Returns:
            True if file exists, False otherwise.
        """
        return self.filepath.exists()
