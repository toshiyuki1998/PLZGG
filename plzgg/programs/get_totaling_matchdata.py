import os
import time, datetime
import config
import connection_tools
from riotwatcher import LolWatcher, ApiError
import pandas as pd
import json


lol_watcher = LolWatcher(os.getenv('RIOT_TOKEN'))
region = "jp1"
large_region = "ASIA"
season_start = 1637625600
season_end = ""
queue = "RANKED_SOLO_5x5"
queue_id = 420


match_list = []
summonerName = "THBlade"

puuid = lol_watcher.summoner.by_name(region, summonerName)["puuid"]
match_list+=lol_watcher.match.matchlist_by_puuid(region=large_region, puuid=puuid, queue=queue_id, start_time=season_start)


connection = connection_tools.connect_db()
cur = connection.cursor()


championName = "Kaisa"
cur.execute("select match_id, match_timeline from match_data where champion_name4 = '"+championName+"';")


frames = pd.DataFrame()
for i, r in enumerate(cur):
    match_id = r[0]
    match_timeline = r[1]
    frame_num = len(match_timeline["info"]["frames"])
    frame_interval = match_timeline["info"]["frameInterval"]
    for n in range(frame_num):
        frame = pd.json_normalize(match_timeline["info"]["frames"][n]["participantFrames"]["4"], sep="_")
        frame["match_id"] = match_id
        frame["timestamp"] = match_timeline["info"]["frames"][n]["timestamp"]
        frame["time"] = frame_interval*n/1000
        frame["final"] = 0
        if n == frame_num-1:
            frame["final"] = 1
            frame["time"] = frame["timestamp"]/1000
        frames = frames.append(frame)
frames["time"] = frames["time"].astype("int")


frames[frames.final==0].groupby("time").mean()


