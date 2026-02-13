"""Tests for storage handlers."""

import pytest
import tempfile
import os
from src.storage import JSONStorage, CSVStorage


class TestJSONStorage:
    @pytest.fixture
    def temp_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)  # Delete so we start with non-existent file
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_save_and_load_dict(self, temp_json):
        storage = JSONStorage(temp_json)
        data = {"key": "value", "number": 42}
        storage.save(data)
        loaded = storage.load()
        assert loaded == data

    def test_save_and_load_list(self, temp_json):
        storage = JSONStorage(temp_json)
        data = [1, 2, 3, "test"]
        storage.save(data)
        loaded = storage.load()
        assert loaded == data

    def test_append_to_list(self, temp_json):
        storage = JSONStorage(temp_json)
        storage.save([1, 2])
        storage.append(3)
        loaded = storage.load()
        assert loaded == [1, 2, 3]

    def test_update_dict(self, temp_json):
        storage = JSONStorage(temp_json)
        storage.save({"a": 1})
        storage.update("b", 2)
        loaded = storage.load()
        assert loaded == {"a": 1, "b": 2}

    def test_exists(self, temp_json):
        storage = JSONStorage(temp_json)
        assert not storage.exists()
        storage.save({})
        assert storage.exists()


class TestCSVStorage:
    @pytest.fixture
    def temp_csv(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        os.unlink(path)  # Delete so we start with non-existent file
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_save_and_load(self, temp_csv):
        storage = CSVStorage(temp_csv)
        data = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"},
        ]
        storage.save(data)
        loaded = storage.load()
        assert len(loaded) == 2
        assert loaded[0]["name"] == "Alice"

    def test_append_row(self, temp_csv):
        storage = CSVStorage(temp_csv, fieldnames=["name", "age"])
        storage.append({"name": "Alice", "age": "30"})
        storage.append({"name": "Bob", "age": "25"})
        loaded = storage.load()
        assert len(loaded) == 2

    def test_exists(self, temp_csv):
        storage = CSVStorage(temp_csv)
        assert not storage.exists()
        storage.save([{"a": "1"}])
        assert storage.exists()
