from ollama import chat, ChatResponse, Options
from collections import defaultdict


def send_request_to_llm(input_prompt, system_prompt, temp=0, model="llama3.1:8b"):
    response = chat(
        # llama3.1:8b
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_prompt},
        ],
        options=Options(temperature=temp),
    )
    return response["message"]["content"]
