"""Pronunciation rules for narration ("vo"), enforced at build time and fixable in place.
    python3 voice_lint.py [--fix] [specs/x.json ...]     # check (or fix) specs; no args = all specs
Rules (agreed with the channel owner):
  1. Every subcontinent player name - first and last - and Indian place names are written in Devanagari.
  2. "U19" / "U-19" / "U 19" is read as "Under nineteen" (the screen may still show U19).
  3. No digits in narration: years and numbers are spelled out in words."""
import json, re, sys, glob

# Latin -> Devanagari (longest first when applied). Add new names here AND their parts to engine.SHOW (done automatically below).
NAMES = {
    "Virat Kohli": "विराट कोहली", "Kohli": "कोहली", "Virat": "विराट", "Rohit Sharma": "रोहित शर्मा", "Rohit": "रोहित",
    "Abhishek Sharma": "अभिषेक शर्मा", "Abhishek": "अभिषेक", "Jasprit Bumrah": "जसप्रीत बुमराह", "Jasprit": "जसप्रीत", "Bumrah": "बुमराह",
    "Sachin Tendulkar": "सचिन तेंदुलकर", "Sachin": "सचिन", "Tendulkar": "तेंदुलकर", "MS Dhoni": "एम एस धोनी", "Dhoni": "धोनी",
    "Rishabh Pant": "ऋषभ पंत", "Rishabh": "ऋषभ", "Pant": "पंत", "Shubman Gill": "शुभमन गिल", "Shubman": "शुभमन", "Gill": "गिल",
    "Sai Sudharsan": "साई सुदर्शन", "Sudharsan": "सुदर्शन", "Ishan Kishan": "इशान किशन", "Ishan": "इशान", "Kishan": "किशन",
    "KL Rahul": "के एल राहुल", "Rahul Tripathi": "राहुल त्रिपाठी", "Tripathi": "त्रिपाठी", "Rahul Dravid": "राहुल द्रविड़", "Dravid": "द्रविड़",
    "Sanju Samson": "संजू सैमसन", "Sanju": "संजू", "Samson": "सैमसन", "Vaibhav Sooryavanshi": "वैभव सूर्यवंशी", "Vaibhav Suryavanshi": "वैभव सूर्यवंशी",
    "Sooryavanshi": "सूर्यवंशी", "Suryavanshi": "सूर्यवंशी", "Vaibhav": "वैभव", "Bhuvneshwar Kumar": "भुवनेश्वर कुमार", "Bhuvneshwar": "भुवनेश्वर",
    "Mohsin Khan": "मोहसिन ख़ान", "Mohsin": "मोहसिन", "Rashid Khan": "राशिद ख़ान", "Rashid": "राशिद", "Yash Dayal": "यश दयाल", "Dayal": "दयाल",
    "Anshul Kamboj": "अंशुल कंबोज", "Kamboj": "कंबोज", "Tilak Varma": "तिलक वर्मा", "Tilak": "तिलक", "Shreyas Iyer": "श्रेयस अय्यर",
    "Shreyas": "श्रेयस", "Iyer": "अय्यर", "Hardik Pandya": "हार्दिक पंड्या", "Hardik": "हार्दिक", "Krunal Pandya": "क्रुणाल पंड्या", "Krunal": "क्रुणाल",
    "Pandya": "पंड्या", "Arshdeep Singh": "अर्शदीप सिंह", "Arshdeep": "अर्शदीप", "Umran Malik": "उमरान मलिक", "Umran": "उमरान",
    "Shoaib Akhtar": "शोएब अख़्तर", "Shoaib": "शोएब", "Babar Azam": "बाबर आज़म", "Babar": "बाबर", "Joginder Sharma": "जोगिंदर शर्मा", "Joginder": "जोगिंदर",
    "Gurnoor Brar": "गुरनूर बराड़", "Gurnoor": "गुरनूर", "Brar": "बराड़", "Aaryavir Sehwag": "आर्यवीर सहवाग", "Aaryavir": "आर्यवीर",
    "Virender Sehwag": "वीरेंद्र सहवाग", "Virender": "वीरेंद्र", "Sehwag": "सहवाग", "Ravindra Jadeja": "रवींद्र जडेजा", "Jadeja": "जडेजा",
    "Kuldeep Yadav": "कुलदीप यादव", "Kuldeep": "कुलदीप", "Mohammed Shami": "मोहम्मद शमी", "Shami": "शमी", "Mohammed Siraj": "मोहम्मद सिराज", "Siraj": "सिराज",
    "Axar Patel": "अक्षर पटेल", "Axar": "अक्षर", "Varun Chakaravarthy": "वरुण चक्रवर्ती", "Varun": "वरुण", "Chakaravarthy": "चक्रवर्ती",
    "Yashasvi Jaiswal": "यशस्वी जायसवाल", "Yashasvi": "यशस्वी", "Jaiswal": "जायसवाल", "Suryakumar Yadav": "सूर्यकुमार यादव", "Suryakumar": "सूर्यकुमार",
    "Prithvi Shaw": "पृथ्वी शॉ", "Prithvi": "पृथ्वी", "Lakshya Raichandani": "लक्ष्य रायचंदानी", "Anvay Dravid": "अन्वय द्रविड़", "Anvay": "अन्वय",
    "Ravichandran Ashwin": "रविचंद्रन अश्विन", "Ashwin": "अश्विन", "Yuzvendra Chahal": "युज़वेंद्र चहल", "Chahal": "चहल", "Prasidh Krishna": "प्रसिद्ध कृष्णा",
    "Avesh Khan": "आवेश ख़ान", "Avesh": "आवेश", "Mayank Agarwal": "मयंक अग्रवाल", "Mayank": "मयंक", "Prabhsimran Singh": "प्रभसिमरन सिंह",
    "Mohammad Rizwan": "मोहम्मद रिज़वान", "Rizwan": "रिज़वान", "Shaheen Shah Afridi": "शाहीन शाह अफ़रीदी", "Shaheen": "शाहीन",
    "Gautam Gambhir": "गौतम गंभीर", "Gambhir": "गंभीर", "Ajinkya Rahane": "अजिंक्य रहाणे", "Rahane": "रहाणे", "Ajaz Patel": "एजाज़ पटेल",
    "Rachin Ravindra": "रचिन रवींद्र", "Rachin": "रचिन", "Ish Sodhi": "ईश सोढ़ी", "Sodhi": "सोढ़ी", "Nitish Rana": "नितीश राणा", "Rahul": "राहुल",
    # places
    "Hyderabad": "हैदराबाद", "Gujarat": "गुजरात", "Mumbai": "मुंबई", "Delhi": "दिल्ली", "Chennai": "चेन्नई", "Bengaluru": "बेंगलुरु",
    "Bangalore": "बेंगलुरु", "Ranchi": "रांची", "Rajkot": "राजकोट", "Kolkata": "कोलकाता", "Lucknow": "लखनऊ", "Ahmedabad": "अहमदाबाद",
    "Punjab": "पंजाब", "Rajasthan": "राजस्थान", "Mohali": "मोहाली", "Wankhede": "वानखेड़े", "Jaipur": "जयपुर", "Shillong": "शिलॉन्ग",
    "Meghalaya": "मेघालय", "Chandigarh": "चंडीगढ़", "Cooch Behar": "कूच बिहार", "Vinoo Mankad": "विनू मांकड़", "Muscat": "मस्कट",
}
U19 = re.compile(r"\bU[\s-]?(19|nineteen)\b", re.I)
DIGIT = re.compile(r"\d")
KEYS = sorted(NAMES, key=len, reverse=True)
PAT = re.compile(r"(?<![A-Za-zऀ-ॿ])(" + "|".join(re.escape(k) for k in KEYS) + r")(?![A-Za-z])")


