import os
from sentence_transformers import SentenceTransformer
from info import FileInfo, FolderInfo

MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")


def generate_embeddings(folder_info: FolderInfo, model: SentenceTransformer = MODEL):
    if folder_info.summary:
        folder_info.summary_embedding = model.encode(folder_info.summary)

    if folder_info.children_info:
        for child_info in folder_info.children_info.values():
            if isinstance(child_info, FileInfo):
                print(child_info.path)
                if child_info.summary:
                    child_info.summary_embedding = model.encode(child_info.summary)
            elif isinstance(child_info, FolderInfo):
                print(child_info.path)
                generate_embeddings(child_info, model)


def generate_embedding(sentence: str, model: SentenceTransformer = MODEL):
    return model.encode(sentence)


if __name__ == "__main__":
    from datetime import datetime

    # Replace this example with your actual FolderInfo instance
    # example_folder_info = FolderInfo(
    #     path="codebases/langchain",
    #     summary=None,
    #     children_info={
    #         "langchain": FolderInfo(
    #             path="codebases/langchain/langchain",
    #             summary=None,
    #             children_info={
    #                 "serpapi.py": FileInfo(
    #                     path="codebases/langchain/langchain/serpapi.py",
    #                     summary="The 'serpapi.py' Python file is used to provide backwards compatibility...",
    #                 )
    #             },
    #         )
    #     },
    # )

    folder_info = FolderInfo.load_from_json("outputs/03_22_01_04_04.json")

    generate_embeddings(folder_info)
    print(folder_info)

    date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
    folder_info.save_to_msgpack(f"outputs/{date_time}.msgpack")
