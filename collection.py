
import json
from pathlib import Path

from sprites import (
    ALL_SPRITES,
    SPRITE_DATABASE_VERSION,
    get_variant,
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SUPPORTED_SEASON = "C7S5"

SAVE_FORMAT_VERSION = 3
SUPPORTED_SAVE_VERSIONS = [3]

DATA_FILE = Path(__file__).resolve().parent / "data" / "collection.json"

STATUSES = ["Unmastered", "Mastered", "Level 5"]


# --------------------------------------------------
# COLLECTION DATA
# --------------------------------------------------

collection = {
    "owned": []
}


# --------------------------------------------------
# SAVE VALIDATION
# --------------------------------------------------

def validate_save_data(data):
    """Validate the structure of a v3 collection save."""

    if not isinstance(data, dict):
        return False

    if data.get("save_format_version") != SAVE_FORMAT_VERSION:
        return False

    if data.get("sprite_database_version") != SPRITE_DATABASE_VERSION:
        return False

    if data.get("season") != SUPPORTED_SEASON:
        return False

    owned = data.get("owned")

    if not isinstance(owned, list):
        return False

    seen = set()

    for entry in owned:

        if not isinstance(entry, dict):
            return False

        number = entry.get("number")

        if not isinstance(number, int) or isinstance(number, bool):
            return False

        variant = get_variant(number)

        if variant is None:
            return False

        if entry.get("name") != variant.sprite.name:
            return False

        if entry.get("variant") != variant.name:
            return False

        if entry.get("status") not in STATUSES:
            return False

        if number in seen:
            return False

        seen.add(number)

        for attribute in ("first_edition", "won_match"):

            if not isinstance(entry.get(attribute), bool):
                return False

    return True


# --------------------------------------------------
# SAVE COMPATIBILITY
# --------------------------------------------------

def check_compatibility(data):
    """Check whether a save belongs to the supported season and format."""

    if not isinstance(data, dict):
        return False

    if data.get("season") != SUPPORTED_SEASON:
        return False

    if data.get("save_format_version") not in SUPPORTED_SAVE_VERSIONS:
        return False

    return True


# --------------------------------------------------
# LOAD COLLECTION
# --------------------------------------------------

def load_collection():
    """Load the collection from disk."""

    if not DATA_FILE.exists():
        collection["owned"].clear()
        return False

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        print(f"Error loading collection: {error}")
        return False

    if not validate_save_data(data):
        print("Error: Collection save is invalid or incompatible.")
        return False

    collection["owned"].clear()
    collection["owned"].extend(data["owned"])

    return True


# --------------------------------------------------
# SAVE COLLECTION
# --------------------------------------------------

def save_collection():
    """Save the current collection to disk."""

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "save_format_version": SAVE_FORMAT_VERSION,
        "sprite_database_version": SPRITE_DATABASE_VERSION,
        "season": SUPPORTED_SEASON,
        "owned": collection["owned"],
    }

    if not validate_save_data(data):
        print("Error: Collection data failed validation.")
        return False

    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        return True

    except OSError as error:
        print(f"Error saving collection: {error}")
        return False


# --------------------------------------------------
# FIND OWNED SPRITE
# --------------------------------------------------

def find_owned(variant):
    """Find a collection entry using its permanent numeric ID."""

    if variant is None:
        return None

    for entry in collection["owned"]:

        if entry["number"] == variant.number:
            return entry

    return None


# --------------------------------------------------
# CHECK OWNERSHIP
# --------------------------------------------------

def is_owned(variant):
    """Check whether a variant exists in the collection."""

    return find_owned(variant) is not None


# --------------------------------------------------
# ADD SPRITE
# --------------------------------------------------

