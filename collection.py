
import json
import shutil
from pathlib import Path

from sprites import ALL_SPRITES, get_sprite, normalize_name


# ============================================================
# COLLECTION SETTINGS
# ============================================================

DATA_FILE = Path(__file__).parent / "data" / "collection.json"
BACKUP_FILE = DATA_FILE.with_suffix(".bak")

TEMP_FILE = DATA_FILE.with_suffix(".tmp")
TEMP_BACKUP_FILE = BACKUP_FILE.with_suffix(".tmp")

SAFETY_FILE = DATA_FILE.with_name("collection.pre_restore.json")
SAFETY_TEMP_FILE = DATA_FILE.with_name("collection.pre_restore.tmp")

CURRENT_SEASON = "C7S5"
COLLECTION_VERSION = 1

STATUSES = ["Unmastered", "Mastered", "Level 5"]


# ============================================================
# VALIDATION
# ============================================================

def find_variant(sprite, variant_name):
    """Find a variant belonging to a Sprite."""

    for variant in sprite.variants:
        if normalize_name(variant.name) == normalize_name(variant_name):
            return variant

    return None


def validate_sprite(name):
    """Check whether a Sprite exists."""

    sprite = get_sprite(name)

    if sprite is None:
        raise ValueError(f"Unknown Sprite: {name}")

    return sprite


def validate_variant(sprite, variant_name):
    """Check whether a variant exists and is available."""

    variant = find_variant(sprite, variant_name)

    if variant is None:
        raise ValueError(
            f"{variant_name} is not a valid variant of {sprite.name}."
        )

    if variant.status != "Available":
        raise ValueError(f"{variant.name} is not currently available.")

    return variant


def validate_status(status):
    """Check whether a mastery status is valid."""

    if status not in STATUSES:
        raise ValueError(f"Invalid mastery status: {status}")

    return status


def validate_save_data(data):
    """Validate the structure of a collection save."""

    if not isinstance(data, dict):
        raise ValueError("Collection must be a JSON object.")

    season = data.get("season")
    version = data.get("version")
    owned = data.get("owned")

    if not isinstance(season, str) or not season:
        raise ValueError("Missing or invalid collection season.")

    if type(version) is not int or version < 1:
        raise ValueError("Missing or invalid save version.")

    if not isinstance(owned, list):
        raise ValueError("Invalid owned collection data.")

    for entry in owned:
        if not isinstance(entry, dict):
            raise ValueError("Invalid collection entry.")

        if not all(
            isinstance(entry.get(key), str)
            for key in ["name", "variant", "status"]
        ):
            raise ValueError("Invalid collection entry fields.")

        validate_status(entry["status"])

    return data


def read_collection_file(path):
    """Read and validate a collection JSON file."""

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return validate_save_data(data)


def is_compatible(data):
    """Check whether a collection matches this release."""

    return (
        data["season"] == CURRENT_SEASON
        and data["version"] == COLLECTION_VERSION
    )


def describe_collection(data):
    """Return a readable season and version label."""

    return f"{data['season']} v{data['version']}"


def get_file_description(path):
    """Describe a collection file without modifying it."""

    if not path.exists():
        return "Not found"

    try:
        data = read_collection_file(path)
        return describe_collection(data)

    except (json.JSONDecodeError, ValueError, OSError):
        return "Invalid or unreadable"


# ============================================================
# BACKUP MANAGEMENT
# ============================================================

def create_backup():
    """Back up a valid, compatible collection."""

    if not DATA_FILE.exists():
        return False

    data = read_collection_file(DATA_FILE)

    if not is_compatible(data):
        raise ValueError(
            "Cannot back up an incompatible collection."
        )

    # Create a temporary backup first.
    shutil.copy2(DATA_FILE, TEMP_BACKUP_FILE)

    # Replace the previous backup only after copying succeeds.
    TEMP_BACKUP_FILE.replace(BACKUP_FILE)

    return True


def backup_collection():
    """Manually create a backup of the collection."""

    try:
        if create_backup():
            print(f"Collection backup created: {BACKUP_FILE.name}")
            return True

        print("No collection file exists to back up.")
        return False

    except (json.JSONDecodeError, ValueError, OSError) as error:
        print(f"Could not create backup: {error}")
        return False


