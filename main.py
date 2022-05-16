import requests, discord, re, time, threading, copy, zoomtools, datetime
from discord_components import DiscordComponents, Button, ButtonStyle
from config import *

client = discord.Client()

ITEMS = requests.get("https://ddragon.leagueoflegends.com/cdn/12.4.1/data/ru_RU/item.json").json()['data']
CHAMPIONS = dict(([champ['key'], {"name": champ['name'], "icon": "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/champion/%s" % champ['image']['full']}] for (_, champ) in requests.get("https://ddragon.leagueoflegends.com/cdn/12.4.1/data/ru_RU/champion.json").json()['data'].items()))

def request(url, json={}, headers={}):
    headers['X-Riot-Token'] = RIOT_TOKEN
    return requests.get(url=url, json=json, headers=headers).json()
      
def get_time(t):  return time.strftime("%M:%S", time.localtime(t))
    
def get_data():
    players = copy.deepcopy(USERS)
    for (name, data) in players.items():
        try:
            game = request("https://ru.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/%s" % data['id'])
            if 'status' in game:
                data['in_game'] = False
                continue
            data['in_game'] = True
            data['length'] = game['gameLength']
            data['mode'] = game['gameMode']
            data['type'] = game['gameType']
            data['game_id'] = game['gameId']
            data['icon'] = str(list(filter(lambda player: player['summonerId'] == data['id'], game['participants']))[0]['profileIconId'])
            data['champion'] = str(list(filter(lambda player: player['summonerId'] == data['id'], game['participants']))[0]['championId'])
        except Exception as err:
            print(err)
            data['in_game'] = False
    return players

last_games = {"games": [], "updated": 0}
def get_games(count=20, new=False, old=False):
    global last_games
    if time.time() - last_games["updated"] < 20 and not required_new or old: return copy.deepcopy(last_games["games"])
    games = []
    games_ids = []
    for (_, data) in USERS.items():
        try:
            puuid = request("https://ru.api.riotgames.com/lol/summoner/v4/summoners/%s" % data['id'])['puuid']
            games_ids += request("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/%s/ids?count=%s" % (puuid, count))
        except: pass
    for game_id in list(set(games_ids)): 
        try:
            game = request("https://europe.api.riotgames.com/lol/match/v5/matches/%s" % game_id)
            games.append(game['info'])
        except: pass
    last_games = {"games": games, "updated": time.time()}
    return copy.deepcopy(games)

def get_top(top_type, games_count=20, old=False, new=False):
    games = filter(lambda x: x['gameType'] == "MATCHED_GAME", get_games(count=games_count, old=old, new=new))
    top = copy.deepcopy(USERS)
    for game in games:
        for (name, user) in top.items():
            player = list(filter(lambda player: player['summonerId'] == user['id'], game['participants']))
            if not player: continue
            player = player[0]
            changed = False
            first = False
            kda = round((player['kills'] + player['assists']) / (player['deaths'] if player['deaths'] != 0 else 1), 1)
            param = kda if top_type == "kda" else player[top_type]
            if "top_param" not in user: first = True
            else:
                print(name)
                print(user['top_param'])
            if top_type in ["kda", "kills", "assists"]: 
                if zoomtools.smart_int(param) > zoomtools.smart_int(user.get("top_param")) or first:
                    user["top_param"] = param
                    user["top_param_visual"] = "%s / %s / %s ( %s KDA )" % (player["kills"], player['deaths'], player['assists'], kda)
                    changed = True
            else:
                if zoomtools.smart_int(param) > zoomtools.smart_int(user.get("top_param")) or first: 
                    user["top_param"] = param
                    user["top_param_visual"] = zoomtools.value_parse(param) + TOP_VISUAL[top_type]
                    changed = True
            if changed:
                user["gameId"] = game["gameId"]
                user["icon"] = "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/profileicon/%s.png" % player["profileIcon"]
                user["champion"] = player['championId']
                user["created"] = game["gameCreation"] / 1000
    print(top)
    return top

def get_gamedata(gameId):
    game = request("https://europe.api.riotgames.com/lol/match/v5/matches/RU_%s" % gameId)
    if 'status' in game: return False
    game['info']['id'] = gameId
    return game['info']

