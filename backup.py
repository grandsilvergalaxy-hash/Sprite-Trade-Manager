
import json
import shutil

from pathlib import Path

import collection as collection_module

from sprites import (
    ALL_VARIANTS,
    SPRITE_DATABASE_VERSION,
)


# --------------------------------------------------
# VERSION SETTINGS
# --------------------------------------------------

SUPPORTED_SEASON = "C7S5"

CURRENT_SAVE_VERSION = 3
CURRENT_DATABASE_VERSION = SPRITE_DATABASE_VERSION

SUPPORTED_SAVE_VERSIONS = [1, 2, 3]
LEGACY_DATABASE_VERSION = 2


# --------------------------------------------------
# FILE SETTINGS
# --------------------------------------------------

DATA_FILE = collection_module.DATA_FILE

BACKUP_FILE = DATA_FILE.with_suffix(".bak")
TEMP_FILE = DATA_FILE.with_suffix(".tmp")
TEMP_BACKUP_FILE = BACKUP_FILE.with_suffix(".tmp")

SAFETY_FILE = DATA_FILE.with_name("collection.pre_restore.json")
TEMP_SAFETY_FILE = SAFETY_FILE.with_suffix(".tmp")


# --------------------------------------------------
# CATALOG LOOKUP
# --------------------------------------------------

def find_catalog_variant(sprite_name, variant_name):
    """Find a variant using its Sprite and variant names."""

    for variant in ALL_VARIANTS:

        sprite = getattr(variant, "sprite", None)

        if sprite is None:
            continue

        if (
            sprite.name == sprite_name
            and variant.name == variant_name
        ):
            return variant

    return None


def find_catalog_variant_by_number(number):
    """Find a variant using its permanent numeric ID."""

    for variant in ALL_VARIANTS:

        if variant.number == number:
            return variant

    return None


# --------------------------------------------------
# SAVE FORMAT NORMALIZATION
# --------------------------------------------------

def normalize_save_header(data):
    """Convert old header names into the current naming convention."""

    normalized = dict(data)

    save_version = normalized.get(
        "save_format_version",
        normalized.get("version"),
    )

    database_version = normalized.get(
        "sprite_database_version",
        normalized.get(
            "database_version",
            LEGACY_DATABASE_VERSION,
        ),
    )

    normalized.pop("version", None)
    normalized.pop("database_version", None)

    normalized["save_format_version"] = save_version
    normalized["sprite_database_version"] = database_version

    return normalized


# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

def validate_legacy_data(data):
    """Validate a v1 or v2 save before migration."""

    if not isinstance(data, dict):
        raise ValueError("Collection data must be a dictionary.")

    if data.get("season") != SUPPORTED_SEASON:
        raise ValueError("Unsupported Fortnite season.")

    version = data.get("save_format_version")

    if version not in (1, 2):
        raise ValueError("Invalid legacy save version.")

    if not isinstance(data.get("owned"), list):
        raise ValueError("Collection owned data must be a list.")

    seen = set()

    for entry in data["owned"]:

        if not isinstance(entry, dict):
            raise ValueError("Collection records must be dictionaries.")

        name = entry.get("name")
        variant_name = entry.get("variant")
        status = entry.get("status")

        if not isinstance(name, str):
            raise ValueError("A collection record has an invalid Sprite name.")

        if not isinstance(variant_name, str):
            raise ValueError("A collection record has an invalid variant name.")

        if status not in collection_module.STATUSES:
            raise ValueError(
                f"Invalid mastery status for {name} - {variant_name}."
            )

        variant = find_catalog_variant(name, variant_name)

        if variant is None:
            raise ValueError(
                f"Unknown Sprite variant: {name} - {variant_name}."
            )

        if variant.number in seen:
            raise ValueError(
                f"Duplicate collection entry: #{variant.number}."
            )

        seen.add(variant.number)

        for attribute in ("first_edition", "won_match"):

            if attribute in entry and not isinstance(entry[attribute], bool):
                raise ValueError(
                    f"{attribute} must be True or False."
                )


def validate_collection_data(data):
    """Validate collection data using the current v3 schema."""

    if not isinstance(data, dict):
        raise ValueError("Collection data must be a dictionary.")

    if data.get("save_format_version") != CURRENT_SAVE_VERSION:
        raise ValueError("Collection must use save format v3.")

    if data.get("sprite_database_version") != CURRENT_DATABASE_VERSION:
        raise ValueError("Collection must use the current Sprite database.")

    if data.get("season") != SUPPORTED_SEASON:
        raise ValueError("Unsupported Fortnite season.")

    if not isinstance(data.get("owned"), list):
        raise ValueError("Collection owned data must be a list.")

    # Use the current collection.py validator.
    if not collection_module.validate_save_data(data):
        raise ValueError("Collection failed v3 validation.")


