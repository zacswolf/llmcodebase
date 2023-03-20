from datetime import datetime
import openai
import os
import dotenv
import json
import tiktoken

dotenv.load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

cache_file_name = "open_ai_cache.json"


def call_llm(prompt):
    # Check cache
    if os.path.exists(cache_file_name):
        with open(cache_file_name, "r") as json_file:
            response_cache = json.load(json_file)
    else:
        response_cache = {}

    if prompt in response_cache:
        return response_cache[prompt][0]

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    assert (
        response and response.choices and response.choices[0].text
    ), f"Failed to generate response from OpenAI API {response}"

    response_str = response.choices[0].text.strip()

    # Update cache
    response_cache[prompt] = [
        response_str,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ]
    with open(cache_file_name, "w") as outfile:
        json.dump(response_cache, outfile)

    return response_str


def llm_checklength(prompt):
    """
    Check if the given prompt is within the token limit.

    Args:
        prompt (str): The text prompt.
        max_tokens (int): The maximum allowed token count.

    Returns:
        bool: True if the prompt is within the token limit, False otherwise.
    """
    max_tokens = 2048  # Maximum number of tokens for Text-Davinci-003 model

    enc = tiktoken.encoding_for_model("text-davinci-003")
    num_tokens = len(enc.encode(prompt))
    return num_tokens < max_tokens
