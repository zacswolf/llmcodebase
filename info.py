import os
import json
import msgpack
from torch import Tensor
import typing


class FileInfo:
    def __init__(
        self, path: os.PathLike, summary: str, summary_embedding: Tensor | None = None
    ):
        self.path = path
        self.summary = summary
        self.summary_embedding = summary_embedding

    def to_dict(self):
        return {
            "path": self.path,
            "summary": self.summary,
            "summary_embedding": self.summary_embedding.tolist()
            if self.summary_embedding is not None
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        summary_embedding = None
        if data.get("summary_embedding") is not None:
            summary_embedding = Tensor(data["summary_embedding"])
        return cls(data["path"], data["summary"], summary_embedding)

    def __repr__(self):
        return self.to_dict().__repr__()


class FolderInfo:
    def __init__(
        self,
        path: os.PathLike,
        summary: str,
        children_info: dict[str, typing.Self | FileInfo | None] = None,
        summary_embedding: Tensor | None = None,
    ):
        self.path = path
        self.summary = summary
        self.children_info = children_info
        self.summary_embedding = summary_embedding

    def to_dict(self):
        return {
            "path": self.path,
            "summary": self.summary,
            "summary_embedding": self.summary_embedding.tolist()
            if self.summary_embedding is not None
            else None,
            "children_info": {
                child_name: child_info.to_dict() if child_info is not None else None
                for child_name, child_info in self.children_info.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict):
        children_info = {
            child_name: (
                FileInfo.from_dict(child_data)
                if "children_info" not in child_data
                else FolderInfo.from_dict(child_data)
            )
            for child_name, child_data in data["children_info"].items()
        }
        summary_embedding = None
        if data.get("summary_embedding") is not None:
            summary_embedding = Tensor(data["summary_embedding"])
        return cls(data["path"], data["summary"], children_info, summary_embedding)

    def __repr__(self):
        return self.to_dict().__repr__()

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def from_dict(cls, data: dict) -> "FolderInfo":
        path = data["path"]
        summary = data["summary"]
        children_info = {}

        for child_name, child_data in data["children_info"].items():
            if child_data is None:
                children_info[child_name] = None
            elif "children_info" in child_data:
                children_info[child_name] = FolderInfo.from_dict(child_data)
            else:
                children_info[child_name] = FileInfo(**child_data)

        return cls(path, summary, children_info)

    def save_to_json(self, file_path: os.PathLike) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_json(cls, file_path: os.PathLike) -> "FolderInfo":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls.from_dict(data)

    def save_to_msgpack(self, file_path: os.PathLike) -> None:
        with open(file_path, "wb") as file:
            msgpack.dump(self.to_dict(), file, use_bin_type=True)

    @classmethod
    def load_from_msgpack(cls, file_path: os.PathLike) -> "FolderInfo":
        with open(file_path, "rb") as file:
            data = msgpack.load(file, raw=False)
        return cls.from_dict(data)
