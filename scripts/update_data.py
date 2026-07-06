#!/usr/bin/env python3
import json, os, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "live-data.json"
FOOTBALL_DATA_KEY=os.getenv("FOOTBALL_DATA_KEY","")
ODDS_API_KEY=os.getenv("ODDS_API_KEY","")
COMPETITION=os.getenv("COMPETITION","WC")
SEASON=os.getenv("SEASON","2026")
ODDS_SPORT=os.getenv("ODDS_SPORT","soccer_fifa_world_cup")
ODDS_REGION=os.getenv("ODDS_REGION","eu")
BASE_TEAMS={"Brazil":{"rating":91,"off":8.9,"def":8.5,"momentum":89},"Norway":{"rating":84,"off":8.6,"def":7.7,"momentum":86},"Argentina":{"rating":92,"off":9.0,"def":8.6,"momentum":92},"France":{"rating":93,"off":9.1,"def":8.8,"momentum":93},"England":{"rating":86,"off":8.3,"def":8.1,"momentum":83},"Egypt":{"rating":80,"off":7.5,"def":7.7,"momentum":79}}
def fetch_json(url, headers=None):
    req=urllib.request.Request(url,headers=headers or {})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode("utf-8"))
def norm(s): return "".join(ch.lower() if ch.isalnum() else " " for ch in str(s or "")).strip()
def same(a,b):
    a,b=norm(a),norm(b)
    return bool(a and b) and (a==b or a in b or b in a)
def football_data_matches():
    if not FOOTBALL_DATA_KEY: return []
    url=f"https://api.football-data.org/v4/competitions/{urllib.parse.quote(COMPETITION)}/matches?season={urllib.parse.quote(SEASON)}"
    raw=fetch_json(url,{"X-Auth-Token":FOOTBALL_DATA_KEY})
    games=[]
    for x in raw.get("matches",[]):
        home=x.get("homeTeam",{}).get("name") or x.get("homeTeam",{}).get("shortName")
        away=x.get("awayTeam",{}).get("name") or x.get("awayTeam",{}).get("shortName")
        if not home or not away: continue
        ft=x.get("score",{}).get("fullTime",{}); ht=x.get("score",{}).get("halfTime",{})
        games.append({"id":str(x.get("id") or f"{home}-{away}-{x.get('utcDate')}"),"date":x.get("utcDate"),"home":home,"away":away,"status":x.get("status","SCHEDULED"),"realFT":f"{ft.get('home')}-{ft.get('away')}" if ft.get("home") is not None and ft.get("away") is not None else None,"realHT":f"{ht.get('home')}-{ht.get('away')}" if ht.get("home") is not None and ht.get("away") is not None else None,"odds":{}})
    return games
def odds_api_events():
    if not ODDS_API_KEY: return []
    url=f"https://api.the-odds-api.com/v4/sports/{urllib.parse.quote(ODDS_SPORT)}/odds/?apiKey={urllib.parse.quote(ODDS_API_KEY)}&regions={urllib.parse.quote(ODDS_REGION)}&markets=h2h,totals&oddsFormat=decimal&dateFormat=iso"
    return fetch_json(url)
def map_odds(games, events):
    for ev in events:
        for g in games:
            if not ((same(g["home"],ev.get("home_team")) and same(g["away"],ev.get("away_team"))) or (same(g["home"],ev.get("away_team")) and same(g["away"],ev.get("home_team")))): continue
            odds={}
            for bm in ev.get("bookmakers",[]):
                for m in bm.get("markets",[]):
                    for o in m.get("outcomes",[]):
                        price=o.get("price")
                        if not price: continue
                        if m.get("key")=="h2h":
                            if same(o.get("name"),g["home"]): odds["home"]=max(odds.get("home",0),price)
                            elif same(o.get("name"),g["away"]): odds["away"]=max(odds.get("away",0),price)
                            elif o.get("name")=="Draw": odds["draw"]=max(odds.get("draw",0),price)
                        if m.get("key")=="totals" and float(o.get("point",0))==2.5:
                            if o.get("name")=="Over": odds["o25"]=max(odds.get("o25",0),price)
                            if o.get("name")=="Under": odds["u25"]=max(odds.get("u25",0),price)
            if odds: g["odds"]=odds
def main():
    games=football_data_matches()
    if not games and OUT.exists(): games=json.loads(OUT.read_text()).get("games",[])
    events=odds_api_events()
    if events: map_odds(games,events)
    print("Writing:", OUT)
    print("Source: GitHub Actions")
    print("Games:", len(games))
    OUT.write_text(json.dumps({"meta":{"source":"GitHub Actions","updated_at":datetime.now(timezone.utc).isoformat(),"competition":COMPETITION,"season":SEASON},"teams":BASE_TEAMS,"games":games},indent=2,ensure_ascii=False),encoding="utf-8")
    print(f"Wrote {OUT} with {len(games)} games.")
if __name__=="__main__": main()
