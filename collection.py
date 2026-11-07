
import json
from pathlib import Path

from sprites import ALL_SPRITES, get_sprite, normalize_name
SUPPORTED_SEASON = "C7S5"


# --------------------------------------------------
# COLLECTION SETTINGS
# --------------------------------------------------

DATA_FILE = Path(__file__).parent / "data" / "collection.json"

SAVE_FORMAT_VERSION = 2

STATUSES = ["Unmastered", "Mastered", "Level 5"]

# The collection starts empty until load_collection() is called.
collection = {"owned": []}


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def find_variant(sprite, variant_name):
    """Find a variant belonging to a Sprite."""

    for variant in sprite.variants:
        if normalize_name(variant.name) == normalize_name(variant_name):
            return variant

    return None


def validate_sprite(sprite_name):
    """Check whether a Sprite exists in the database."""

    return get_sprite(sprite_name)


def validate_variant(sprite, variant_name):
    """Check whether a variant exists and is available."""

    variant = find_variant(sprite, variant_name)

    if variant is None or variant.status != "Available":
        return None

    return variant


def validate_status(status):
    """Check whether a mastery status is valid."""

    return status in STATUSES


def validate_save_data(data):
    """Validate the structure of a collection save file."""

    if not isinstance(data, dict):
        raise ValueError("Collection data must be a dictionary.")

    if not isinstance(data.get("season"), str):
        raise ValueError("Collection is missing valid season metadata.")

    version = data.get("version")

    if type(version) is not int or version < 1:
        raise ValueError("Collection has an invalid save format version.")

    if not isinstance(data.get("owned"), list):
        raise ValueError("Collection is missing a valid owned list.")

    for entry in data["owned"]:
        if not isinstance(entry, dict):
            raise ValueError("Collection contains an invalid entry.")

        for field in ("name", "variant", "status"):
            if not isinstance(entry.get(field), str):
                raise ValueError(f"Collection entry is missing {field}.")

        if not validate_status(entry["status"]):
            raise ValueError(
                f"Invalid mastery status: {entry['status']}"
            )

    return data


def check_compatibility(data):
    """Check whether a save file matches the current release."""

    if data["season"] != SUPPORTED_SEASON:
        raise ValueError(
            f"This collection belongs to {data['season']}, "
            f"but this release supports {SUPPORTED_SEASON}."
        )

    if data["version"] != SAVE_FORMAT_VERSION:
        raise ValueError(
            f"This collection uses save format v{data['version']}, "
            f"but this release requires v{SAVE_FORMAT_VERSION}."
        )


# --------------------------------------------------
# LOADING AND SAVING
# --------------------------------------------------

def load_collection():
    """Load the collection from its JSON file."""

    global collection

    if not DATA_FILE.exists():
        collection = {"owned": []}
        return collection

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    validate_save_data(data)
    check_compatibility(data)

    collection = {"owned": data["owned"]}

    return collection


def save_collection():
    """Save the current collection to JSON."""

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "season": SUPPORTED_SEASON,
        "version": SAVE_FORMAT_VERSION,
        "owned": collection["owned"]
    }

    temp_file = DATA_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    temp_file.replace(DATA_FILE)


# --------------------------------------------------
# COLLECTION LOOKUP
# --------------------------------------------------

def find_owned(sprite_name, variant_name):
    """Find an owned Sprite variant."""

    for entry in collection["owned"]:
        if (
            normalize_name(entry["name"]) == normalize_name(sprite_name)
            and normalize_name(entry["variant"]) == normalize_name(variant_name)
        ):
            return entry

    return None


# --------------------------------------------------
# ADDING SPRITES
# --------------------------------------------------

def _add_owned_entry(
    owned,
    sprite_name,
    variant_name,
    status,
    announce=True
):
    """Validate and add an entry to an owned list."""

    sprite = validate_sprite(sprite_name)

    if sprite is None:
        print("Sprite not found.")
        return False

    variant = validate_variant(sprite, variant_name)

    if variant is None:
        print("Variant not found or currently unavailable.")
        return False

    if not validate_status(status):
        print("Invalid mastery status.")
        return False

    for entry in owned:
        if (
            normalize_name(entry["name"]) == normalize_name(sprite.name)
            and normalize_name(entry["variant"]) == normalize_name(variant.name)
        ):
            print("You already own this variant.")
            return False

    owned.append({
        "name": sprite.name,
        "variant": variant.name,
        "status": status
    })

    if announce:
        print(f"Added {sprite.name} - {variant.name} ({status})")

    return True


def add_sprite(sprite_name, variant_name, status="Unmastered"):
    """Add a Sprite variant to the collection."""

    added = _add_owned_entry(
        collection["owned"],
        sprite_name,
        variant_name,
        status
    )

    if added:
        save_collection()

    return added


# --------------------------------------------------
# UPDATING MASTERY
# --------------------------------------------------

def update_status(sprite_name, variant_name, new_status):
    """Change the mastery status of an owned variant."""

    entry = find_owned(sprite_name, variant_name)

    if entry is None:
        print("You do not own this variant.")
        return False

    if not validate_status(new_status):
        print("Invalid mastery status.")
        return False

    entry["status"] = new_status

    save_collection()

    print(
        f"Updated {entry['name']} - {entry['variant']} "
        f"to {new_status}"
    )

    return True


# --------------------------------------------------
# RECORDING TRADES
# --------------------------------------------------

def record_trade(sprite_name, variant_name):
    """Record a trade involving an owned variant."""

    entry = find_owned(sprite_name, variant_name)

    if entry is None:
        print("You do not own this variant.")
        return False

    if entry["status"] == "Level 5":
        entry["status"] = "Mastered"

    save_collection()

    print(
        f"Recorded trade for {entry['name']} - {entry['variant']}"
    )

    return True


