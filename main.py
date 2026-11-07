
from sprites import ALL_SPRITES

from collection import (
    STATUSES,
    collection,
    display_collection,
    add_sprite,
    update_status,
    record_trade,
    remove_sprite,
    reset_collection,
    find_owned
)

from backup import initialize_collection


# --------------------------------------------------
# APPLICATION INFORMATION
# --------------------------------------------------

APP_NAME = "Sprite Trade Manager"
APP_VERSION = "1.1.0"
SUPPORTED_SEASON = "C7S5"


# --------------------------------------------------
# SELECTION HELPERS
# --------------------------------------------------

def choose_sprite():
    """Display all Sprites and let the user select one."""

    print("\nAvailable Sprites:")

    for index, sprite in enumerate(ALL_SPRITES, start=1):
        print(f"{index}. {sprite.name}")

    print("0. Cancel")

    while True:
        choice = input("\nSelect a Sprite: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice = int(choice)

        if choice == 0:
            return None

        if 1 <= choice <= len(ALL_SPRITES):
            return ALL_SPRITES[choice - 1]

        print("Invalid selection.")


def choose_variant(sprite):
    """Display available variants for a selected Sprite."""

    available = [
        variant for variant in sprite.variants
        if variant.status == "Available"
    ]

    if not available:
        print("No available variants for this Sprite.")
        return None

    print(f"\n{sprite.name} Variants:")

    for index, variant in enumerate(available, start=1):
        print(f"{index}. {variant.name}")

    print("0. Cancel")

    while True:
        choice = input("\nSelect a variant: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice = int(choice)

        if choice == 0:
            return None

        if 1 <= choice <= len(available):
            return available[choice - 1]

        print("Invalid selection.")


def choose_status():
    """Let the user select a mastery status."""

    print("\nMastery Status:")

    for index, status in enumerate(STATUSES, start=1):
        print(f"{index}. {status}")

    print("0. Cancel")

    while True:
        choice = input("\nSelect a status: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice = int(choice)

        if choice == 0:
            return None

        if 1 <= choice <= len(STATUSES):
            return STATUSES[choice - 1]

        print("Invalid selection.")


def choose_owned_variant():
    """Display owned variants grouped by Sprite."""

    owned_variants = []

    print("\nOwned Sprite Variants:")

    index = 1

    for sprite in ALL_SPRITES:

        sprite_entries = []

        for variant in sprite.variants:
            entry = find_owned(sprite.name, variant.name)

            if entry is not None:
                sprite_entries.append((variant, entry))

        if not sprite_entries:
            continue

        print(f"\n{sprite.name}:")

        for variant, entry in sprite_entries:

            print(
                f"{index}. {variant.name} "
                f"({entry['status']})"
            )

            owned_variants.append(
                (sprite.name, variant.name)
            )

            index += 1

    if not owned_variants:
        print("You don't own any Sprite variants.")
        return None

    print("0. Cancel")

    while True:
        choice = input("\nSelect an owned variant: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice = int(choice)

        if choice == 0:
            return None

        if 1 <= choice <= len(owned_variants):
            return owned_variants[choice - 1]

        print("Invalid selection.")


# --------------------------------------------------
# COLLECTION ACTIONS
# --------------------------------------------------

def add_to_collection():
    """Add a Sprite variant to the collection."""

    sprite = choose_sprite()

    if sprite is None:
        return

    variant = choose_variant(sprite)

    if variant is None:
        return

    status = choose_status()

    if status is None:
        return

    add_sprite(sprite.name, variant.name, status)


def change_mastery():
    """Update the mastery status of an owned variant."""

    selected = choose_owned_variant()

    if selected is None:
        return

    sprite_name, variant_name = selected

    status = choose_status()

    if status is None:
        return

    update_status(sprite_name, variant_name, status)


def trade_sprite():
    """Record a trade involving an owned variant."""

    selected = choose_owned_variant()

    if selected is None:
        return

    sprite_name, variant_name = selected

    record_trade(sprite_name, variant_name)


def delete_sprite():
    """Remove an owned variant from the collection."""

    selected = choose_owned_variant()

    if selected is None:
        return

    sprite_name, variant_name = selected

    remove_sprite(sprite_name, variant_name)


def clear_collection():
    """Reset the entire collection after confirmation."""

    print("\nWARNING: This will remove every owned Sprite variant.")

    confirmation = input(
        "Are you sure you want to reset your collection? (y/n): "
    ).strip().lower()

    if confirmation == "y":
        reset_collection()

    elif confirmation == "n":
        print("Collection reset cancelled.")

    else:
        print("Invalid confirmation. Collection was not reset.")


# --------------------------------------------------
# MAIN MENU
# --------------------------------------------------

def display_menu():
    """Display the main application menu."""

    print("\n" + "=" * 40)
    print("                MAIN MENU")
    print("=" * 40)

    print("1. Display Collection")
    print("2. Add Sprite")
    print("3. Update Mastery")
    print("4. Record Trade")
    print("5. Remove Sprite")
    print("6. Reset Collection")
    print("7. Exit")


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

def main():
    """Start Sprite Trade Manager."""

    # Initialize collection and handle save recovery.
    initialize_collection()

    # Display application information.
    print("\n" + "=" * 60)
    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"Supporting Fortnite {SUPPORTED_SEASON}")
    print("=" * 60)

    # Main application loop.
    while True:

        display_menu()

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            display_collection()

        elif choice == "2":
            add_to_collection()

        elif choice == "3":
            change_mastery()

        elif choice == "4":
            trade_sprite()

        elif choice == "5":
            delete_sprite()

        elif choice == "6":
            clear_collection()

        elif choice == "7":
            print("\nThank you for using Sprite Trade Manager!")
            print("Goodbye!")
            break

        else:
            print("\nInvalid selection. Please choose 1-7.")


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
