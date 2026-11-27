"""VO script for the Rohit 'Mumbai cha Raja' reel: one block per scene (rohit_render.SCENES order). python3 rohit_vo.py lint|gen"""
import os, sys, json, base64, urllib.request, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_lint as V
VO = [
 "He is back. मुंबईचा राजा, रोहित शर्मा, is captain of the Mumbai Indians once more.",
 "Listen to वानखेड़े. The chant has followed him for fifteen years.",
 "Nineteen seasons. Seven thousand, three hundred and twenty-nine IPL runs in our archive. Yellow for Deccan, blue for Mumbai, every bar a season.",
 "It began at Deccan Chargers, with a title in two thousand nine. In two thousand eleven he came home to Mumbai, and from then on, he never left.",
 "Two thousand thirteen. Ricky Ponting steps aside, Rohit takes over, and in his first season as captain, Mumbai are champions.",
 "Six IPL titles. One with Deccan, five with Mumbai. Only अंबाती रायुडू has as many.",
 "As captain, five finals. Five titles. He never lost a final.",
 "Under Rohit, Mumbai won eighty-two and lost sixty-six, and made the playoffs in six of ten seasons. Since twenty twenty-four, seventeen wins, twenty-seven defeats.",
 "Seven thousand, three hundred and twenty-nine runs. Three hundred and twenty-four sixes. Six titles.",
 "Every season, on one card. Four hundred and four in his first year. Four eighty-nine in twenty sixteen. Two eighty-three in twenty twenty-six.",
 "Joint-most titles. The first Indian past three hundred IPL sixes, in our archive. And at thirty-eight, the oldest world number one ODI batter.",
 "Welcome back, captain. मुंबईचा राजा, रोहित शर्मा.",
]
VO = [V.fix_text(t) for t in VO]
if __name__ == "__main__":
    bad = [(i + 1, V.problems(t)) for i, t in enumerate(VO) if V.problems(t)]; print("problems:", bad); print("words", sum(len(t.split()) for t in VO), "chars", sum(len(t) for t in VO))
    if sys.argv[1:] == ["gen"] and not bad:
        d0 = "out/rohit_vo"; os.makedirs(d0, exist_ok=True); VOICE = "siw1N9V8LmYeEWKyWBxv"; meta = []
        for i, t in enumerate(VO):
            f = f"{d0}/s{i}.mp3"
            if not os.path.exists(f):
                body = {"text": t, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": .45, "similarity_boost": .8, "style": .3, "use_speaker_boost": True}, "previous_text": VO[i - 1] if i else None, "next_text": VO[i + 1] if i + 1 < len(VO) else None}
                req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128", data=json.dumps(body).encode(), headers={"xi-api-key": os.environ["XI_KEY"], "Content-Type": "application/json"})
                d = json.load(urllib.request.urlopen(req, timeout=180)); open(f, "wb").write(base64.b64decode(d["audio_base64"])); json.dump(d["alignment"], open(f"{d0}/s{i}.json", "w"))
            print("scene", i + 1, flush=True)
