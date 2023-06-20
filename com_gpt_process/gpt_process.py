import openai


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