def add_sprite(
    variant,
    status="Unmastered",
    first_edition=False,
    won_match=False,
):
    """Add a Sprite variant to the collection."""

    if variant is None:
        print("Invalid Sprite variant.")
        return False

    if is_owned(variant):
        print("That Sprite variant is already in your collection.")
        return False

    if status not in STATUSES:
        print("Invalid mastery status.")
        return False

    if not isinstance(first_edition, bool):
        print("First Edition must be True or False.")
        return False

    if not isinstance(won_match, bool):
        print("Won Match must be True or False.")
        return False

    entry = {
        "number": variant.number,
        "name": variant.sprite.name,
        "variant": variant.name,
        "status": status,
        "first_edition": first_edition,
        "won_match": won_match,
    }

    collection["owned"].append(entry)

    if not save_collection():
        collection["owned"].remove(entry)
        print("Sprite was not added because saving failed.")
        return False

    print(
        f"Added {variant.sprite.name} "
        f"({variant.name}) to your collection."
    )

    return True


# --------------------------------------------------
# UPDATE MASTERY
# --------------------------------------------------

def update_status(variant, new_status):
    """Update the mastery status of an owned Sprite."""

    entry = find_owned(variant)

    if entry is None:
        print("Sprite variant is not in your collection.")
        return False

    if new_status not in STATUSES:
        print("Invalid mastery status.")
        return False

    current_status = entry["status"]

    # Mastery cannot be reversed.
    if current_status in ("Mastered", "Level 5"):
        if new_status == "Unmastered":
            print("A mastered Sprite cannot become Unmastered.")
            return False

    old_status = entry["status"]
    entry["status"] = new_status

    if not save_collection():
        entry["status"] = old_status
        return False

    print(
        f"{entry['name']} ({entry['variant']}) "
        f"status updated to {new_status}."
    )

    return True


# --------------------------------------------------
# RECORD TRADE OR LOSS
# --------------------------------------------------

def record_trade(variant):
    """Record a trade or loss without deleting collection history."""

    entry = find_owned(variant)

    if entry is None:
        print("Sprite variant is not in your collection.")
        return False

    old_status = entry["status"]

    if entry["status"] == "Level 5":
        entry["status"] = "Mastered"

    if not save_collection():
        entry["status"] = old_status
        return False

    print(
        f"{entry['name']} ({entry['variant']}) "
        "recorded as traded or lost."
    )

    return True


# --------------------------------------------------
# UPDATE COLLECTION ATTRIBUTES
# --------------------------------------------------

def update_attribute(variant, attribute, value):
    """Update a personal collection attribute."""

    entry = find_owned(variant)

    if entry is None:
        print("Sprite variant is not in your collection.")
        return False

    if attribute not in ("first_edition", "won_match"):
        print("Invalid collection attribute.")
        return False

    if not isinstance(value, bool):
        print("Attribute value must be True or False.")
        return False

    old_value = entry[attribute]
    entry[attribute] = value

    if not save_collection():
        entry[attribute] = old_value
        return False

    return True


def update_first_edition(variant, value):
    """Update the First Edition attribute."""

    return update_attribute(variant, "first_edition", value)


def update_won_match(variant, value):
    """Update the Won Match attribute."""

    return update_attribute(variant, "won_match", value)


# --------------------------------------------------
# REMOVE SPRITE
# --------------------------------------------------

def remove_sprite(variant):
    """Remove a Sprite variant from the collection."""

    entry = find_owned(variant)

    if entry is None:
        print("Sprite variant is not in your collection.")
        return False

    collection["owned"].remove(entry)

    if not save_collection():
        collection["owned"].append(entry)
        return False

    print(
        f"Removed {entry['name']} ({entry['variant']}) "
        "from your collection."
    )

    return True


# --------------------------------------------------
# RESET COLLECTION
# --------------------------------------------------

def reset_collection():
    """Remove every record from the collection."""

    old_collection = collection["owned"].copy()
    collection["owned"].clear()

    if not save_collection():
        collection["owned"].extend(old_collection)
        return False

    print("Collection has been reset.")
    return True


# --------------------------------------------------
# COLLECTION STATISTICS
# --------------------------------------------------

def get_collection_stats():
    """Return collection statistics."""

    total = len(collection["owned"])

    unmastered = 0
    mastered = 0
    level_5 = 0

    first_edition = 0
    won_match = 0

    for entry in collection["owned"]:

        if entry["status"] == "Unmastered":
            unmastered += 1

        elif entry["status"] == "Mastered":
            mastered += 1

        elif entry["status"] == "Level 5":
            level_5 += 1

        if entry["first_edition"]:
            first_edition += 1

        if entry["won_match"]:
            won_match += 1

    return {
        "total": total,
        "unmastered": unmastered,
        "mastered": mastered,
        "level_5": level_5,
        "first_edition": first_edition,
        "won_match": won_match,
    }


