import json, os, sys, subprocess, urllib.request

KEY = os.environ["XI_KEY"]
VOICE = os.environ.get("XI_VOICE", "siw1N9V8LmYeEWKyWBxv")  # Ruhaan
OUT = os.path.join(os.path.dirname(__file__), "vo")
os.makedirs(OUT, exist_ok=True)

PARAS = [
    "He scored one hundred international centuries. Thirty-four thousand runs. But in a career spanning twenty-four years, सचिन तेंदुलकर played exactly one T20 international.",
    "Johannesburg, December, two thousand six. India's first-ever T20 match. सचिन made ten off twelve balls, picked up a wicket, and India won. He never played the format for India again.",
    "He did get a taste in the IPL. Six seasons with मुंबई. Two thousand three hundred runs. And in twenty ten, at thirty-six years old, he won the Orange Cap with six hundred and eighteen runs.",
    "But here's the problem. His IPL strike rate was just under one-twenty. And the game has changed. In two thousand eight, top-order batters struck at one-thirty. By twenty twenty-five, that number had jumped past one-fifty-eight. The powerplay went from seven runs an over to more than nine.",
    "So would सचिन have survived? Look closer. In one-day cricket, he struck at eighty-six, far quicker than most of his era. शारजाह. Nineteen ninety-eight. He took apart Australia in a desert storm. In two thousand three, he upper-cut शोएब अख़्तर over third man for six. A shot that today is a T20 staple. He invented it before the format existed.",
    "Now give him flat pitches, bigger bats, and an Impact Player batting behind him. Scale his IPL numbers to today's game, and his strike rate climbs to around one-forty-six. That's an opener who wins you the powerplay without giving away his wicket.",
    "The verdict? Modern T20 सचिन isn't a slogger. He's the anchor who scores at a run a ball, and then explodes. And with a technique like that, he might just be the most complete T20 batter we never got to see.",
    "Would सचिन have dominated the T20 era? Tell us in the comments.",
]

durs = []
for i, p in enumerate(PARAS):
    body = {"text": p, "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True},
            "previous_text": PARAS[i - 1] if i else None,
            "next_text": PARAS[i + 1] if i + 1 < len(PARAS) else None}
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_192",
        data=json.dumps(body).encode(), headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        open(f"{OUT}/p{i}.mp3", "wb").write(r.read())
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{OUT}/p{i}.mp3"]))
    durs.append(d)
    print(i, round(d, 2), flush=True)
json.dump(durs, open(f"{OUT}/para_durs.json", "w"))
