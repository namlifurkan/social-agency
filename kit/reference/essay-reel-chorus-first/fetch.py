import json, os, subprocess, sys, urllib.parse, urllib.request

D = os.path.dirname(os.path.abspath(__file__))
UA = "RiffiterSocial/1.0 (furkannamli@gmail.com)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def commons(q, n):
    qs = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                                 "gsrsearch": f"{q} filetype:bitmap", "gsrlimit": n, "prop": "imageinfo",
                                 "iiprop": "url|size", "iiurlwidth": 1400})
    pages = json.loads(get(f"https://commons.wikimedia.org/w/api.php?{qs}")).get("query", {}).get("pages", {})
    out = []
    for p in sorted(pages.values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        if ii["width"] >= 900:
            out.append((ii.get("thumburl") or ii["url"], p["title"]))
    return out


def openverse(q, n):
    qs = urllib.parse.urlencode({"q": q, "page_size": n})
    return [(r["url"], r.get("title") or "") for r in json.loads(get(f"https://api.openverse.org/v1/images/?{qs}"))["results"]
            if r.get("width", 0) >= 900]


def main():
    src, slug, q = sys.argv[1], sys.argv[2], sys.argv[3]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    os.makedirs(f"{D}/cand", exist_ok=True)
    hits = (commons if src == "c" else openverse)(q, n)
    files = []
    for i, (url, title) in enumerate(hits):
        path = f"{D}/cand/{slug}-{i}.jpg"
        try:
            open(path, "wb").write(get(url))
            files.append(path)
            print(f"{slug}-{i}\t{title}")
        except Exception as e:
            print(f"skip {url}: {e}")
    if files:
        subprocess.run(["magick", *files, "-resize", "x300", "-background", "black", "-splice", "6x0", "+append",
                        f"{D}/cand/sheet-{slug}.jpg"], check=True)


main()
