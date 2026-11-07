
import json
import shutil

from pathlib import Path

import collection as collection_module

from sprites import get_sprite, normalize_name
SUPPORTED_SEASON = "C7S5"


# --------------------------------------------------
# FILE SETTINGS
# --------------------------------------------------

DATA_FILE = collection_module.DATA_FILE

BACKUP_FILE = DATA_FILE.with_suffix(".bak")
TEMP_FILE = DATA_FILE.with_suffix(".tmp")
TEMP_BACKUP_FILE = BACKUP_FILE.with_suffix(".tmp")

SAFETY_FILE = DATA_FILE.with_name("collection.pre_restore.json")
TEMP_SAFETY_FILE = SAFETY_FILE.with_suffix(".tmp")

CURRENT_SAVE_VERSION = collection_module.SAVE_FORMAT_VERSION

SUPPORTED_SAVE_VERSIONS = [1, 2]


# --------------------------------------------------
# FILE VALIDATION
# --------------------------------------------------

def read_save_file(file_path):
    """Read and validate a collection JSON file."""

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    collection_module.validate_save_data(data)

    if data["season"] != SUPPORTED_SEASON:
        raise ValueError(
            f"Collection belongs to {data['season']}, "
            f"but this release supports {SUPPORTED_SEASON}."
        )

    if data["version"] not in SUPPORTED_SAVE_VERSIONS:
        raise ValueError(
            f"Unsupported collection save version: {data['version']}."
        )

    # Validate Sprite names, variants, and duplicate entries.
    seen = set()

    for entry in data["owned"]:
        sprite = get_sprite(entry["name"])

        if sprite is None:
            raise ValueError(
                f"Unknown Sprite in collection: {entry['name']}."
            )

        variant = None

        for available_variant in sprite.variants:
            if (
                normalize_name(available_variant.name)
                == normalize_name(entry["variant"])
            ):
                variant = available_variant
                break

        if variant is None:
            raise ValueError(
                f"Unknown variant: {entry['name']} - {entry['variant']}."
            )

        key = (
            normalize_name(sprite.name),
            normalize_name(variant.name)
        )

        if key in seen:
            raise ValueError(
                f"Duplicate collection entry: {sprite.name} - {variant.name}."
            )

        seen.add(key)

    return data


# --------------------------------------------------
# BACKUP CREATION
# --------------------------------------------------

def create_backup():
    """Create a backup of the current collection file."""

    if not DATA_FILE.exists():
        return False

    # Never overwrite a good backup with invalid data.
    read_save_file(DATA_FILE)

    BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(DATA_FILE, TEMP_BACKUP_FILE)
    TEMP_BACKUP_FILE.replace(BACKUP_FILE)

    return True


def create_safety_backup():
    """Preserve the current collection before recovery."""

    if not DATA_FILE.exists():
        return False

    shutil.copy2(DATA_FILE, TEMP_SAFETY_FILE)
    TEMP_SAFETY_FILE.replace(SAFETY_FILE)

    return True


# --------------------------------------------------
# WRITING COLLECTION DATA
# --------------------------------------------------

def write_save_file(data):
    """Write collection data using an atomic file replacement."""

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(TEMP_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    TEMP_FILE.replace(DATA_FILE)


def update_loaded_collection(owned):
    """Update the collection module without replacing its dictionary."""

    collection_module.collection["owned"].clear()
    collection_module.collection["owned"].extend(owned)


# --------------------------------------------------
# COLLECTION MIGRATION
# --------------------------------------------------

def migrate_v1_to_v2(data):
    """Migrate a version 1 collection into version 2."""

    if data["version"] != 1:
        raise ValueError("This migration only supports save version 1.")

    print("\nMigrating collection from v1 to v2...")
    print("-" * 50)

    migrated_entries = []

    for entry in data["owned"]:
        sprite = get_sprite(entry["name"])

        # Find the canonical Sprite and variant names.
        variant = next(
            variant
            for variant in sprite.variants
            if normalize_name(variant.name)
            == normalize_name(entry["variant"])
        )

        migrated_entry = {
            "name": sprite.name,
            "variant": variant.name,
            "status": entry["status"]
        }

        migrated_entries.append(migrated_entry)

        print(
            f"Added {sprite.name} - {variant.name} "
            f"({entry['status']})"
        )

    migrated_data = {
        "season": SUPPORTED_SEASON,
        "version": 2,
        "owned": migrated_entries
    }

    print("-" * 50)
    print(
        f"Migration complete! "
        f"{len(migrated_entries)} entries migrated."
    )

    return migrated_data


# --------------------------------------------------
# BACKUP RESTORATION
# --------------------------------------------------

def restore_backup():
    """Restore the collection from the backup file."""

    if not BACKUP_FILE.exists():
        raise FileNotFoundError("No backup file was found.")

    # Validate the backup before changing anything.
    backup_data = read_save_file(BACKUP_FILE)

    # Preserve the current file before replacing it.
    create_safety_backup()

    if backup_data["version"] == 1:
        print("\nThe backup uses save format v1.")
        print("Migrating the restored backup...")

        backup_data = migrate_v1_to_v2(backup_data)

    write_save_file(backup_data)
    update_loaded_collection(backup_data["owned"])

    print("\nBackup restored successfully.")

    if SAFETY_FILE.exists():
        print(f"Previous collection preserved at: {SAFETY_FILE.name}")

    return True


# --------------------------------------------------
# RECOVERY SCREEN
# --------------------------------------------------

def recovery_screen(problem):
    """Offer recovery when the main collection cannot be loaded."""

    print("\n" + "=" * 55)
    print("                 COLLECTION RECOVERY")
    print("=" * 55)

    print(f"\nProblem: {problem}")

    if BACKUP_FILE.exists():
        print("\nBackup file detected.")

        try:
            backup_data = read_save_file(BACKUP_FILE)

            print(
                f"Backup collection: "
                f"{backup_data['season']} v{backup_data['version']}"
            )

        except (ValueError, json.JSONDecodeError, OSError) as error:
            print(f"Backup is invalid or incompatible: {error}")

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
                StopIteration
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
        update_loaded_collection([])
        return collection_module.collection

    try:
        data = read_save_file(DATA_FILE)

        # Migrate an older save format.
        if data["version"] == 1:

            # Preserve the original before migration.
            create_backup()

            print("\nOlder collection format detected.")

            migrated_data = migrate_v1_to_v2(data)

            write_save_file(migrated_data)

            update_loaded_collection(migrated_data["owned"])

        else:
            # Current save format: refresh automatic backup.
            create_backup()

            update_loaded_collection(data["owned"])

        print(
            f"\nCollection loaded: "
            f"{SUPPORTED_SEASON} v{CURRENT_SAVE_VERSION}"
        )

        return collection_module.collection

    except (
        ValueError,
        json.JSONDecodeError,
        OSError,
        StopIteration
    ) as error:

        recovery_screen(error)

        return collection_module.collection
