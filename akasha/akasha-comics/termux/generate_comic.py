#!/usr/bin/env python3
import os, json
from datetime import datetime

def load_env():
    env = {}
    with open(".env") as f:
        for line in f:
            if "=" in line:
                k,v = line.strip().split("=",1)
                env[k] = v
    return env

ENV = load_env()

DATA_CHAR = ENV["AKASHA_DATA"]
CARD_CHAR = ENV["AKASHA_CARDS"]
PROMPT_DIR = ENV["AKASHA_PROMPTS"]
STORE_FILE = ENV["AKASHA_STORE"]
INPUT_FILE = ENV["AKASHA_INPUT"]
OUTPUT_DIR = ENV["AKASHA_OUTPUT"]

def load_json(p):
    with open(p) as f: return json.load(f)

def load_characters():
    chars = {}
    if os.path.exists(DATA_CHAR):
        for f in os.listdir(DATA_CHAR):
            data = load_json(os.path.join(DATA_CHAR,f))
            chars[data["name"].lower()] = data
    if os.path.exists(CARD_CHAR):
        for f in os.listdir(CARD_CHAR):
            if f.endswith(".json"):
                data = load_json(os.path.join(CARD_CHAR,f))
                name = data.get("name", f.replace(".json","")).lower()
                chars[name] = data
    return chars

def load_prompts():
    p = {}
    if os.path.exists(PROMPT_DIR):
        for f in os.listdir(PROMPT_DIR):
            name = f.replace(".txt","").lower()
            with open(os.path.join(PROMPT_DIR,f)) as pf:
                p[name] = pf.read().strip()
    return p

def read_input():
    with open(INPUT_FILE) as f: return f.read().lower()

def detect_characters(text, chars):
    return [chars[n] for n in chars if n in text]

def build_panels(text, chars, store):
    names = [c.get("name","Unknown") for c in chars]
    s = ", ".join(names) if names else "workers"
    mood = "tense" if any(x in text for x in ["rough","busy","slam"]) else "normal"
    return [
        f"{s} starting shift at {store['store_name']} (mood: {mood})",
        "Rush hits, pressure rising",
        "Peak chaos at grill",
        "Resolution, small win moment"
    ]

def main():
    chars = load_characters()
    prompts = load_prompts()
    store = load_json(STORE_FILE)
    text = read_input()
    found = detect_characters(text, chars)
    panels = build_panels(text, found, store)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    out = f"{OUTPUT_DIR}/comic_{date}.txt"

    with open(out,"w") as f:
        for i,p in enumerate(panels,1):
            f.write(f"Panel {i}: {p}\n\n")
        f.write("\n--- IMAGE PROMPTS ---\n")
        for c in found:
            n = c.get("name","").lower()
            if n in prompts:
                f.write(f"\n[{n.upper()}]\n{prompts[n]}\n")

    print("[OK]", out)

if __name__ == "__main__":
    main()
