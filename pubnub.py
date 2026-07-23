import requests
import queue
import Threading

## Transmit Player Movements
def publish(channel, message):
    pass

## Receive the game state
def subscribe(channel, inbox):
    origin = ''
    timetoken = '1000'
    subkey = 'demo'
    uri=f"https://${origin}/subscribe/${subkey}/${channel}/0/${timetoken}";
    response = requests.get(uri)
    pass
    
