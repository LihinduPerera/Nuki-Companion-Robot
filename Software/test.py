import requests

def query_ollama(prompt, model='llama3.2', base_url='http://localhost:11434'):
    endpoint = f'{base_url}/api/generate'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'model': model,
        'prompt': prompt,
        'stream': False
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['response']
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# Example usage
if __name__ == "__main__":
    prompt_text = "Explain the theory of relativity in simple terms."
    try:
        output = query_ollama(prompt_text)
        print("LLaMA 3.2 Response:\n", output)
    except Exception as e:
        print("Error:", e)