T20 = re.compile(r"\bT20(I|Is)?\b")


def fix_text(s):
    s = U19.sub("Under nineteen", s)
    s = T20.sub(lambda m: "T-twenty international" + ("s" if m.group(1) == "Is" else "") if m.group(1) else "T-twenty", s)
    return PAT.sub(lambda m: NAMES[m.group(1)], s)


def problems(s):
    out = []
    if U19.search(s): out.append("U19 (say 'Under nineteen')")
    for m in PAT.finditer(s): out.append(f"Latin name/place '{m.group(1)}' (use {NAMES[m.group(1)]})")
    if DIGIT.search(s): out.append("digits (spell numbers out)")
    return out


def walk(o, fn, key=None):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "vo" and isinstance(v, str): o[k] = fn(v)
            else: walk(v, fn, k)
    elif isinstance(o, list):
        for v in o: walk(v, fn)


def fix_spec(spec):
    walk(spec, fix_text); return spec


def check_spec(spec, fmts=("long", "short")):
    errs = []
    for f in fmts:
        for i, p in enumerate(spec.get(f, []) or []):
            for e in problems(p.get("vo", "")): errs.append(f"{f} p{i}: {e}")
    return errs


def show_map():
    """Devanagari word -> English word, for captions/SRT."""
    m = {}
    for k, v in NAMES.items():
        for lw, dw in zip(k.split(), v.split()):
            m.setdefault(dw, lw)
    m["ख़ान"] = "Khan"; m["एम"] = "M"; m["एस"] = "S"; m["के"] = "K"; m["एल"] = "L"
    return m


if __name__ == "__main__":
    fix = "--fix" in sys.argv
    files = [a for a in sys.argv[1:] if a.endswith(".json")] or sorted(glob.glob("specs/*.json"))
    bad = 0
    for f in files:
        sp = json.load(open(f))
        if fix:
            before = json.dumps(sp, ensure_ascii=False); fix_spec(sp)
            if json.dumps(sp, ensure_ascii=False) != before: json.dump(sp, open(f, "w"), ensure_ascii=False, indent=1); print("fixed", f)
        errs = check_spec(sp)
        if errs: bad += 1; print(f"{f}:"); [print("   ", e) for e in errs]
    sys.exit(1 if bad and not fix else 0)
