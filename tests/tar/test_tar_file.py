"""Tests for umbi.tar.tar_file module."""

import pathlib

import pytest

from umbi.tar import TarFile


class TestTarFileBasics:
    """Test basic TarFile functionality."""

    def test_create_empty_tarfile(self):
        """Test creating an empty TarFile."""
        tf = TarFile()
        assert len(tf) == 0
        assert list(tf.filenames) == []

    def test_add_and_retrieve_file(self):
        """Test adding and retrieving a file."""
        tf = TarFile()
        data = b"hello world"
        tf.add_file("test.txt", data)

        assert tf.has_file("test.txt")
        assert tf.read_file("test.txt") == data

    def test_has_file(self):
        """Test checking if file exists."""
        tf = TarFile()
        assert not tf.has_file("nonexistent.txt")

        tf.add_file("exists.txt", b"data")
        assert tf.has_file("exists.txt")

    def test_get_required_file_missing(self):
        """Test that missing required file raises KeyError."""
        tf = TarFile()
        with pytest.raises(KeyError):
            tf.read_file("missing.txt")

    def test_get_optional_file_missing(self):
        """Test that missing optional file returns None."""
        tf = TarFile()
        result = tf.read_file("missing.txt", optional=True)
        assert result is None

    def test_add_file_duplicate_without_overwrite(self):
        """Test that adding duplicate file without overwrite raises error."""
        tf = TarFile()
        tf.add_file("file.txt", b"original")

        with pytest.raises(KeyError):
            tf.add_file("file.txt", b"new")

    def test_add_file_duplicate_with_overwrite(self):
        """Test that overwrite flag allows replacing files."""
        tf = TarFile()
        tf.add_file("file.txt", b"original")
        tf.add_file("file.txt", b"new", overwrite=True)

        result = tf.read_file("file.txt")
        assert result is not None
        assert result == b"new"

    def test_filenames_property(self):
        """Test filenames property."""
        tf = TarFile()
        tf.add_file("a.txt", b"data1")
        tf.add_file("b.txt", b"data2")
        tf.add_file("c.txt", b"data3")

        filenames = list(tf.filenames)
        assert len(filenames) == 3
        assert "a.txt" in filenames
        assert "b.txt" in filenames
        assert "c.txt" in filenames


class TestTarFileIO:
    """Test reading and writing tarfiles."""

    def test_write_and_read_tarfile(self, tmp_path: pathlib.Path):
        """Test writing and reading a tarfile."""
        # Write
        tf1 = TarFile()
        tf1.add_file("file1.txt", b"content1")
        tf1.add_file("file2.txt", b"content2")

        tarpath = tmp_path / "test.tar.gz"
        tf1.write(tarpath)

        # Read
        tf2 = TarFile(tarpath)
        assert tf2.has_file("file1.txt")
        assert tf2.has_file("file2.txt")
        content1 = tf2.read_file("file1.txt")
        assert content1 is not None
        assert content1 == b"content1"
        content2 = tf2.read_file("file2.txt")
        assert content2 is not None
        assert content2 == b"content2"

    def test_write_and_read_empty_tarfile(self, tmp_path: pathlib.Path):
        """Test writing and reading an empty tarfile."""
        tf1 = TarFile()

        tarpath = tmp_path / "empty.tar.gz"
        tf1.write(tarpath)

        tf2 = TarFile(tarpath)
        assert len(tf2) == 0

    def test_write_with_different_compression(self, tmp_path: pathlib.Path):
        """Test writing with different compression formats."""
        tf = TarFile()
        tf.add_file("test.txt", b"data")

        for compression in ["gz", "bz2", "xz"]:
            tarpath = tmp_path / f"test.tar.{compression}"
            tf.write(tarpath, compression=compression)  # type: ignore

            tf_loaded = TarFile(tarpath)
            data = tf_loaded.read_file("test.txt")
            assert data is not None
            assert data == b"data"

    def test_read_nonexistent_file(self, tmp_path: pathlib.Path):
        """Test that reading nonexistent tarfile raises error."""
        tarpath = tmp_path / "nonexistent.tar.gz"

        with pytest.raises(FileNotFoundError):
            TarFile(tarpath)


class TestTarFileDict:
    """Test dict-like interface."""

    def test_tarfile_is_dict(self):
        """Test that TarFile behaves like a dict."""
        tf = TarFile()
        tf["key1"] = b"value1"
        tf["key2"] = b"value2"

        assert tf["key1"] == b"value1"
        assert tf["key2"] == b"value2"
        assert len(tf) == 2

    def test_iteration(self):
        """Test iterating over TarFile."""
        tf = TarFile()
        tf["a"] = b"data_a"
        tf["b"] = b"data_b"
        tf["c"] = b"data_c"

        keys = list(tf.keys())
        assert len(keys) == 3
        assert "a" in keys
