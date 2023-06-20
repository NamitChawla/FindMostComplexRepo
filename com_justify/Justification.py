from com_gpt_process import gpt_process


def generate_justification(code_chunk):
    # Implement your code to generate a justification for selecting the code chunk
    # (e.g., pass the code chunk through GPT and analyze the response)
    # You can use prompt engineering techniques to craft the input prompt to GPT
    prompt = f"Justify the selection of this code chunk as the most complex:\n\n{code_chunk}"
    # Use the prompt to invoke GPT and obtain the justification

    just = gpt_process.gpt_process(prompt)
    return just
