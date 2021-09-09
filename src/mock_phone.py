#%% Import libraries

import requests

# %% Mock SMS Phone
def sendSms(message):
    response = requests.post(
        f'https://b720-136-144-33-25.ngrok.io/sms?Body={message}'
    )
    print(f'Response: {response.text}')
# %% Main loop

if __name__=='__main__':
    while True:
        text = input("Text to send: ")
        sendSms(text)