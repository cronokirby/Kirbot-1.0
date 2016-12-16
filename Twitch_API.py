"""
This module interacts with Twitch's API to fetch info about streams.
"""
# used to calculate the elapsed time of a stream
from datetime import datetime
import aiohttp
# these 2 are for parsing the config file
import os
import json
# this changes the directory to the directory of the script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
with open('config.json') as fp:
    Client_ID = json.load(fp)['twitchclientid']
# the header used for requests
headers = {'content-type': 'application/json',
           'Client-ID': Client_ID}


# Check if a stream exists, returns 'Live', 'Offline', 'False': doesn't exist.
async def findstream(name):
    try:
        url = "https://api.twitch.tv/kraken/streams/{}".format(name)
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, headers=headers) as r:
                Data = await r.json()
        # This will fail if the stream does not exist.
        if Data['stream']:
            return 'Live'
        # Data['stream'] is None when the streamer is offline
        else:
            return 'Offline'
    except:
        return False


# used to fetch a single stream
async def fetchstreaminfo(name):
    # try will fail if the url is bad, which means the name is incorrect
    try:
        url = "https://api.twitch.tv/kraken/streams/{}".format(name)
        StreamLink = "http://twitch.tv/{}".format(name)
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url, headers=headers) as r:
                Data = await r.json()
        if Data["stream"] is None:
            # Online will be used to check the online status of a stream
            Info = {
                'online': False,
                'URL': StreamLink}
        else:
            # Time in UTC, because creation_datetime is in UTC
            Current_Time = datetime.utcnow()
            creation_datetime = Data["stream"]["created_at"]
            creation_datetime = datetime.strptime(creation_datetime,
                                                  '%Y-%m-%dT%H:%M:%SZ')
            # This returns a datetime.timedelta() object
            ElapsedTime = Current_Time - creation_datetime
            Hours, Remainder = divmod(ElapsedTime.total_seconds(), 3600)
            Minutes = divmod(Remainder, 60)
            Seconds = Minutes[1]
            Uptime = {
                'Hours': int(Hours),
                'Minutes': int(Minutes[0]),
                'Seconds': int(Seconds)}

            Info = {
                'uptime': Uptime,
                'online': True,
                'URL': StreamLink,
                'game': Data["stream"]["game"],
                'viewers': Data["stream"]["viewers"],
                'preview': Data["stream"]["preview"]["medium"],
                'display_name': Data["stream"]["channel"]["display_name"],
                'status': Data["stream"]["channel"]["status"],
                'logo' : Data["stream"]["channel"]["logo"]}

        return Info
    except:
        # I could use False instead, but this is clearer later
        return "bad name"


# used to fetch multiple streams at once
async def fetchstreaminfolist(name_list):
    url = 'https://api.twitch.tv/kraken/streams?limit=100&channel='
    url += ','.join(name_list)
    async with aiohttp.ClientSession() as client:
        async with client.get(url=url, headers=headers) as r:
            Data = await r.json()
    # This will be used to calculate stream uptime
    Current_Time = datetime.utcnow()
    streams = []
    for stream_info in Data['streams']:
        creation_datetime = stream_info["created_at"]
        creation_datetime = datetime.strptime(creation_datetime,
                                              '%Y-%m-%dT%H:%M:%SZ')
        # This returns a datetime.timedelta() object
        ElapsedTime = Current_Time - creation_datetime
        Hours, Remainder = divmod(ElapsedTime.total_seconds(), 3600)
        Minutes = divmod(Remainder, 60)
        Seconds = Minutes[1]
        Uptime = {
            'Hours': int(Hours),
            'Minutes': int(Minutes[0]),
            'Seconds': int(Seconds)}

        Info = {
            'uptime': Uptime,
            'URL': stream_info['channel']["url"],
            'game': stream_info["game"],
            'viewers': stream_info["viewers"],
            'preview': stream_info["preview"]["medium"],
            'display_name': stream_info["channel"]["display_name"],
            'twitch_name': stream_info["channel"]["name"],
            'status': stream_info["channel"]["status"],
            'logo' : stream_info["channel"]["logo"]}

        streams.append(Info)
    return streams


# returns the twitchname if it exists, false otherwise
async def findgame(gamename):
    gamename = gamename.replace(" ", "+")
    url = "https://api.twitch.tv/kraken/search/games?q={}&type=suggest".format(
        gamename)
    async with aiohttp.ClientSession() as client:
        async with client.get(url=url, headers=headers) as r:
            Data = await r.json()
    print(Data)
    games = Data['games']
    if len(games) == 0:
        return False
    else:
        return Data['games'][0]['name']
