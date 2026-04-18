# scraper/test_lm.py
import requests

response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "local-model",
        "messages": [{"role": "user", "content": "Say hello in one sentence."}],
        "max_tokens": 50
    }
)

print(response.json()["choices"][0]["message"]["content"])