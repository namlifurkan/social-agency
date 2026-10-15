import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "kit", "reelkit"))
from vo import generate

BEATS = [
    ("hook", "Olivia Rodrigo's number one hit was missing two writers."),
    ("y2021", "May 2021. good 4 u goes straight to number one. | Then TikTok hears something."),
    ("y2007", "Rewind to 2007. Paramore, Misery Business. | Hayley Williams is eighteen."),
    ("ab", "Now play them back to back."),
    ("credits", "Three months later, the credits changed. Hayley Williams and Josh Farro were added as writers."),
    ("first", "Fourteen years after they wrote it, it was their first number one as songwriters."),
    ("twist", "And it wasn't the only one. On the same album, deja vu added Taylor Swift, Jack Antonoff and St. Vincent, because of Cruel Summer."),
    ("card", "So, which one hits harder?"),
]

generate(BEATS, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vo"))
