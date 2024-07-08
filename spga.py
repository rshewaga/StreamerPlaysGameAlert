import argparse
import requests
from timeit import default_timer as timer
from time import sleep
import pyttsx3

ttsEngine = pyttsx3.init()

parser = argparse.ArgumentParser(description="Periodically checks whether a given streamer is playing a given game. At the first sight that they are, an audio notification is played and the script exits.")
parser.add_argument("-streamerName", type=str, required=True, help="Public name of the streamer", default="Robbaz")
parser.add_argument("-gameName", type=str, required=True, help="Name of the game to watch for", default="Wreckfest")
parser.add_argument("-oauth", type=str, required=True, help="Your user request OAuth token")
parser.add_argument("-checkInterval", type=int, help="Number of minutes between each check", default=1)
parser.add_argument("-timeout", type=int, help="Number of minutes before exiting the script", default=30)

args = parser.parse_args()

# Get the broadcaster_id from the given streamer name
params:dict = {'login': args.streamerName}
headers:dict = {'Authorization': 'Bearer {0}'.format(args.oauth), 'Client-Id': '83mrwk5de48splmqpbylf43nya59fg'}
req:requests.Response = requests.get('https://api.twitch.tv/helix/users', params=params, headers=headers)
json:dict = req.json()

# Error check
if(json.get("data",-1) == -1):
    raise ValueError("Can't find streamer with that name!")
if(len(json["data"]) < 1):
    raise ValueError("Can't find streamer with that name!")
if(len(json["data"]) > 1):
    raise ValueError("Found multiple streamers with that name!")

broadcaster_id:int = req.json()["data"][0]["id"]
params:dict = {'broadcaster_id': broadcaster_id}

# Start a timer for the timeout to check against
start:float = timer()
while(timer() - start < (args.timeout * 60)):
    # Check what game the streamer is playing
    req = requests.get('https://api.twitch.tv/helix/channels', params=params, headers=headers)
    json = req.json()

    # Error check
    if(json.get("data",-1) == -1):
        raise ValueError("Can't find streamer with that name!")
    for idx in range(len(json["data"])):
        if(json["data"][idx]["broadcaster_id"] != broadcaster_id):
            continue
        if(json["data"][idx]["game_name"] == args.gameName):
            success:str = "{0} is now playing {1}!".format(json["data"][idx]["broadcaster_name"], json["data"][idx]["game_name"])
            print(success)
            ttsEngine.say(success)
            ttsEngine.say(success)
            ttsEngine.say("Goodbye :)")
            ttsEngine.runAndWait()
            exit(0)

        print("\"{0}\" is currently playing \"{1}\". Checking for \"{2}\" again in {3} minute(s)...".format(json["data"][idx]["broadcaster_name"], json["data"][idx]["game_name"], args.gameName, args.checkInterval))

    sleep(args.checkInterval * 60)

print("Timed out after {0} minute(s)".format(args.timeout))
exit(0)