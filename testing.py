import requests


def send_message(SERVER_URL):
    url = f"{SERVER_URL}/chat"
    conversation_id = input("Enter the conversation ID: ")

    while True:
        message = input("Enter a question (or 'exit' to change conversation ID): ")
        if message.lower() == "exit":
            conversation_id = input("Enter a new conversation ID: ")
            continue

        payload = {
            "conversation_id": conversation_id,
            "message": message
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    print(line + '\n')
            else:
                print(f"Request failed with status code {response.status_code}")
                print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")


if __name__ == "__main__":
    send_message("http://localhost:8000")
