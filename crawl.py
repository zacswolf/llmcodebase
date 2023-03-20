import argparse
import os

from gen_python import gen_py_info
import os
from git import Repo
import fnmatch



def generate_info(path, include_patterns=None, exclude_patterns=None, repo=None, gitignore=True):
    if repo is None:
        try:
            repo = Repo(path, search_parent_directories=True)
        except:
            pass

    if gitignore and repo is not None and (len(repo.ignored(path)) or path.endswith(".git")):
        # Ignore
        return None

    pass
    if exclude_patterns and any(fnmatch.filter([path], pat) for pat in exclude_patterns):
        # Exclude files that match any of the given exclude_patterns
        return None

    if include_patterns and not any(fnmatch.filter([path], pat) for pat in include_patterns):
        # Exclude files that do not match any of the given include_patterns
        return None

    level_info = {}

    if os.path.isfile(path):
        file_info = process_file(path)
        if file_info:
            level_info[path] = file_info
    elif os.path.isdir(path):
        folder_info, children_info = process_folder(path, include_patterns=include_patterns, exclude_patterns=exclude_patterns, repo=repo, gitignore=gitignore)
        level_info[path] = folder_info
        level_info.update(children_info)

    return level_info


def process_file(path):
    with open(path, "r") as f:
        path_extension = os.path.splitext(path)[1]
        file_name = os.path.basename(path)

        match path_extension:
            case ".py":
                contents = f.read()
                return gen_py_info(path, file_name, contents)
            # TODO: Add more file types here
            case _:
                return None


def process_folder(path, include_patterns=None, exclude_patterns=None, repo=None, gitignore=True):
    folder_name = os.path.basename(path)
    children_info = {}

    for child_name in os.listdir(path):
        child_path = os.path.join(path, child_name)
        child_info = generate_info(child_path, include_patterns=include_patterns, exclude_patterns=exclude_patterns, repo=repo, gitignore=gitignore)
        children_info[child_name] = child_info

    folder_info = gen_folder_info(folder_name, children_info)
    return folder_info, children_info


def gen_folder_info(folder_name, children_info):
    # TODO: Implement folder info generation
    pass


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Crawl a codebase and generate information about each level"
#     )
#     parser.add_argument(
#         "--root_path", help="Path to the root directory of the codebase", default="."
#     )



#     args = parser.parse_args()

#     codebase_info = generate_info(args.root_path)

#     # In the future we will use codebase_info as a dynamic context provided to an LLM through a program that can use the LLM answer questions about our codebase or to be given a task like help onboard a new developer.

#     # For now, we will just print the codebase info
#     print(codebase_info)


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
    print(codebase_info)