def restore_backup():
    """Restore a backup if it matches the current release."""

    if not BACKUP_FILE.exists():
        raise ValueError("No backup file exists.")

    # Validate backup before touching the main collection.
    backup_data = read_collection_file(BACKUP_FILE)

    if not is_compatible(backup_data):
        raise ValueError(
            "The backup does not match the current season and version."
        )

    # Preserve the current main file before restoring.
    if DATA_FILE.exists():
        shutil.copy2(DATA_FILE, SAFETY_TEMP_FILE)
        SAFETY_TEMP_FILE.replace(SAFETY_FILE)

    # Copy backup to a temporary restore file.
    restore_temp = DATA_FILE.with_suffix(".restore.tmp")

    shutil.copy2(BACKUP_FILE, restore_temp)

    # Replace the main collection only after copying succeeds.
    restore_temp.replace(DATA_FILE)

    print("\nBackup restored successfully!")
    print(f"Restored collection: {describe_collection(backup_data)}")

    if SAFETY_FILE.exists():
        print(f"Previous collection preserved: {SAFETY_FILE.name}")

    return backup_data


# ============================================================
# COLLECTION WRITING
# ============================================================

def write_collection(owned):
    """Write collection data using the current save format."""

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "season": CURRENT_SEASON,
        "version": COLLECTION_VERSION,
        "owned": owned
    }

    with open(TEMP_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    TEMP_FILE.replace(DATA_FILE)


def save_collection():
    """Save the current collection."""

    write_collection(collection["owned"])


# ============================================================
# COMPATIBILITY SCREEN
# ============================================================

def compatibility_screen(problem):
    """Display recovery options for an incompatible collection."""

    backup_description = get_file_description(BACKUP_FILE)

    print("\n" + "=" * 60)
    print("                 COLLECTION MISMATCH")
    print("=" * 60)

    print(f"\nCollection file: {problem}")
    print(
        f"Current release: "
        f"{CURRENT_SEASON} v{COLLECTION_VERSION}"
    )
    print(f"Backup file:     {backup_description}")

    print("\nYour collection could not be loaded.")
    print("Your original files will not be overwritten automatically.")

    print("\nWhat would you like to do?")

    while True:
        print("\n1. Restore from backup")
        print("2. Exit without making changes")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            try:
                restored_data = restore_backup()
                return {"owned": restored_data["owned"]}

            except (json.JSONDecodeError, ValueError, OSError) as error:
                print(f"\nCould not restore backup: {error}")
                print("Your existing collection files were preserved.")

        elif choice == "2":
            print("\nExiting without making changes.")
            raise SystemExit(0)

        else:
            print("Invalid selection. Please choose 1 or 2.")


# ============================================================
# COLLECTION LOADING
# ============================================================

def load_collection():
    """Load, validate, and back up the current collection."""

    if not DATA_FILE.exists():
        return {"owned": []}

    try:
        data = read_collection_file(DATA_FILE)

    except (json.JSONDecodeError, ValueError, OSError) as error:
        return compatibility_screen(
            f"Invalid or unreadable ({error})"
        )

    # Check compatibility BEFORE creating a backup.
    if not is_compatible(data):
        return compatibility_screen(describe_collection(data))

    # Only compatible collections can refresh the backup.
    try:
        create_backup()

    except OSError as error:
        raise ValueError(
            f"Could not create collection backup: {error}"
        ) from error

    return {"owned": data["owned"]}


# ============================================================
# COLLECTION INITIALIZATION
# ============================================================

# Load collection when this module is imported.
collection = load_collection()


# ============================================================
# SPRITE ADDITION LOGIC
# ============================================================

def _add_owned_entry(
    owned,
    sprite_name,
    variant_name,
    status,
    require_available=False,
    announce=True
):
    """Shared Sprite addition logic."""

    sprite = validate_sprite(sprite_name)
    variant = find_variant(sprite, variant_name)

    if variant is None:
        raise ValueError(
            f"{variant_name} is not a valid variant of {sprite.name}."
        )

    if require_available and variant.status != "Available":
        raise ValueError(f"{variant.name} is not currently available.")

    validate_status(status)

    # Prevent duplicate entries.
    for entry in owned:
        if (
            normalize_name(entry["name"]) == normalize_name(sprite.name)
            and normalize_name(entry["variant"]) == normalize_name(variant.name)
        ):
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
        status,
        require_available=True
    )

    if not added:
        print(f"You already own {sprite_name} - {variant_name}.")
        return False

    save_collection()
    return True