# --------------------------------------------------
# READ SAVE FILE
# --------------------------------------------------

def read_save_file(file_path):
    """Read and validate a collection JSON file."""

    with open(file_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, dict):
        raise ValueError("Invalid collection file.")

    data = normalize_save_header(raw_data)

    if data.get("season") != SUPPORTED_SEASON:
        raise ValueError("Collection belongs to an unsupported season.")

    version = data.get("save_format_version")

    if version not in SUPPORTED_SAVE_VERSIONS:
        raise ValueError(f"Unsupported save version: {version}.")

    database_version = data.get("sprite_database_version")

    if not isinstance(database_version, int) or isinstance(database_version, bool):
        raise ValueError("Invalid Sprite database version.")

    if database_version > CURRENT_DATABASE_VERSION:
        raise ValueError("Save uses a newer Sprite database.")

    if version in (1, 2):
        validate_legacy_data(data)

    elif version == 3:
        validate_collection_data(data)

    return data


# --------------------------------------------------
# BACKUP CREATION
# --------------------------------------------------

def create_backup():
    """Back up the current collection after validating it."""

    if not DATA_FILE.exists():
        return False

    read_save_file(DATA_FILE)

    BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy2(DATA_FILE, TEMP_BACKUP_FILE)
        TEMP_BACKUP_FILE.replace(BACKUP_FILE)

        return True

    finally:
        if TEMP_BACKUP_FILE.exists():
            TEMP_BACKUP_FILE.unlink()


def create_safety_backup():
    """Preserve the current file before restoring another save."""

    if not DATA_FILE.exists():
        return False

    SAFETY_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy2(DATA_FILE, TEMP_SAFETY_FILE)
        TEMP_SAFETY_FILE.replace(SAFETY_FILE)

        return True

    finally:
        if TEMP_SAFETY_FILE.exists():
            TEMP_SAFETY_FILE.unlink()


# --------------------------------------------------
# FILE WRITING
# --------------------------------------------------

