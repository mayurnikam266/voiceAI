import requests
from memory_store import memory

def call_ai_engine(prompt, api_key, role, custom_role=""):
    if role == "friendly":
        system_prompt = "You are a friendly assistant."
    elif role == "english_tutor":
        system_prompt = "You are a helpful English tutor."
    elif role == "custom":
        system_prompt = custom_role 
    else:
        system_prompt = "You are a helpful assistant."

    messages = [{"role": "system", "content": system_prompt}] + [
        {"role": "user", "content": m["user"]} if "user" in m else {"role": "assistant", "content": m["assistant"]}
        for m in memory
    ] + [{"role": "user", "content": prompt}]

    headers = {"Authorization": f"Bearer {api_key}"}
    body = {"model": "openrouter/cypher-alpha:free", "messages": messages}

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        result = response.json()
        print("🔁 Raw OpenRouter response:", result)

        # Handle error response
        if "choices" not in result:
            raise ValueError(f"OpenRouter API Error: {result}")

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ AI Engine Error:", e)
        return "Sorry, an error occurred while getting a response from the AI engine."
