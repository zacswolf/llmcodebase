import os

from llm import call_llm, llm_checklength


def gen_folder_info(path, children_info: dict[str, str]) -> str:
    # TODO: Implement folder info generation
    prompt = create_prompt_list(path, children_info)

    fits_in_one_request = llm_checklength(prompt)
    if fits_in_one_request:
        # summary = call_llm(prompt)
        summary = None
    else:
        # Handle very long sections if needed
        # print(f"Very long section, not implemented yet: {path}")
        # # raise NotImplementedError
        # ci1 = dict(list(children_info.items())[len(children_info) // 2 :])
        # ci2 = dict(list(children_info.items())[: len(children_info) // 2])
        # p1 = create_prompt_list(path, ci1)
        # p2 = create_prompt_list(path, ci2)
        # s1 = call_llm(p1)
        # s2 = call_llm(p2)

        # prompt = f"Combine the following two partial summaries into one:\n\nSummary 1:\n{s1}\n\nSummary 2:\n{s2}\n\nCombined Summary:"
        # summary = call_llm(prompt)
        summary = None

    return summary


def create_prompt_list(path, children_info: dict[str, str]) -> str:
    folder_name = os.path.basename(path)

    summaries_list = ""
    for file_name, info in children_info.items():
        summary = None if info is None else info.summary
        summaries_list += f"- {file_name}: {summary}\n"

    prompt = (
        f"The folder '{path}' contains the following files and their summaries:\n{summaries_list}\n"
        "Provide a importance weighted, high level, summary of the folder's contents considering the information provided above."
    )

    return prompt


def create_prompt_list_base(path, children_info: dict[str, str]) -> str:
    folder_name = os.path.basename(path)
    list_of_files = ", ".join(children_info.keys())

    summaries_list = ""
    for file_name, summary in children_info.items():
        summaries_list += f"- {file_name}: {summary}\n"

    prompt = (
        f"The following files are present in the folder '{path}': {list_of_files}. "
        f"Here are the summaries of each file:\n{summaries_list}\n"
        "Provide a brief summary of the folder's contents considering the information provided above."
    )

    return prompt