# --------------------------------------------------
# DISPLAY COLLECTION
# --------------------------------------------------

def display_collection():
    """Display the user's collection grouped by Sprite."""

    if not collection["owned"]:
        print("\nYour collection is empty.")
        return

    print("\n" + "=" * 55)
    print("                  SPRITE COLLECTION")
    print("=" * 55)

    for sprite in ALL_SPRITES:

        entries = [
            entry
            for entry in collection["owned"]
            if entry["name"] == sprite.name
        ]

        if not entries:
            continue

        print(f"\n{sprite.name}")

        for entry in sorted(entries, key=lambda item: item["number"]):

            fe = "Yes" if entry["first_edition"] else "No"
            wm = "Yes" if entry["won_match"] else "No"

            print(
                f"  {entry['variant']:<10} "
                f"[{entry['status']:<10}] "
                f"FE: {fe:<3} | WM: {wm}"
            )

    stats = get_collection_stats()

    print("\n" + "-" * 55)
    print(f"Total variants: {stats['total']}")
    print(f"Unmastered: {stats['unmastered']}")
    print(f"Mastered: {stats['mastered']}")
    print(f"Level 5: {stats['level_5']}")
    print(f"First Edition: {stats['first_edition']}")
    print(f"Won Match: {stats['won_match']}")
    print("=" * 55)


# --------------------------------------------------
# TRADE ADVERTISEMENT
# --------------------------------------------------

def generate_trade_ad():
    """Generate a categorized Sprite trade advertisement."""

    owned_by_number = {
        entry["number"]: entry
        for entry in collection["owned"]
    }

    all_variants = [
        variant
        for sprite in ALL_SPRITES
        for variant in sprite.variants
    ]

    total_variants = len(all_variants)
    total_owned = len(owned_by_number)
    missing_count = total_variants - total_owned

    percentage = (
        total_owned / total_variants * 100
        if total_variants > 0
        else 0
    )

    missing = []
    unmastered = []
    for_trade = []

    for variant in all_variants:

        entry = owned_by_number.get(variant.number)

        if entry is None:
            missing.append({
                "number": variant.number,
                "name": variant.sprite.name,
                "variant": variant.name,
                "status": "Missing",
            })

        elif entry["status"] == "Unmastered":
            unmastered.append(entry)

        else:
            for_trade.append(entry)

    lines = [
        "=" * 60,
        "                    SPRITE TRADES",
        "=" * 60,
        "",
        f"Collection: {total_owned}/{total_variants} "
        f"({percentage:.1f}%)",
        f"Missing: {missing_count} | "
        f"Unmastered: {len(unmastered)} | "
        f"Mastered: {len(for_trade)}",
    ]

    def add_section(title, entries):
        """Add a categorized section grouped by Sprite."""

        lines.append("")
        lines.append("-" * 60)
        lines.append(f"{title} ({len(entries)})")
        lines.append("-" * 60)

        if not entries:
            lines.append("None")
            return

        grouped = {}

        for entry in entries:
            grouped.setdefault(entry["name"], []).append(entry)

        for sprite in ALL_SPRITES:

            sprite_entries = grouped.get(sprite.name, [])

            if not sprite_entries:
                continue

            variants = []

            for entry in sorted(
                sprite_entries,
                key=lambda item: item["number"]
            ):

                variant_text = entry["variant"]

                if entry["status"] == "Level 5":
                    variant_text += " (Level 5)"

                variants.append(variant_text)

            lines.append(
                f"{sprite.name}: {', '.join(variants)}"
            )

    add_section("LF", missing)
    add_section("UNMASTERED", unmastered)
    add_section("FT", for_trade)

    lines.append("-" * 60)

    return "\n".join(lines)


def display_trade_ad():
    """Display the generated Sprite trade advertisement."""

    print()
    print(generate_trade_ad())
