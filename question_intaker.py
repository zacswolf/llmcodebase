from pprint import pprint
from torch import Tensor
import torch
from torch.nn.functional import cosine_similarity
from info import FileInfo, FolderInfo
from llm import call_llm, llm_checklength
import argparse
from embedding_generator import generate_embedding
from queue import PriorityQueue


# Impliment a root to answer crawler implemented using LLM
# The LLM uses the supplied question and the folder info to dynamically load context to find the answer
# This is going to be LLM that has access to tools
# The commands are going to be:

# Possible commands right now just have to deal with the file system
# OPEN(file_name|folder_name)
# EXPAND(file_name|folder_name)
# CLOSE(file_name|folder_name)


# Types of questions:
# What is the structure of the


def collect_summary_embeddings(
    info: FolderInfo, enable_folder=True, enable_file=True
) -> list[tuple[str, Tensor]]:
    embeddings = []
    if info.summary_embedding is not None and enable_folder:
        embeddings.append((info.summary, info.summary_embedding))

    for child in info.children_info.values():
        if child is not None:
            if isinstance(child, FolderInfo):
                embeddings.extend(
                    collect_summary_embeddings(
                        child, enable_file=enable_file, enable_folder=enable_folder
                    )
                )
            elif (
                isinstance(child, FileInfo)
                and child.summary_embedding is not None
                and enable_file
            ):
                embeddings.append((child.summary, child.summary_embedding))

    return embeddings


def get_context_sentence_transformers(
    question: str,
    info: FolderInfo,
    top_k: int = 15,
    enable_folder=True,
    enable_file=True,
) -> list[tuple[str, float]]:
    question_embedding = torch.tensor(generate_embedding(question))

    # Collect summary embeddings
    summary_embeddings = collect_summary_embeddings(info, enable_folder, enable_file)

    # Find the top k most similar sentences in the folder info
    top_sentences = PriorityQueue(maxsize=top_k)

    for summary, embedding in summary_embeddings:
        embedding = torch.tensor(embedding)
        similarity = cosine_similarity(
            question_embedding.unsqueeze(0), embedding.unsqueeze(0)
        ).item()

        # If the PriorityQueue is not full or the current similarity is higher than the lowest similarity in the queue
        if top_sentences.full():
            lowest_similarity, _ = top_sentences.get()
            if similarity > lowest_similarity:
                top_sentences.put((similarity, summary))
        else:
            top_sentences.put((similarity, summary))

    # Return the top k most similar sentences as a list
    return [
        (summary, similarity)
        for similarity, summary in sorted(
            top_sentences.queue, key=lambda x: x[0], reverse=True
        )
    ]


def ask_question(question: str, folder_info: FolderInfo):
    most_rel = get_context_sentence_transformers(
        question, folder_info, enable_folder=True
    )

    prompt = create_prompt(question, [context for context, score in most_rel])
    fits_in_one_request = llm_checklength(prompt)
    if fits_in_one_request:
        answer = call_llm(prompt)
    else:
        # Handle very long sections if needed
        print(f"Very long section, not implemented yet: {folder_info.path}")
        raise NotImplementedError

    prompt = context_feedback_prompt(question, [context for context, score in most_rel])
    feedback_context = call_llm(prompt)

    prompt = answer_feedback_prompt(question, answer)
    feedback_answer = call_llm(prompt)
    return answer, feedback_context, feedback_answer


def create_prompt(question: str, context_list: list[str]) -> str:

    prompt = "Context:\n"
    for context in context_list:
        prompt += f"- {context}\n"
    prompt += f"\nThe user asked: {question}\n\n"
    prompt += "\nPlease answer the user's question."
    return prompt


def context_feedback_prompt(question: str, context_list: list[str]) -> str:
    prompt = "Context:\n"
    for context in context_list:
        prompt += f"- {context}\n"
    # prompt += f"\nThe user asked: {question}\n\n"
    # prompt += "\nHow relevant is the above context to the user's question?"
    prompt += f'\n\nIf the user asked "{question}". How relevant is the above context to the user\'s question?'
    return prompt


def filter_context_prompt(question: str, context_list: list[str]) -> str:
    prompt = "Context:\n"
    for idx, context in enumerate(context_list):
        prompt += f"<Context {idx+1}>\n{context}\n</Context {idx+1}>\n"
    # prompt += f"\nThe user asked: {question}\n\n"
    # prompt += "\nHow relevant is the above context to the user's question?"
    prompt += f'\n\nIf the user asked "{question}". What are the relevant context blocks, respond with the numbers of the context blocks separated by a space.'
    return prompt


def answer_feedback_prompt(question: str, answer: str) -> str:
    prompt = f"\nThe user asked: {question}\n\n"
    prompt += f"The model answered: {answer}\n\n"
    prompt += "\nHow relevant is the above answer to the user's question?"
    return prompt


def clean_question(question: str):
    question = question.strip()
    if question[-1] != "?":
        question += "?"
    return question


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q",
        "--question",
        help="The question to ask the codebase",
        default="What is the overall purpose of this project?",
    )
    parser.add_argument(
        "-p", "--path", help="The path to the index file"
    )  # outputs/03_22_21_43_21.msgpack
    args = parser.parse_args()

    question = clean_question(args.question)
    path = args.path
    folder_info = FolderInfo.load_from_msgpack(path)

    # answer = ask_question(question, folder_info)
    # most_rel = get_context_sentence_transformers(question, folder_info)
    # pprint(most_rel)

    answer, context_feedback, answer_feedback = ask_question(question, folder_info)
    pprint([answer, context_feedback, answer_feedback])
