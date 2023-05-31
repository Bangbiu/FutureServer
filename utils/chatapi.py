import openai

openai.api_key = "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"
max_token = 2000

debug_mode = True
## History Format
# [{"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}]

def chat(history) -> str:
    if debug_mode: return "Debug"
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history,
    )
    return completion.choices[0].message.content

def request(prompt: str, model: str) -> str:
    if debug_mode: return "Debug"
    # Invoke API
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}])
    return completion.choices[0].message.content
