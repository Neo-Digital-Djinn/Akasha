import json
import os

INPUT_DIR = "data/characters"
OUTPUT_DIR = "character_cards"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_card(character):
    return {
        "id": character.get("id", ""),
        "alias": character.get("alias", ""),

        "real_world": {
            "name": character.get("real_name_optional", ""),
            "summary": character.get("baseline_behavior", ""),
            "traits": [
                character.get("core_trait", "")
            ] + character.get("quirks_and_ticks", [])
        },

        "character_version": {
            "title": character.get("archetype", ""),
            "tagline": character.get("core_trait", ""),
            "core_trait": character.get("core_trait", ""),
            "power_summary": character.get("power_expression", ""),
            "abilities": character.get("abilities", []),
            "limitations": character.get("limitations", []),
            "catchphrase": character.get("catchphrase", "")
        },

        "visuals": {
            "real_reference_image": f"reference_images/{character.get('id', '')}.jpg",
            "character_art_image": f"character_cards/{character.get('id', '')}.png",
            "environment": character.get("environment", {}).get("primary_location", "")
        }
    }

def process():
    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".json"):
            continue

        input_path = os.path.join(INPUT_DIR, filename)

        with open(input_path, "r") as f:
            character = json.load(f)

        card = build_card(character)

        output_filename = filename.replace(".json", ".card.json")
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, "w") as f:
            json.dump(card, f, indent=2)

        print(f"Generated: {output_path}")

if __name__ == "__main__":
    process()