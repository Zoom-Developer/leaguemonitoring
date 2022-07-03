import sys, requests, json
from config import *

def request(url, json={}, headers={}):
    headers['X-Riot-Token'] = RIOT_TOKEN
    return requests.get(url=url, json=json, headers=headers).json()
    
in_json = False
    
users = sys.argv[1:]
if '--json' in users:
    users.remove("--json")
    in_json = True
    
result = {}
for user in users:
    summoner = request("https://ru.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + user)
    if summoner.get("status"): continue
    result[summoner['name']] = {"id": summoner['id']}
    
print("------------------------------ RESULT ------------------------------")
if in_json:
    print(json.dumps(result, indent=4))
else:
    for user, info in result.items():
        print("%s - %s" % (user, info['id']))
print("------------------------------ RESULT ------------------------------")