import requests
import threading
from queue import Queue

## Transmit Player Movements
def publish(channel, message):
    origin = 'h2.pubnubapi.com'
    pubkey = 'demo'
    subkey = 'demo'
    payload = json.dumps(message)
    uri = f'/publish/{pubkey}/{subkey}/0/{channel}/0/{payload}'

    response = requests.get(uri)
    return response.json()[0]

## Receive the game state
def subscribe(channel, inbox):
    while True:
        origin = 'h2.pubnubapi.com'
        timetoken = '1000'
        subkey = 'demo'
        uri=f"https://{origin}/subscribe/{subkey}/{channel}/0/{timetoken}";
        response = requests.get(uri)
        data = response.json()
        timetoken = data[1]
        messages = data[0]

        for message in messages:
            inbox.put(message)

def publisher(inbox, outbox):
    while True:
        message = inbox.get()
        print(message)

if __name__ == '__main__':
    game_state_channel = 't-rex-dino-game-state'
    game_move_channel = 't-rex-dino-game-movement'

    ## Subscription Inbox
    inbox = Queue()
    subscription = threading.Thread(target=subscribe, args=(inbox,))

    ## Publish Game Movement
    outbox = Queue()
    publishing = threading.Thread(target=publisher, args=(inbox, outbox,))

    subscription.join()
    publishing.join()