def write_save_file(data):
    """Write validated v3 data using atomic file replacement."""

    validate_collection_data(data)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(TEMP_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        TEMP_FILE.replace(DATA_FILE)

    finally:
        if TEMP_FILE.exists():
            TEMP_FILE.unlink()


def update_loaded_collection(owned):
    """Update the collection without replacing its dictionary."""

    collection_module.collection["owned"].clear()
    collection_module.collection["owned"].extend(owned)


def save_collection():
    """Save the current in-memory collection in v3 format."""

    data = {
        "save_format_version": CURRENT_SAVE_VERSION,
        "sprite_database_version": CURRENT_DATABASE_VERSION,
        "season": SUPPORTED_SEASON,
        "owned": collection_module.collection["owned"],
    }

    write_save_file(data)


# --------------------------------------------------
# MIGRATION
# --------------------------------------------------

def migrate_v1_to_v2(data):
    """Convert an older v1 save into the intermediate v2 format."""

    if data["save_format_version"] != 1:
        raise ValueError("This migration only supports save v1.")

    migrated_entries = []

    for entry in data["owned"]:

        migrated_entries.append({
            "name": entry["name"],
            "variant": entry["variant"],
            "status": entry["status"],
            "first_edition": entry.get("first_edition", False),
            "won_match": entry.get("won_match", False),
        })

    return {
        "season": SUPPORTED_SEASON,
        "save_format_version": 2,
        "sprite_database_version": LEGACY_DATABASE_VERSION,
        "owned": migrated_entries,
    }


def migrate_v2_to_v3(data):
    """Convert v2 records into the v3 numeric-ID format."""

    if data["save_format_version"] != 2:
        raise ValueError("This migration only supports save v2.")

    print("\n" + "=" * 55)
    print("             COLLECTION MIGRATION")
    print("=" * 55)

    print("Save format: v2 -> v3")
    print("Sprite database: v2 -> v3")
    print("\nMigrating collection records...")

    migrated_entries = []

    for entry in data["owned"]:

        variant = find_catalog_variant(
            entry["name"],
            entry["variant"],
        )

        if variant is None:
            raise ValueError(
                f"Cannot migrate unknown variant: "
                f"{entry['name']} - {entry['variant']}."
            )

        migrated_entry = {
            "number": variant.number,
            "name": variant.sprite.name,
            "variant": variant.name,
            "status": entry["status"],
            "first_edition": entry.get("first_edition", False),
            "won_match": entry.get("won_match", False),
        }

        migrated_entries.append(migrated_entry)

    migrated_data = {
        "save_format_version": CURRENT_SAVE_VERSION,
        "sprite_database_version": CURRENT_DATABASE_VERSION,
        "season": SUPPORTED_SEASON,
        "owned": migrated_entries,
    }

    validate_collection_data(migrated_data)

    print(
        f"\n{len(migrated_entries)} collection records "
        "migrated successfully."
    )

    print("\nNew collection attributes:")
    print("  FE - First Edition")
    print("  WM - Won Match")

    print("\nMissing attributes were initialized to No.")
    print("Existing attribute values were preserved when present.")
    print("Existing mastery progress preserved.")

    print("\nOriginal collection backed up successfully.")

    print("\nMigration complete!")
    print("=" * 55)

    return migrated_data


def migrate_to_current(data):
    """Migrate an older save through each required version."""

    version = data["save_format_version"]

    if version == 1:
        print("\nOlder save format v1 detected.")
        data = migrate_v1_to_v2(data)

    if data["save_format_version"] == 2:
        data = migrate_v2_to_v3(data)

    validate_collection_data(data)

    return data


# --------------------------------------------------
# BACKUP RESTORATION
# --------------------------------------------------

def restore_backup():
    """Restore a valid backup and migrate it if necessary."""

    if not BACKUP_FILE.exists():
        raise FileNotFoundError("No backup file was found.")

    data = read_save_file(BACKUP_FILE)

    create_safety_backup()

    data = migrate_to_current(data)

    write_save_file(data)
    update_loaded_collection(data["owned"])

    print("\nBackup restored successfully.")

    return True


# --------------------------------------------------
# RECOVERY SCREEN
# --------------------------------------------------

def recovery_screen(problem):
    """Offer recovery when the main collection cannot load."""

    print("\n" + "=" * 55)
    print("                 COLLECTION RECOVERY")
    print("=" * 55)

    print(f"\nProblem: {problem}")

    if BACKUP_FILE.exists():

        try:
            backup_data = read_save_file(BACKUP_FILE)

            print(
                f"\nBackup detected: "
                f"Save v{backup_data['save_format_version']}, "
                f"database v{backup_data['sprite_database_version']}"
            )

        except (
            ValueError,
            json.JSONDecodeError,
            OSError,
            KeyError,
            TypeError,
        ) as error:

            print(f"\nBackup is invalid: {error}")

    else:
        print("\nNo backup file was found.")

    while True:

        print("\n1. Restore from backup")
        print("2. Exit without making changes")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":

            try:
                restore_backup()
                return

            except (
                ValueError,
                json.JSONDecodeError,
                OSError,
                KeyError,
                TypeError,
            ) as error:

                print(f"\nRecovery failed: {error}")

        elif choice == "2":

            print("\nExiting without modifying the collection.")
            raise SystemExit(0)

        else:
            print("Invalid selection.")


# --------------------------------------------------
# INITIALIZE COLLECTION
# --------------------------------------------------

def initialize_collection():
    """Load, migrate, or recover the collection at startup."""

    if not DATA_FILE.exists():

        new_data = {
            "save_format_version": CURRENT_SAVE_VERSION,
            "sprite_database_version": CURRENT_DATABASE_VERSION,
            "season": SUPPORTED_SEASON,
            "owned": [],
        }

        write_save_file(new_data)
        update_loaded_collection([])

        print("\nNew v3 collection initialized.")

        return collection_module.collection

    try:
        data = read_save_file(DATA_FILE)

        save_version = data["save_format_version"]
        database_version = data["sprite_database_version"]

        needs_migration = (
            save_version < CURRENT_SAVE_VERSION
            or database_version < CURRENT_DATABASE_VERSION
        )

        if needs_migration:

            # Preserve the original before changing anything.
            if not create_backup():
                raise OSError("Could not create the original collection backup.")

            data = migrate_to_current(data)

            write_save_file(data)

        update_loaded_collection(data["owned"])

        print(
            f"\nCollection loaded successfully: "
            f"{SUPPORTED_SEASON} v{CURRENT_SAVE_VERSION}"
        )

        return collection_module.collection

    except (
        ValueError,
        json.JSONDecodeError,
        OSError,
        KeyError,
        TypeError,
    ) as error:

        recovery_screen(error)

        return collection_module.collection
