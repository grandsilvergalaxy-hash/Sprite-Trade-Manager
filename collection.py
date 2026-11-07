
import json
from pathlib import Path

from sprites import ALL_SPRITES, get_sprite, normalize_name


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = Path(__file__).parent / "data" / "collection.json"

STATUSES = ["Unmastered", "Mastered", "Level 5"]

COLLECTION_VERSION = 3


# ============================================================
# SPRITE VALIDATION
# ============================================================

def find_variant(sprite, variant_name):
    """Find a variant belonging to a Sprite."""

    for variant in sprite.variants:
        if normalize_name(variant.name) == normalize_name(variant_name):
            return variant

    return None


def validate_sprite(name):
    """Return a Sprite object if it exists."""

    sprite = get_sprite(name)

    if sprite is None:
        raise ValueError(f"Unknown Sprite: {name}")

    return sprite


def validate_variant(sprite, variant_name):
    """Return a variant if it exists and is available."""

    variant = find_variant(sprite, variant_name)

    if variant is None:
        raise ValueError(
            f"{variant_name} is not a variant of {sprite.name}."
        )

    if variant.status != "Available":
        raise ValueError(
            f"{variant.name} is not currently available."
        )

    return variant


def validate_status(status):
    """Check whether a mastery status is valid."""

    if status not in STATUSES:
        raise ValueError(
            f"Invalid status. Choose from: {', '.join(STATUSES)}"
        )


# ============================================================
# COLLECTION STORAGE
# ============================================================

def save_collection():
    """Save the collection to the JSON file."""

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": COLLECTION_VERSION,
        "owned": collection["owned"]
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_collection():
    """Load the collection and migrate older data if necessary."""

    if not DATA_FILE.exists():
        return {"owned": []}

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    version = data.get("version", 1)

    if version == COLLECTION_VERSION:
        return {"owned": data.get("owned", [])}

    # Migrate version 2 records.
    if version == 2:
        print("Migrating collection from version 2 to version 3...")

        return {
            "owned": data.get("owned", [])
        }

    # Migrate the original collection format.
    if version == 1:
        print("Migrating older collection data...")

        owned = []

        old_owned = data.get("owned", [])
        old_mastered = data.get("mastered", [])
        old_level_5 = data.get("level_5", [])

        for name in old_owned:
            status = "Unmastered"

            if name in old_mastered:
                status = "Mastered"

            if name in old_level_5:
                status = "Level 5"

            owned.append({
                "name": name,
                "variant": "Base",
                "status": status
            })

        return {"owned": owned}

    raise ValueError("Unsupported collection file version.")


# Load the collection when this module is imported.
collection = load_collection()


# ============================================================
# COLLECTION LOOKUPS
# ============================================================

def find_owned(name, variant_name):
    """Find an owned variant in the collection."""

    for entry in collection["owned"]:
        if (
            normalize_name(entry["name"]) == normalize_name(name)
            and normalize_name(entry["variant"])
            == normalize_name(variant_name)
        ):
            return entry

    return None


# ============================================================
# ADDING SPRITES
# ============================================================

def add_sprite(name, variant_name="Base", status="Unmastered"):
    """Add a variant to the owned collection."""

    sprite = validate_sprite(name)
    variant = validate_variant(sprite, variant_name)

    validate_status(status)

    if find_owned(sprite.name, variant.name):
        print(f"You already own {sprite.name} ({variant.name}).")
        return False

    collection["owned"].append({
        "name": sprite.name,
        "variant": variant.name,
        "status": status
    })

    save_collection()

    print(f"Added {sprite.name} ({variant.name}) to your collection.")

    return True


# ============================================================
# UPDATING MASTERY
# ============================================================

def update_status(name, variant_name, new_status):
    """Change the mastery status of an owned variant."""

    validate_status(new_status)

    entry = find_owned(name, variant_name)

    if entry is None:
        print("You do not own this variant.")
        return False

    entry["status"] = new_status

    save_collection()

    print(
        f"Updated {entry['name']} ({entry['variant']}) "
        f"to {new_status}."
    )

    return True


# ============================================================
# RECORDING TRADES
# ============================================================