# --------------------------------------------------
# REMOVING SPRITES
# --------------------------------------------------

def remove_sprite(sprite_name, variant_name):
    """Remove an owned variant from the collection."""

    entry = find_owned(sprite_name, variant_name)

    if entry is None:
        print("You do not own this variant.")
        return False

    collection["owned"].remove(entry)

    save_collection()

    print(f"Removed {entry['name']} - {entry['variant']}")

    return True


def reset_collection():
    """Remove all owned variants."""

    collection["owned"].clear()

    save_collection()

    print("Collection has been reset.")


# --------------------------------------------------
# COLLECTION STATISTICS
# --------------------------------------------------

def get_available_variants():
    """Return all currently obtainable Sprite variants."""

    available = []

    for sprite in ALL_SPRITES:
        for variant in sprite.variants:
            if variant.status == "Available":
                available.append((sprite.name, variant.name))

    return available


def get_collection_stats():
    """Calculate collection completion and mastery statistics."""

    available = get_available_variants()

    total = len(available)
    owned = len(collection["owned"])

    unmastered = sum(
        entry["status"] == "Unmastered"
        for entry in collection["owned"]
    )

    mastered = sum(
        entry["status"] in ["Mastered", "Level 5"]
        for entry in collection["owned"]
    )

    missing = total - owned

    percentage = (owned / total * 100) if total else 0

    return {
        "total": total,
        "owned": owned,
        "missing": missing,
        "unmastered": unmastered,
        "mastered": mastered,
        "percentage": percentage
    }


# --------------------------------------------------
# TRADE ADVERTISEMENT
# --------------------------------------------------

def generate_trade_ad():
    """Generate a text-based Sprite trade advertisement."""

    owned = set()
    unmastered = set()
    level_5 = set()

    for entry in collection["owned"]:
        key = (
            normalize_name(entry["name"]),
            normalize_name(entry["variant"])
        )

        owned.add(key)

        if entry["status"] == "Unmastered":
            unmastered.add(key)

        elif entry["status"] == "Level 5":
            level_5.add(key)

    available = get_available_variants()

    looking_for = []
    unmastered_list = []
    for_trade = []

    for sprite_name, variant_name in available:
        key = (
            normalize_name(sprite_name),
            normalize_name(variant_name)
        )

        if key not in owned:
            looking_for.append((sprite_name, variant_name))

        if key in unmastered:
            unmastered_list.append((sprite_name, variant_name))

        if key in owned and key not in unmastered:
            for_trade.append((sprite_name, variant_name))

    def format_group(items, show_level_5=False):
        """Group variants under their Sprite names."""

        groups = {}

        for sprite_name, variant_name in items:
            groups.setdefault(sprite_name, []).append(variant_name)

        lines = []

        for sprite_name, variants in groups.items():
            lines.append(f"{sprite_name}: " + ", ".join(variants))

            if show_level_5:
                for variant_name in variants:
                    key = (
                        normalize_name(sprite_name),
                        normalize_name(variant_name)
                    )

                    if key in level_5:
                        lines.append(f"  - {variant_name} - Level 5")

        return "\n".join(lines) if lines else "None"

    return (
        "LF:\n"
        + format_group(looking_for)
        + "\n\nUNMASTERED:\n"
        + format_group(unmastered_list)
        + "\n\nFT:\n"
        + format_group(for_trade, show_level_5=True)
    )


# --------------------------------------------------
# DISPLAY COLLECTION
# --------------------------------------------------



def generate_trade_ad():
    """Generate structured Looking For, Unmastered, and For Trade lists."""

    trade_ad = {
        "LF": {},
        "UNMASTERED": {},
        "FT": {}
    }

    for sprite in ALL_SPRITES:

        for variant in sprite.variants:

            if variant.status != "Available":
                continue

            entry = find_owned(sprite.name, variant.name)

            if entry is None:
                category = "LF"

            elif entry["status"] == "Unmastered":
                category = "UNMASTERED"

            elif entry["status"] in ("Mastered", "Level 5"):
                category = "FT"

            else:
                continue

            trade_ad[category].setdefault(sprite.name, []).append({
                "name": variant.name,
                "status": entry["status"] if entry else None
            })

    return trade_ad

def display_collection():
    """Display collection statistics and condensed trade advertisement."""

    stats = get_collection_stats()
    trade_ad = generate_trade_ad()

    print("\n" + "=" * 60)
    print("                    SPRITE TRADES")
    print("=" * 60)

    print(
        f"\nCollection: {stats['owned']}/{stats['total']} "
        f"({stats['percentage']:.1f}%)"
    )

    print(
        f"Missing: {stats['missing']} | "
        f"Unmastered: {stats['unmastered']} | "
        f"Mastered: {stats['mastered']}"
    )

    for category in ("LF", "UNMASTERED", "FT"):

        entries = trade_ad[category]

        count = sum(
            len(variants)
            for variants in entries.values()
        )

        print("\n" + "-" * 60)
        print(f"{category} ({count})")
        print("-" * 60)

        if not entries:
            print("None")
            continue

        for sprite_name, variants in entries.items():

            formatted_variants = []

            for variant in variants:

                variant_name = variant["name"]
                status = variant["status"]

                if status == "Level 5":
                    formatted_variants.append(
                        f"{variant_name} (Level 5)"
                    )
                else:
                    formatted_variants.append(variant_name)

            print(
                f"{sprite_name}: "
                f"{', '.join(formatted_variants)}"
            )

    print("-" * 60)
