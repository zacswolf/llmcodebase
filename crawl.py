import argparse
from datetime import datetime
import os
from pprint import pprint

from gen_python import gen_py_info
from gen_folder import gen_folder_info
import os
from git import Repo
import fnmatch
from info import FileInfo, FolderInfo



def generate_info(path, include_patterns=None, exclude_patterns=None, repo=None, gitignore=True):
    if repo is None:
        try:
            repo = Repo(path, search_parent_directories=True)
        except:
            pass

    if gitignore and repo is not None and (len(repo.ignored(path)) or path.endswith(".git")):
        # Ignore
        return None

    if exclude_patterns and any(fnmatch.filter([path], pat) for pat in exclude_patterns):
        # Exclude files that match any of the given exclude_patterns
        return None

    if include_patterns and not any(fnmatch.filter([path], pat) for pat in include_patterns):
        # Exclude files that do not match any of the given include_patterns
        return None


    if os.path.isfile(path):
        file_info = process_file(path)
        return file_info
    elif os.path.isdir(path):
        folder_info = process_folder(path, include_patterns=include_patterns, exclude_patterns=exclude_patterns, repo=repo, gitignore=gitignore)
        return folder_info

    raise ValueError(f"Path is neither a file nor a directory: {path}")


def process_file(path) -> FileInfo | None:
    with open(path, "r") as f:
        path_extension = os.path.splitext(path)[1]
        file_name = os.path.basename(path)

        match path_extension:
            case ".py":
                contents = f.read()
                summary = gen_py_info(path, file_name, contents)
                return FileInfo(path, summary)
            # TODO: Add more file types here
            case _:
                return None


def process_folder(path, include_patterns=None, exclude_patterns=None, repo=None, gitignore=True) -> FolderInfo:
    children_info = {}

    for child_name in os.listdir(path):
        child_path = os.path.join(path, child_name)
        child_info = generate_info(child_path, include_patterns=include_patterns, exclude_patterns=exclude_patterns, repo=repo, gitignore=gitignore)
        children_info[child_name] = child_info

    folder_summary = gen_folder_info(path, children_info)
    return FolderInfo(path, folder_summary, children_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl a codebase and generate information about each level"
    )
    parser.add_argument(
        "--root_path", help="Path to the root directory of the codebase", default="."
    )
    parser.add_argument(
        "-P",
        "--include",
        action="append",
        help="List only those files that match any of the given patterns.",
        default=[],
    )
    parser.add_argument(
        "-I",
        "--exclude",
        action="append",
        help="Do not list files that match any of the given patterns.",
        default=[],
    )
    parser.add_argument(
        "--gitignore", help="Filter by using .gitignore files.", action="store_true"
    )

    args = parser.parse_args()

    codebase_info = generate_info(args.root_path, include_patterns=args.include, exclude_patterns=args.exclude, gitignore=args.gitignore)

    # In the future we will use codebase_info as a dynamic context provided to an LLM through a program that can use the LLM answer questions about our codebase or to be given a task like help onboard a new developer.

    # For now, we will just print the codebase info
    print("\n\n\n\n\n")
    print(codebase_info.to_dict())
    import json
    date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
    with open(f"outputs/{date_time}.json", "w") as f:
        json.dump(codebase_info.to_dict(), f,indent=1)