def record_trade(name, variant_name):
    """
    Record a trade.

    Level 5 becomes Mastered.
    Mastered and Unmastered statuses remain unchanged.
    Ownership is retained.
    """

    entry = find_owned(name, variant_name)

    if entry is None:
        print("You do not own this variant.")
        return False

    if entry["status"] == "Level 5":
        entry["status"] = "Mastered"

        save_collection()

        print(
            f"{entry['name']} ({entry['variant']}) "
            "is now recorded as Mastered."
        )

    else:
        print("No mastery status change was necessary.")

    return True


# ============================================================
# REMOVING SPRITES
# ============================================================

def remove_sprite(name, variant_name):
    """Remove an owned variant completely."""

    entry = find_owned(name, variant_name)

    if entry is None:
        print("This variant is not in your collection.")
        return False

    collection["owned"].remove(entry)

    save_collection()

    print(f"Removed {name} ({variant_name}) from your collection.")

    return True


# ============================================================
# RESETTING THE COLLECTION
# ============================================================

def reset_collection():
    """Clear all owned variants."""

    collection["owned"].clear()

    save_collection()

    print("Your collection has been reset.")


# ============================================================
# AVAILABLE VARIANTS
# ============================================================

def get_available_variants():
    """Return every currently obtainable Sprite variant."""

    available = []

    for sprite in ALL_SPRITES:
        for variant in sprite.variants:

            if variant.status == "Available":
                available.append({
                    "name": sprite.name,
                    "variant": variant.name
                })

    return available


# ============================================================
# COLLECTION STATISTICS
# ============================================================

def get_collection_stats():
    """Calculate collection progress."""

    available = get_available_variants()

    total = len(available)
    owned = len(collection["owned"])

    mastered = sum(
        1 for entry in collection["owned"]
        if entry["status"] in ["Mastered", "Level 5"]
    )

    unmastered = sum(
        1 for entry in collection["owned"]
        if entry["status"] == "Unmastered"
    )

    looking_for = total - owned

    return {
        "total": total,
        "owned": owned,
        "mastered": mastered,
        "unmastered": unmastered,
        "looking_for": looking_for
    }


# ============================================================
# TRADE ADVERTISEMENT
# ============================================================

def generate_trade_ad():
    """Generate LF, UNMASTERED, and FT sections."""

    available = get_available_variants()

    # Create sets of owned and unmastered variants.
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

    # Determine which category each available variant belongs to.
    looking_for = []
    unmastered_list = []
    for_trade = []

    for item in available:

        key = (
            normalize_name(item["name"]),
            normalize_name(item["variant"])
        )

        if key not in owned:
            looking_for.append(item)

        elif key in unmastered:
            unmastered_list.append(item)

        else:
            for_trade.append(item)

    # Group variants under their Sprite names.
    def group_variants(variants, show_level_5=False):

        grouped = {}

        for item in variants:
            name = item["name"]
            variant_name = item["variant"]

            key = (
                normalize_name(name),
                normalize_name(variant_name)
            )

            if name not in grouped:
                grouped[name] = []

            if show_level_5 and key in level_5:
                grouped[name].append(f"{variant_name} - Level 5")
            else:
                grouped[name].append(variant_name)

        lines = []

        for name, variant_names in grouped.items():
            lines.append(
                f"{name} ({', '.join(variant_names)})"
            )

        return lines

    # Build the advertisement.
    lf_lines = group_variants(looking_for)
    unmastered_lines = group_variants(unmastered_list)
    ft_lines = group_variants(for_trade, show_level_5=True)

    sections = [
        ("LF", lf_lines),
        ("UNMASTERED", unmastered_lines),
        ("FT", ft_lines)
    ]

    advertisement = []

    for title, lines in sections:
        advertisement.append(f"{title}:")

        if lines:
            advertisement.extend(lines)
        else:
            advertisement.append("(None)")

        advertisement.append("")

    return "\n".join(advertisement).strip()


# ============================================================
# COLLECTION DISPLAY
# ============================================================

def display_collection():
    """Display collection statistics and the trade advertisement."""

    stats = get_collection_stats()

    print("\nSPRITE COLLECTION MANAGER")
    print("=========================")

    print(f"Owned:       {stats['owned']}/{stats['total']}")
    print(f"Mastered:    {stats['mastered']}/{stats['total']}")
    print(f"Looking For: {stats['looking_for']}")

    print("\n" + "=" * 60)
    print("                    SPRITE TRADES")
    print("=" * 60)

    print(generate_trade_ad())


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    display_collection()
