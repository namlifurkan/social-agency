import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "kit", "reelkit"))
from vo import generate

BEATS = [
    ("hook", "This song is called Nicole Kidman. | And Nicole Kidman just lip-synced it."),
    ("who", "It's by Adéla, a singer from Slovakia."),
    ("globes", "She wrote it after a Golden Globes party. | That night, she felt like Nicole Kidman."),
    ("fallon", "In September, Jimmy Fallon asks Kidman about it."),
    ("chanel", "Then, at Chanel's show in Paris, she lip-syncs it. | Dua Lipa and Pedro Pascal join in."),
    ("now", "This week, it's number two on Spotify worldwide."),
    ("card", "So, is it a hit?"),
]

generate(BEATS, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vo"))
