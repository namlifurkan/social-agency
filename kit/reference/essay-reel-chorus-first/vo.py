import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "kit", "reelkit"))
from vo import generate

BEATS = [
    ("hook", "Why do so many songs now start right on the hook?"),
    ("billie", "In 1983, Billie Jean makes you wait. | Twenty-nine seconds before Michael sings."),
    ("jelly", "Quincy Jones wanted that intro cut. | Michael said no. That's the jelly."),
    ("unholy", "Now play a hit from 2022."),
    ("unholy2", "Unholy. The hook lands in the first second."),
    ("study", "A 2018 study timed thirty years of top ten hits. | Intros fell from over twenty seconds to about five."),
    ("skip", "On Spotify, a play only counts after thirty seconds. | And one song in four is skipped in the first five."),
    ("charli", "Charli XCX's rule: chorus in the first thirty seconds. | No self-indulgent intro."),
    ("roxette", "The rule is older than streaming. | In 1995, Roxette named an album after it."),
    ("flip", "Then this February, Harry Styles went to number one | with forty-five seconds before his first word."),
    ("card", "So, would you wait forty-five seconds?"),
]

generate(BEATS, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vo"))
