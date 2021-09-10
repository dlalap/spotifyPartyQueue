#%% Import libraries

import requests

# %% Mock SMS Phone
def sendSms(message):
    response = requests.post(
        f'http://0.0.0.0:1812/sms?Body={message}'
    )
    print(f'Response: {response.text}')
# %% Main loop

if __name__=='__main__':
    while True:
        text = input("Text to send: ")
        sendSms(text)