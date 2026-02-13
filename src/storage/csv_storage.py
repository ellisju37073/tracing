"""CSV file storage handler."""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional


class CSVStorage:
    """Storage handler for CSV files."""

    def __init__(self, filepath: str, fieldnames: Optional[List[str]] = None):
        """Initialize the CSV storage.

        Args:
            filepath: Path to the CSV file.
            fieldnames: List of column names. If None, will be inferred.
        """
        self.filepath = Path(filepath)
        self.fieldnames = fieldnames
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the parent directory exists."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: List[Dict[str, Any]]) -> None:
        """Save data to CSV file.

        Args:
            data: List of dictionaries to save.
        """
        if not data:
            return

        fieldnames = self.fieldnames or list(data[0].keys())

        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def load(self) -> List[Dict[str, Any]]:
        """Load data from CSV file.

        Returns:
            List of dictionaries from the CSV file.
        """
        if not self.filepath.exists():
            return []

        with open(self.filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def append(self, row: Dict[str, Any]) -> None:
        """Append a row to the CSV file.

        Args:
            row: Dictionary representing a row.
        """
        file_exists = self.filepath.exists() and self.filepath.stat().st_size > 0
        fieldnames = self.fieldnames or list(row.keys())

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def append_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Append multiple rows to the CSV file.

        Args:
            rows: List of dictionaries representing rows.
        """
        if not rows:
            return

        file_exists = self.filepath.exists()
        fieldnames = self.fieldnames or list(rows[0].keys())

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows)

    def exists(self) -> bool:
        """Check if the CSV file exists.

        Returns:
            True if file exists, False otherwise.
        """
        return self.filepath.exists()
