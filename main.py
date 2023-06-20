import os
from constants import openai_key, max_file_size, max_chunk_size
import requests
import openai
import streamlit as st
from com_justify import Justification
from com_gpt_process import gpt_process
from com_repositories import RetrieveRepositories

openai.api_key = openai_key

st.title("Repository Complexity Analysis")
url = st.text_input("Enter Git URL")


def getRepos(url, max_file_size, max_chunk_size):
    most_complex_repo = None
    highest_complexity = float('-inf')
    justification = ""
    username = url.split("/")
    username = username[-1]
    response = requests.get(f"https://api.github.com/users/{username}/repos")
    if response.status_code == 200:
        repos = response.json()
        repo_names = [r["name"] for r in repos]

        # repo_names = [r["name"] for r in repositories]

        for r in repo_names:
            print(f"Processing repository {r}")
            response = requests.get(f"https://api.github.com/repos/{username}/{r}/contents")
            if response.status_code == 200:
                contents = response.json()
                for file in contents:
                    file_name = file["name"]
                    file_url = file["download_url"]
                    file_size = file["size"]

                    if file_size <= max_file_size:
                        try:
                            response = requests.get(file_url)
                        except Exception as e:
                            print("Could not read file due to " + str(e))
                        if response.status_code == 200:
                            file_content = response.text

                            # Chunk the file content if it exceeds the maximum chunk size
                            if len(file_content) > max_chunk_size:
                                chunks = chunk_large_files(file_content, max_chunk_size)

                                for chunk in chunks:
                                    tech_complexity = evaluate_complexity(chunk)

                                    print("Chunk technical complexity {tech_complexity}")
                                    if tech_complexity > highest_complexity:
                                        highest_complexity = tech_complexity
                                        most_complex_repo = r
                                        justification = justification.generate_justification(chunk)
                            else:
                                tech_complexity = evaluate_complexity(file_content)
                                print(f"File Technical Complexity {tech_complexity}")
                                if tech_complexity > highest_complexity:
                                    highest_complexity = tech_complexity
                                    most_complex_repo = r
                                    justification = justification.generate_justification(file_content)
                        else:
                            print(f"failed to fetch content for {file_name}")
                    else:
                        print(f"skipping large file {file_name}")
            else:
                print(f"Failed to fetch contents for repository: {r}")

    else:
        print("unable to fetch user's repository")
    return highest_complexity, most_complex_repo, justification


'''def generate_justification(code_chunk):
    # Implement your code to generate a justification for selecting the code chunk
    # (e.g., pass the code chunk through GPT and analyze the response)
    # You can use prompt engineering techniques to craft the input prompt to GPT
    prompt = f"Justify the selection of this code chunk as the most complex:\n\n{code_chunk}"
    # Use the prompt to invoke GPT and obtain the justification
    just = gpt_process(prompt)
    return just
'''


def chunk_large_files(content, max_chunk_size):
    chunks = []
    start = 0
    while start < len(content):
        end = start + max_chunk_size
        if end >= len(content):
            chunk = content[start:]
        else:
            # Find a line break or token boundary to end the chunk
            chunk = content[start:end]
            last_line_break = chunk.rfind("\n")
            last_token_boundary = chunk.rfind(" ")

            if last_line_break > 0:
                end = start + last_line_break + 1
            elif last_token_boundary > 0:
                end = start + last_token_boundary + 1
            chunk = content[start:end]
        chunks.append(chunk)
        start = end
    return chunks


'''def evaluate_complexity(code_chunk):
    prompt = f"Evaluate the technical complexity of this code:\n\n{code_chunk} amongst the following levels only without any explanation: very low, low, moderate, high, very high and maximum"
    response = openai.Completion.create(
        engine='text-davinci-003',  # Choose the appropriate GPT model
        prompt=prompt,
        max_tokens=100,  # Adjust as needed based on token limits
        temperature=0.5,  # Adjust temperature for diversity of responses
        n=1,  # Number of completions to generate
        stop=None,  # Optional stopping condition
        timeout=15,  # Optional timeout for response
    )
    # complexity = gpt_process(prompt)
    completion = response.choices[0].text.strip().lower()
    print(f"Completion: {completion}")  # Added line for debugging
    complexity_score = convert_to_complexity_score(completion)
    return complexity_score
'''


def convert_to_complexity_score(completion):
    complexity_mapping = {
        'very low': 0.10,
        'very less': 0.10,
        'less': 0.30,
        'low': 0.30,
        'moderate': 0.50,
        'medium': 0.50,
        'average': 0.50,
        'high': 0.70,
        'very high': 0.90,
        'maximum': 1.00
    }
    for level, score in complexity_mapping.items():
        if level.lower() in completion:
            return score
    raise ValueError("Failed to convert completion to complexity score")


def gpt_process(prompt):
    model = "text-davinci-003"
    max_tokens = 100  # Adjust the value based on your needs

    # Generate a response from the GPT-3 model
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=1.0,
        n=1,  # adjust as per the requirement
        stop=None,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        best_of=1
    )

    # Retrieve the generated text from the response
    generated_text = response.choices[0].text.strip()

    return generated_text


if url:
    highest_complexity, most_complex_repo, justification = RetrieveRepositories.getRepos(url, max_file_size,
                                                                                         max_chunk_size)
    st.write("Most complex repo: " + most_complex_repo)
    st.write("Justification: " + justification)
