import re
import os
from llm import call_llm, llm_checklength


def gen_py_info(path: os.PathLike, file_name: str, contents: str) -> str:
    """
    Generate a summary of the Python file using an LLM.

    Args:
        file_name (str): The name of the Python file.
        contents (str): The contents of the Python file.

    Returns:
        str: The summary of the Python file.
    """

    prompt = create_prompt_file(file_name, contents)

    fits_in_one_request = llm_checklength(prompt)
    if fits_in_one_request:
        summary = call_llm(prompt)
    else:
        # # Handle very long sections if needed
        # raise NotImplementedError(f"Very long section, not implemented yet: {path}")

        # dumb solution
        r1 = gen_py_info(path, file_name, contents[: len(contents) // 2])
        r2 = gen_py_info(path, file_name, contents[len(contents) // 2 :])

        prompt = f"Combine the following two partial summaries into one:\n\nSummary 1:\n{r1}\n\nSummary 2:\n{r2}\n\nCombined Summary:"
        summary = call_llm(prompt)

    return summary


def create_prompt_file(file_name, contents):
    """
    Create a prompt for generating a summary of a Python file.

    Args:
        file_name (str): The name of the Python file.
        contents (str): The contents of the Python file.

    Returns:
        str: The generated prompt for the LLM.
    """
    return (
        f"Analyze the entire Python file '{file_name}' and provide a summary, including the purpose, architecture, "
        f"classes, functions, and any important details or patterns. Consider the overall structure and "
        f"organization of the code to provide a comprehensive understanding of the file.\n\n"
        f"--- Code ---\n{contents}\n--- End of Code ---\n\n"
        f"Summary:"
    )


def method_by_sections(file_name, contents):
    """
    Does the job of gen_py_info using sections of code with lines of context

    Args:
        file_name (str): The name of the Python file.
        contents (str): The contents of the Python file.

    Returns:
        str: The summary of the Python file.
    """

    sections, main_sections = split_code_sections(file_name, contents)
    section_summaries = []

    for section, main_section in zip(sections, main_sections):
        main_section_start = section.find(main_section)
        main_section_end = main_section_start + len(main_section)
        prompt = create_prompt_sections(
            file_name, section, main_section_start, main_section_end
        )

        fits_in_one_request = llm_checklength(prompt)
        if fits_in_one_request:
            summary = call_llm(prompt)
            section_summaries.append(summary)
        else:
            # Handle very long sections if needed
            raise NotImplementedError

    # Combine the section summaries into a single summary
    # TODO: Make this more intelligent
    combined_summary = "\n".join(section_summaries)
    return combined_summary


def split_code_sections(file_name, contents, max_context_lines=2):
    """
    Split the contents of a Python file into sections, including surrounding context.

    Args:
        file_name (str): The name of the Python file.
        contents (str): The contents of the Python file.
        max_context_lines (int): Maximum number of context lines to include around each main section.

    Returns:
        tuple: A tuple containing two lists: sections with context and main sections.
    """
    lines = contents.splitlines()
    line_count = len(lines)

    # Find section boundaries (classes and functions)
    section_boundaries = [
        i for i, line in enumerate(lines) if re.match(r"(class .*:|def .*:)", line)
    ]

    # Add the start and end of the file to the section boundaries
    section_boundaries = [0] + section_boundaries + [line_count]

    # Create sections with surrounding context
    sections = []
    main_sections = []
    for i in range(len(section_boundaries) - 1):
        start = section_boundaries[i]
        end = section_boundaries[i + 1]

        # Calculate the number of context lines that fit within the token limit
        main_section = "\n".join(lines[start:end])
        context_lines = max_context_lines
        while context_lines > 0:
            extended_start = max(start - context_lines, 0)
            extended_end = min(end + context_lines, line_count)
            extended_section = "\n".join(lines[extended_start:extended_end])

            if llm_checklength(
                create_prompt_sections(
                    file_name,
                    extended_section,
                    context_lines,
                    len(extended_section) - context_lines,
                )
            ):
                break
            else:
                context_lines -= 1

        # Include the allowed number of context lines
        start = max(start - context_lines, 0)
        end = min(end + context_lines, line_count)
        section = "\n".join(lines[start:end])
        sections.append(section.strip())
        main_sections.append(main_section.strip())

    return sections, main_sections


# def create_prompt_sections(file_name, section):
#     return f"Analyze the following section of the Python file '{file_name}' and provide a summary including the purpose, architecture, classes, functions, and any important details or patterns.\n\n--- Code ---\n{section}\n--- End of Code ---\n\nSummary:"

# def create_prompt_sections(file_name, section):
#     return f"Analyze the following section of the Python file '{file_name}' and provide a summary, focusing on the main section while considering the surrounding context for better understanding.\n\n--- Code ---\n{section}\n--- End of Code ---\n\nSummary:"


def create_prompt_sections(file_name, section, main_section_start, main_section_end):
    """
    Create an LLM prompt for a section of a Python file.

    Args:
        file_name (str): The name of the Python file.
        section (str): The section of the Python file to analyze.
        main_section_start (int): The start index of the main section within the section string.
        main_section_end (int): The end index of the main section within the section string.

    Returns:
        str: The LLM prompt.
    """
    # return f"Analyze the following section of the Python file '{file_name}' and provide a summary, focusing on the main section while considering the surrounding context for better understanding.\n\n--- Code ---\n{section[:main_section_start]}[MAIN_SECTION_START]{section[main_section_start:main_section_end]}[MAIN_SECTION_END]{section[main_section_end:]}\n--- End of Code ---\n\nSummary:"
    return (
        f"Analyze the following section of the Python file '{file_name}' and provide a summary, "
        f"focusing on the main section while considering the surrounding context for better understanding.\n\n"
        f"--- Code ---\n"
        f"{section[:main_section_start]}\n"
        f"[MAIN_SECTION_START]\n"
        f"{section[main_section_start:main_section_end]}\n"
        f"[MAIN_SECTION_END]\n"
        f"{section[main_section_end:]}\n"
        f"--- End of Code ---\n\n"
        f"Summary:"
    )