def listener():
    print("[AHEGAO] Listening")
    games = {}
    games_blacklist = {}
    while True:
        embeds = []
        for (name, info) in get_data().items():
            if name in games_blacklist and info['in_game']:
                if info['game_id'] in games_blacklist[name]: continue
            if name not in games and info['in_game']:
                if name in games_blacklist: games_blacklist[name].append(info['game_id'])
                else: games_blacklist[name] = [info['game_id']]
                games[name] = {"id": info['game_id'], "icon": "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/profileicon/%s.png" % info['icon'], "champion": info['champion']}
                embeds.append({"color": 15387920, "thumbnail": {"url": CHAMPIONS[info['champion']]['icon']}, "author": { "name": name, "icon_url": "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/profileicon/%s.png" % info['icon'] }, "description": f"*Вошёл в игру:* **{GAME_MODES[info['mode']]}**\n*Персонаж:* **{CHAMPIONS[info['champion']]['name']}**\n*ID Игры*: **{info['game_id']}**", "footer": { "text": GAME_TYPES[info['type']] }})
            if name in games and info['in_game']:
                if games[name]['id'] != info['game_id']: 
                    if name in games_blacklist: games_blacklist[name].append(info['game_id'])
                    else: games_blacklist[name] = [info['game_id']]
                    games[name] = {"id": info['game_id'], "icon": "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/profileicon/%s.png" % info['icon'], "champion": info['champion']}
                    embeds.append({"color": 15387920, "thumbnail": {"url": CHAMPIONS[info['champion']]['icon']}, "author": { "name": name, "icon_url": "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/profileicon/%s.png" % info['icon'] }, "description": f"*Вошёл в игру:* **{GAME_MODES[info['mode']]}**\n*Персонаж:* **{CHAMPIONS[info['champion']]['name']}**\n*ID Игры*: **{info['id']}**", "footer": { "text": GAME_TYPES[info['type']] }})
            if name in games: game = get_gamedata(games[name]['id'])
            else: game = False
            if game: 
                del games[name]
                player = list(filter(lambda player: player['summonerId'] == info['id'], game['participants']))
                if player: player = player[0]
                else: continue
                enemies = [f"**{CHAMPIONS[str(enemy['championId'])]['name']}** *({enemy['kills']} / {enemy['deaths']} / {enemy['assists']})*" for enemy in filter(lambda enemy: enemy["teamId"] != player["teamId"] and (enemy['individualPosition'] == player['individualPosition'] or ((enemy['individualPosition'] == "BOTTOM" and player["individualPosition"] == "UTILITY") or (enemy['individualPosition'] == "UTILITY" and player["individualPosition"] == "BOTTOM"))), game['participants'])]
                items = list(map(lambda id: f"**{ITEMS[str(id)]['name']}**" if zoomtools.smart_int(ITEMS[str(id)].get('depth')) >= 3 or ("Boots" in ITEMS[str(id)]['tags'] and zoomtools.smart_int(ITEMS[str(id)].get('depth')) >= 2) or id in ITEMS_EXCEPTIONS else ITEMS[str(id)]['name'], filter(lambda id: str(id) in ITEMS, [player['item%s' % i] for i in range(6)])))
                embeds.append({"color": 6363816, "url": "https://www.leagueofgraphs.com/ru/match/ru/%s" % game['gameId'], "thumbnail": {"url": CHAMPIONS[str(player['championId'])]['icon']}, "author": { "name": name, "icon_url": "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/profileicon/%s.png" % player['profileIcon'] }, "title": "ПОБЕДА" if player['win'] else "ПОРАЖЕНИЕ", "description": f"*Играл за:* **{CHAMPIONS[str(player['championId'])]['name']}** ( **{player['champLevel']} Уровень** )\n*Счёт:* **{player['kills']} / {player['deaths']} / {player['assists']}** (***{round(player['challenges']['kda'], 1)} KDA***)\n*Стоял против:* {', '.join(enemies)}\n*Урона нанесено:* **{zoomtools.value_parse(player['totalDamageDealtToChampions'])}**\n*Золота получено / потрачено:* **{zoomtools.value_parse(player['goldEarned'])} / {zoomtools.value_parse(player['goldSpent'])}**\n*Предметы:* {', '.join(items)}\n*Продолжительность игры:* **{get_time(game['gameDuration'])}**", "footer": {"text": "ID Игры: %s" % game['id']}})
        if embeds: requests.post("https://discordapp.com/api/v6/channels/%s/messages" % LOG_CHANNEL, json={"embeds": embeds}, headers={"Authorization": "Bot " + DISCORD_TOKEN})
        time.sleep(10)

@client.event
async def on_ready(): 
    DiscordComponents(client)
    print("Discord logined")
    
