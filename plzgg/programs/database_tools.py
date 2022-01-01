import os
import time, datetime
from . import config
from . import connection_tools
from riotwatcher import LolWatcher, ApiError
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.offline import plot


def save_metchdata(riot_token, region, large_region, season_start, season_end, queue, queue_id):
    lol_watcher = LolWatcher(riot_token)

    connection = connection_tools.connect_db()
    cur = connection.cursor()

    match_list = []
    #Challenger
    summoners = lol_watcher.league.challenger_by_queue(region, queue)["entries"]
    for summoner in summoners:
        summonerName = summoner["summonerName"]
        try:
            puuid = lol_watcher.summoner.by_name(region, summonerName)["puuid"]
            match_list+=lol_watcher.match.matchlist_by_puuid(region=large_region, puuid=puuid, queue=queue_id, start_time=season_start)
        except:
            continue
        time.sleep(2)

    #Grandmaster
    summoners = lol_watcher.league.grandmaster_by_queue(region, queue)["entries"]
    for summoner in summoners:
        summonerName = summoner["summonerName"]
        try:
            puuid = lol_watcher.summoner.by_name(region, summonerName)["puuid"]
            match_list+=lol_watcher.match.matchlist_by_puuid(region=large_region, puuid=puuid, queue=queue_id, start_time=season_start)
        except:
            continue
        time.sleep(2)

    #Master
    summoners = lol_watcher.league.masters_by_queue(region, queue)["entries"]
    for summoner in summoners:
        summonerName = summoner["summonerName"]
        try:
            puuid = lol_watcher.summoner.by_name(region, summonerName)["puuid"]
            match_list+=lol_watcher.match.matchlist_by_puuid(region=large_region, puuid=puuid, queue=queue_id, start_time=season_start)
        except:
            continue
        time.sleep(2)

    match_list = set(match_list)


    match_list_old = []
    cur.execute("select match_id from match_data")
    for c in cur:
        match_list_old.append(c[0])

    for match_id in match_list:
        if match_id not in match_list_old:
            match_info = lol_watcher.match.by_id(region=large_region, match_id=match_id)
            time.sleep(2)
            match_ready = match_info["info"]["teams"]
            match_result = pd.DataFrame(match_info["info"]["participants"])
            match_timeline = lol_watcher.match.timeline_by_match(region=large_region, match_id=match_id)
            time.sleep(2)
            match_date = match_info["info"]["gameCreation"]
            match_champions = ""
            for champion in match_result["championName"]:
                match_champions += "'" + champion + "', "
            match_champions = match_champions[:-2]
            match_version = match_info["info"]["gameVersion"]
            cur.execute("insert into match_data values ('%s', %s, '%s', '%s', '%s', '%s', '%s', %s);" % (match_id, match_date, match_version, large_region, region, json.dumps(match_info), json.dumps(match_timeline), match_champions))
        connection.commit()



def get_matchdata(riot_token, region, large_region, season_start, season_end, queue, queue_id, champion_name,champion_position):
    connection = connection_tools.connect_db()
    cur = connection.cursor() 
    cur.execute("select match_id, match_timeline from match_data where champion_name"+str(champion_position)+" = '"+champion_name+"';")

    return cur



def get_summoner_champion_matchlist(riot_token, region, large_region, season_start, season_end, queue, queue_id, summoner_name, champion_name,champion_position):
    lol_watcher = LolWatcher(riot_token)
    match_list = []
    puuid = lol_watcher.summoner.by_name(region, summoner_name)["puuid"]
    match_list+=lol_watcher.match.matchlist_by_puuid(region=large_region, puuid=puuid, queue=queue_id, start_time=season_start)

    match_list_new = []
    for match_id in match_list:
        match_info = lol_watcher.match.by_id(region=large_region, match_id=match_id)
        participants = match_info["info"]["participants"]
        for n, participant in enumerate(participants):
            if (participant["summonerName"]==summoner_name)&(participant["championName"]==champion_name)&(int(champion_position)==n+1):
                match_list_new.append(match_id)
    match_timelines = []
    for match_id in match_list_new:
        match_timeline = lol_watcher.match.timeline_by_match(region=large_region, match_id=match_id)
        match_timelines.append([match_id, match_timeline])
        time.sleep(2)

    return match_timelines



def make_matchdata(matchdata, champion_position):#match_timelineを纏める
    frames = pd.DataFrame()
    for i, data in enumerate(matchdata):
        match_id = data[0]
        match_timeline = data[1]

        frame_num = len(match_timeline["info"]["frames"])
        frame_interval = match_timeline["info"]["frameInterval"]
        for n in range(frame_num):
            frame = pd.json_normalize(match_timeline["info"]["frames"][n]["participantFrames"][str(champion_position)], sep="_")
            frame["match_id"] = match_id
            frame["timestamp"] = match_timeline["info"]["frames"][n]["timestamp"]
            frame["time"] = frame_interval*n/1000
            frame["final"] = 0
            if n == frame_num-1:
                frame["final"] = 1
                frame["time"] = frame["timestamp"]/1000
            frames = frames.append(frame)
    
    frames["time"] = frames["time"].astype("int")
    return frames

def get_data(summoner_name, champion_name,champion_position):
    riot_token = os.getenv('RIOT_TOKEN')
    region = "jp1"
    large_region = "ASIA"
    season_start = 1637625600
    season_end = ""
    queue = "RANKED_SOLO_5x5"
    queue_id = 420

    matchdata = get_matchdata(riot_token, region, large_region, season_start, season_end, queue, queue_id, champion_name,champion_position)
    data1 = make_matchdata(matchdata, champion_position)
    matchdata = get_summoner_champion_matchlist(riot_token, region, large_region, season_start, season_end, queue, queue_id, summoner_name, champion_name,champion_position)
    data2 = make_matchdata(matchdata, champion_position)

    fig = line_charts(data1, data2)
    return fig


def line_charts(data1, data2):
    d1 = data1[data1.final==0].groupby("time").mean()
    d2 = data2[data2.final==0].groupby("time").mean()
    fig = go.Figure([
        go.Scatter(x=d1.index/60, y=d1["damageStats_totalDamageDoneToChampions"], opacity=.5),
        go.Scatter(x=d2.index/60, y=d2["damageStats_totalDamageDoneToChampions"], opacity=.5)
    ])

    return fig.to_html(include_plotlyjs=False)
    