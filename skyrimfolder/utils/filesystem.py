import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Self, Union


class FileSystemEntry(ABC):
    """
    An abstract base class representing a file system entry, such as a file or directory.

    Attributes:
        path (Path): The path of the file system entry.
        name (str): The name of the file system entry.

    Methods:
        _calculate_size(): Calculates and returns the size of the file system entry.
        delete(): Deletes the file system entry.
        rename(new_name): Renames the file system entry to the specified new name.
        relative_to(other): Returns the relative path of the file system entry
                            with respect to another entry or a Path instance.
        __eq__(other): Compares two FileSystemEntry instances for equality
                       based on their file system paths.
        __hash__(): Returns the hash value of the FileSystemEntry's path.
    """

    def __init__(self, path: Union[str, Path]):
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._path.name

    @abstractmethod
    def _calculate_size(self) -> int:
        """Calculates and returns the size of the file system entry."""
        pass

    @abstractmethod
    def delete(self) -> None:
        """Deletes the file system entry."""
        pass

    @abstractmethod
    def rename(self, new_name: str) -> None:
        """Renames the file system entry to the specified new name."""
        pass

    def relative_to(self, other: Union["FileSystemEntry", Path]) -> Path:
        other_path: Path
        if isinstance(other, FileSystemEntry):
            other_path = other._path
        elif isinstance(other, Path):
            other_path = other
        else:
            raise TypeError(f"Expected a FileSystemEntry or Path instance")

        return self._path.relative_to(other_path)


class File(FileSystemEntry):
    def __init__(self, path: Union[str, os.PathLike, Path]):
        self._path = Path(path)
        self._size = self._calculate_size()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def size(self) -> int:
        return self._size

    def _calculate_size(self) -> int:
        return self._path.stat().st_size

    def read(self) -> str:
        with self._path.open("r") as f:
            return f.read()

    def read_binary(self) -> bytes:
        with self._path.open("rb") as f:
            return f.read()

    def write(self, content: str) -> None:
        with self._path.open("w") as f:
            f.write(content)

    def write_binary(self, content: bytes) -> None:
        with self._path.open("wb") as f:
            f.write(content)

    def append(self, content: str) -> None:
        with self._path.open("a") as f:
            f.write(content)

    def delete(self) -> None:
        self._path.unlink()

    def rename(self, new_name: str) -> Self:
        new_path = self._path.parent / new_name
        self._path.rename(new_path)
        return File(new_path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, File):
            return False
        return self._path == other._path

    def __hash__(self) -> int:
        return hash(self._path)


class Directory(FileSystemEntry):
    def __init__(self, path: Union[str, os.PathLike, Path]):
        self._path = Path(path)
        self._children = self._get_children()
        self._size = self._calculate_size()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def children(self) -> List:
        return self._children

    @property
    def size(self) -> int:
        total_size = 0
        for child in self.children:
            total_size += child.size
        return total_size

    @property
    def name(self) -> str:
        return self._path.name

    def _get_children(self) -> List:
        children = []

        for child_path in self._path.iterdir():
            if child_path.is_file():
                children.append(File(child_path))
            elif child_path.is_dir():
                children.append(Directory(child_path))

        return children

    def __iter__(self):
        return iter(self._children)

    def _calculate_size(self) -> int:
        total_size = 0
        for child in self.children:
            total_size += child.size
        return total_size

    def get_child(self, name: str) -> Optional[Union["Directory", File]]:
        for child in self._children:
            if child.name == name:
                return child
        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Directory):
            return False
        return self._path == other._path

    def __hash__(self) -> int:
        return hash(self._path)

    def __contains__(self, item: Union["Directory", File]) -> bool:
        return item in self._children

    def walk(self) -> Iterable[Union["Directory", File]]:
        for child in self:
            yield child
            if isinstance(child, Directory):
                yield from child.walk()

    def filter(
        self, predicate: Callable[[Union["Directory", File]], bool]
    ) -> List[Union["Directory", File]]:
        return [child for child in self._children if predicate(child)]

    def delete(self, force: bool = False) -> None:
        if force:
            shutil.rmtree(self._path)
        else:
            self._path.rmdir()

    def rename(self, new_name: str) -> "Directory":
        new_path = self._path.parent / new_name
        self._path.rename(new_path)
        return Directory(new_path)

    def relative_to(self, other: Union["Directory", Path]) -> Path:
        if isinstance(other, Directory):
            other_path = other._path
        else:
            other_path = other
        return self._path.relative_to(other_path)
