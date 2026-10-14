import os
import subprocess

from PIL import Image

from layout import W, H


def fetch(url, out):
    if os.path.exists(out):
        return out
    for client in ("web_embedded", "mweb"):
        r = subprocess.run(["yt-dlp", "-q", "--no-warnings", "--no-playlist", "--extractor-args",
                            f"youtube:player_client={client}", "-f", "bv*[height<=1080]+ba/b",
                            "--merge-output-format", "mp4", "-o", out, url])
        if r.returncode == 0:
            return out
    raise RuntimeError(f"yt-dlp failed for {url}")


class Clip:
    def __init__(self, path, start=0.0, dur=None, focus_x=0.5, speed=1.0, gray=True, w=W, h=H, fps=30,
                 zoom=1.0, focus_y=0.5):
        self.w, self.h, self.fps = w, h, fps
        a, b = focus_x if isinstance(focus_x, tuple) else (focus_x, focus_x)
        pan = f"({a}+({b}-{a})*min(t/{dur}\\,1))" if dur and a != b else str(a)
        vf = [f"fps={fps / speed}", f"scale={round(w * zoom)}:{round(h * zoom)}:force_original_aspect_ratio=increase",
              f"crop={w}:{h}:(iw-{w})*{pan}:(ih-{h})*{focus_y}"]
        if gray:
            vf += ["hue=s=0", "eq=contrast=1.15"]
        self.cmd = ["ffmpeg", "-loglevel", "error", "-ss", str(start), *(["-t", str(dur)] if dur else []),
                    "-i", path, "-vf", ",".join(vf), "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.proc, self.i, self.last = None, -1, None

    def _open(self):
        if self.proc:
            self.proc.kill()
        self.proc, self.i = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL), -1

    def frame(self, t):
        i = max(0, int(t * self.fps))
        if self.proc is None or i < self.i:
            self._open()
        size = self.w * self.h * 3
        while self.i < i:
            buf = self.proc.stdout.read(size)
            if len(buf) < size:
                break
            self.last, self.i = buf, self.i + 1
        if self.last is None:
            raise ValueError(f"no frames decoded: {' '.join(self.cmd)}")
        return Image.frombytes("RGB", (self.w, self.h), self.last)
