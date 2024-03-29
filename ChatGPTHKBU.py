import requests
import os
from dotenv import load_dotenv
load_dotenv()

class ChatGPTHKBU:
    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = (os.getenv(
            'CHATGPT_BASICURL')) + "/deployments/gpt-35-turbo/chat/completions/?api-version=2024-02-15-preview"
        headers = {'Content-Type': 'application/json',
                   'api-key': (os.getenv('CHATGPT_ACCESS_TOKEN'))}
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response


if __name__ == '__main__':
    ChatGPT_test = ChatGPTHKBU()
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)
