import base64, json, os, sys, urllib.error, urllib.request

from vo import key, tts

USAGE = """python3 voice.py check
python3 voice.py list
python3 voice.py design "<voice description>" "<100-1000 char sample text>" <out_dir>
python3 voice.py save <generated_voice_id> "<name>" "<voice description>"
python3 voice.py test <voice_id> "<text>" <out.mp3>"""


def call(path, body=None):
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=json.dumps(body).encode() if body else None,
                                 headers={"xi-api-key": key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs {e.code}: {e.read().decode()[:300]}")


def write(b64, path):
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(path)


def main(cmd, *a):
    if cmd == "check":
        print(f"key ok, {len(call('/v1/voices')['voices'])} voices on the account")
    elif cmd == "list":
        for v in call("/v1/voices")["voices"]:
            print(f"{v['voice_id']}  {v['category']:12s} {v['name']}")
    elif cmd == "design":
        desc, text, out = a
        os.makedirs(out, exist_ok=True)
        for i, p in enumerate(call("/v1/text-to-voice/design", {"voice_description": desc, "text": text})["previews"], 1):
            print(p["generated_voice_id"], end="  ")
            write(p["audio_base_64"], os.path.join(out, f"preview-{i}.mp3"))
    elif cmd == "save":
        gid, name, desc = a
        print(call("/v1/text-to-voice", {"voice_name": name, "voice_description": desc, "generated_voice_id": gid})["voice_id"])
    elif cmd == "test":
        vid, text, out = a
        write(tts(text, vid)["audio_base64"], out)
    else:
        sys.exit(USAGE)


if __name__ == "__main__":
    main(*sys.argv[1:]) if len(sys.argv) > 1 else sys.exit(USAGE)
