#%% Import libraries

import requests

# %% Mock SMS Phone
def sendSms(message):
    response = requests.post(
        f'https://150e-192-109-205-162.ngrok.io/sms?Body={message}'
    )
    print(f'Response: {response.text}')
# %% Main loop

if __name__=='__main__':
    while True:
        text = input("Text to send: ")
        sendSms(text)