# ============================================================
# COLLECTION MANAGEMENT
# ============================================================

def find_owned(sprite_name, variant_name):
    """Find an owned Sprite variant."""

    for entry in collection["owned"]:
        if (
            normalize_name(entry["name"]) == normalize_name(sprite_name)
            and normalize_name(entry["variant"]) == normalize_name(variant_name)
        ):
            return entry

    return None


def update_status(sprite_name, variant_name, status):
    """Update the mastery status of an owned variant."""

    validate_status(status)

    entry = find_owned(sprite_name, variant_name)

    if entry is None:
        print("You do not own that Sprite variant.")
        return False

    entry["status"] = status

    save_collection()

    print(
        f"Updated {entry['name']} - {entry['variant']} "
        f"to {status}."
    )

    return True


def record_trade(sprite_name, variant_name):
    """Record trading away an owned Sprite variant."""

    entry = find_owned(sprite_name, variant_name)

    if entry is None:
        print("You do not own that Sprite variant.")
        return False

    if entry["status"] == "Level 5":
        entry["status"] = "Mastered"

    save_collection()

    print(f"Recorded trade: {entry['name']} - {entry['variant']}.")
    return True


def remove_sprite(sprite_name, variant_name):
    """Remove a Sprite variant from the collection."""

    entry = find_owned(sprite_name, variant_name)

    if entry is None:
        print("You do not own that Sprite variant.")
        return False

    collection["owned"].remove(entry)

    save_collection()

    print(f"Removed {entry['name']} - {entry['variant']}.")
    return True


def reset_collection():
    """Clear the entire collection."""

    collection["owned"].clear()

    save_collection()

    print("Collection has been reset.")


# ============================================================
# COLLECTION INFORMATION
# ============================================================

def get_available_variants():
    """Return all currently available Sprite variants."""

    available = []

    for sprite in ALL_SPRITES:
        for variant in sprite.variants:
            if variant.status == "Available":
                available.append({
                    "name": sprite.name,
                    "variant": variant.name
                })

    return available


def get_collection_stats():
    """Calculate collection ownership and mastery statistics."""

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


# ============================================================
# TRADE ADVERTISEMENT GENERATOR
# ============================================================

def generate_trade_ad():
    """Generate a text-based Sprite trade advertisement."""

    available = get_available_variants()

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

    for entry in collection["owned"]:
        key = (
            normalize_name(entry["name"]),
            normalize_name(entry["variant"])
        )

        if key in unmastered:
            unmastered_list.append(entry)

        elif entry["status"] in ["Mastered", "Level 5"]:
            for_trade.append(entry)

    def format_group(items, show_level_5=False):
        """Group variants by Sprite name."""

        grouped = {}

        for item in items:
            name = item["name"]
            variant = item["variant"]

            if name not in grouped:
                grouped[name] = []

            display = variant

            if show_level_5 and item["status"] == "Level 5":
                display += " - Level 5"

            grouped[name].append(display)

        lines = []

        for name, variants in grouped.items():
            lines.append(f"{name}: {', '.join(variants)}")

        return lines

    ad = []

    ad.append("LF:")
    ad.extend(format_group(looking_for) or ["None"])

    ad.append("")
    ad.append("UNMASTERED:")
    ad.extend(format_group(unmastered_list) or ["None"])

    ad.append("")
    ad.append("FT:")
    ad.extend(format_group(for_trade, show_level_5=True) or ["None"])

    return "\n".join(ad)


# ============================================================
# COLLECTION DISPLAY
# ============================================================

def display_collection():
    """Display collection statistics and the trade advertisement."""

    stats = get_collection_stats()

    print("\n" + "=" * 60)
    print("                    SPRITE TRADES")
    print("=" * 60)

    print(
        f"\nCollection: {stats['owned']}/{stats['total']} "
        f"({stats['percentage']:.1f}%)"
    )

    print(f"Missing: {stats['missing']}")
    print(f"Unmastered: {stats['unmastered']}")
    print(f"Mastered: {stats['mastered']}/{stats['total']}")

    print("\n" + "-" * 60)
    print(generate_trade_ad())
    print("-" * 60)
