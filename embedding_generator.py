import os
import argparse
from datetime import datetime
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
    parser = argparse.ArgumentParser(
        description="Generate embedings for the folder info"
    )
    parser.add_argument(
        "--info_path", help="Path to the folder info json folder"
    )  # "outputs/03_22_21_30_12.json"
    args = parser.parse_args()
    folder_info = FolderInfo.load_from_json(args.info_path)

    generate_embeddings(folder_info)
    print(folder_info)

    date_time = datetime.now().strftime("%m_%d_%H_%M_%S")
    folder_info.save_to_msgpack(f"outputs/{date_time}.msgpack")