@client.event
async def on_message(message):
    if message.author == client.user: return
    if message.content.lower() == '!онлайн' or message.content.lower() == "!online":
        id = requests.post("https://discordapp.com/api/v6/channels/%s/messages" % message.channel.id, json={"embed": {"color": 5893820, "description": "ЗАГРУЗКА ИНФОРМАЦИИ..."}}, headers={"Authorization": "Bot " + DISCORD_TOKEN}).json()['id']
        embeds = []
        for (name, info) in get_data().items():
            #if not info['in_game']: embeds.append({"color": 13305350, "author": { "name": name }, "footer": {"text": "НЕ В ИГРЕ"} })
            if info['in_game']: embeds.append({"color": 6544914, "thumbnail": {"url": CHAMPIONS[info['champion']]['icon']}, "author": { "name": name, "icon_url": "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/profileicon/%s.png" % info['icon'] }, "description": f"**{GAME_MODES[info['mode']]}**\n*Играет за:* **{CHAMPIONS[info['champion']]['name']}**\n*Уже:* **{get_time(info['length'])}** *(~ {get_time(info['length'] + 60*4)})*\n*ID Игры:* **{info['game_id']}**", "footer": { "text": GAME_TYPES[info['type']] }})
        if not embeds: embeds.append({"color": 13305350, "description": "Люди в игре отсутствуют" })
        requests.patch("https://discordapp.com/api/v6/channels/%s/messages/%s" % (message.channel.id, id), json={"embeds": embeds, "content": "> ⚠ Информация о Лиге Легенд доходит c задержкой около 4 минут"}, headers={"Authorization": "Bot " + DISCORD_TOKEN})
    elif message.content.lower() == "!free":
        data = request("https://ru.api.riotgames.com/lol/platform/v3/champion-rotations")
        all_free = '- ' + ('\n- '.join([CHAMPIONS[str(id)]['name'] for id in data['freeChampionIds']]))
        new_free = '- ' + ('\n- '.join([CHAMPIONS[str(id)]['name'] for id in data['freeChampionIdsForNewPlayers']]))
        embeds = [{"color": 565282, "title": "Бесплатные персонажи, доступные для ВСЕХ на данный момент", "description": all_free}, {"color": 14958087, "title": "Бесплатные персонажи, доступные для НОВИЧКОВ на данный момент", "description": new_free}]
        requests.post("https://discordapp.com/api/v6/channels/%s/messages" % message.channel.id, json={"embeds": embeds}, headers={"Authorization": "Bot " + DISCORD_TOKEN})
    elif message.content.lower() in ["!top", "!топ"]:
        buttons = [Button(label = "По количеству убийств", style = 1, custom_id = "top_kills"), Button(label = "По количеству саппортов", style = 1, custom_id = "top_assists"), Button(label = "По значению KDA", style = 1, custom_id = "top_kda"), Button(label = "По полученному золоту", style = 1, custom_id = "top_goldEarned"), Button(label = "По нанесённому урону", style = 1, custom_id = "top_totalDamageDealtToChampions")]
        await message.channel.send("***Выберите подходящий критерий топа***", components = buttons)
        response = await client.wait_for('button_click')
        if response.component.custom_id.startswith("top_"):
            top_type = response.component.custom_id.split("top_")[1]
            await response.message.edit(embed=discord.Embed(color = 5893820, title=response.component.label, description = "СБОР ИГРОВОЙ ИНФОРМАЦИИ..."), components=[], content="***Пожалуйста, ожидайте.***")
            top = get_top(top_type)
            embeds = [{"color": 14958087, "thumbnail": {"url": CHAMPIONS[str(info['champion'])]['icon']}, "author": {"name": name, "icon_url": info['icon']}, "description": f"**{info['top_param_visual']}**", "timestamp": datetime.datetime.fromtimestamp(info['created']).isoformat(), "footer": {"text": "ID Игры: %s" % info['gameId']}, "title": "%s МЕСТО" % i, "url": "https://www.leagueofgraphs.com/ru/match/ru/%s" % info['gameId']} for i, (name, info) in enumerate(sorted(top.items(), key=lambda user: user[1]["top_param"], reverse=True), 1)][:5]
            if embeds: requests.patch("https://discordapp.com/api/v6/channels/%s/messages/%s" % (response.message.channel.id, response.message.id), json={"embeds": embeds, "content": "> Учитываются последние 20 игр каждого пользователя"}, headers={"Authorization": "Bot " + DISCORD_TOKEN})
            
threading.Thread(target=listener).start()
client.run(DISCORD_TOKEN)
