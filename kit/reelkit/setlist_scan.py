import json, os, sys, time, urllib.request, urllib.parse, collections
KEY = sys.argv[1]; ARTISTS = sys.argv[2].split("|")
D = os.environ.get("SETLIST_CACHE", "/tmp/setlist-cache")
os.makedirs(D, exist_ok=True)
def get(path):
    fn = os.path.join(D, urllib.parse.quote(path, safe="") + ".json")
    if os.path.exists(fn): return json.load(open(fn))
    for i in range(5):
        time.sleep(0.6)
        req = urllib.request.Request("https://api.setlist.fm/rest/1.0" + path, headers={"x-api-key": KEY, "Accept": "application/json"})
        try:
            data = json.load(urllib.request.urlopen(req, timeout=30)); break
        except urllib.error.HTTPError as e:
            if e.code == 404: data = {}; break
            if e.code == 429: time.sleep(3); continue
            raise
    json.dump(data, open(fn, "w")); return data
for name in ARTISTS:
    a = get("/search/artists?" + urllib.parse.urlencode({"artistName": name, "sort": "relevance"}))["artist"][0]
    shows, p = [], 1
    while True:
        r = get(f"/artist/{a['mbid']}/setlists?p={p}")
        sl = r.get("setlist", [])
        shows += sl
        if not sl or p * r["itemsPerPage"] >= r["total"]: break
        p += 1
    per_year = collections.Counter(); plays = collections.defaultdict(collections.Counter); last = {}
    for s in shows:
        songs = [x["name"].strip() for st in s.get("sets", {}).get("set", []) for x in st.get("song", []) if x.get("name") and not x.get("tape")]
        if len(songs) < 5: continue
        y = int(s["eventDate"][-4:]); per_year[y] += 1
        for t in set(songs):
            plays[t][y] += 1
            d = s["eventDate"]; k = (d[-4:], d[3:5], d[:2])
            if t not in last or k > last[t][0]: last[t] = (k, s["venue"]["name"], s["venue"]["city"]["name"], s.get("url"))
    years = sorted(y for y in per_year if per_year[y] >= 15)
    out = []
    for t, c in plays.items():
        rate = {y: c[y] / per_year[y] for y in years}
        staple = [y for y in years if rate[y] >= 0.6]
        if len(staple) < 2: continue
        after = [y for y in years if y > max(staple)]
        dead = [y for y in after if rate[y] <= 0.05]
        if len(dead) >= 3 and len(dead) >= len(after) - 1:
            out.append((sum(c.values()), t, f"staple {min(staple)}-{max(staple)}", f"dead {len(dead)}/{len(after)} later yrs", "last " + "-".join(last[t][0]), last[t][1], last[t][2]))
    print(f"\n## {a['name']}  shows={len(shows)} years={years[0] if years else '-'}..{years[-1] if years else '-'}")
    for o in sorted(out, reverse=True)[:6]: print("  ", *o)
