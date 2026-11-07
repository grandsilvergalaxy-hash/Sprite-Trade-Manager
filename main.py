
from sprites import ALL_SPRITES

from collection import (
    STATUSES,
    collection,
    display_collection,
    add_sprite,
    update_status,
    record_trade,
    remove_sprite,
    reset_collection
)


# ============================================================
# SELECTION HELPERS
# ============================================================

def choose_sprite():
    """Let the user select a Sprite."""

    print("\nAVAILABLE SPRITES")
    print("=================")

    for index, sprite in enumerate(ALL_SPRITES, start=1):
        print(f"{index}. {sprite.name}")

    print("0. Cancel")

    choice = input("\nSelect a Sprite: ")

    if choice == "0":
        return None

    try:
        index = int(choice) - 1

        if index < 0 or index >= len(ALL_SPRITES):
            print("Invalid selection.")
            return None

        return ALL_SPRITES[index]

    except ValueError:
        print("Please enter a number.")
        return None


def choose_variant(sprite):
    """Let the user select an available variant."""

    variants = [
        variant for variant in sprite.variants
        if variant.status == "Available"
    ]

    print(f"\n{sprite.name.upper()} VARIANTS")
    print("========================")

    if not variants:
        print("No available variants.")
        return None

    for index, variant in enumerate(variants, start=1):
        print(f"{index}. {variant.name}")

    print("0. Cancel")

    choice = input("\nSelect a variant: ")

    if choice == "0":
        return None

    try:
        index = int(choice) - 1

        if index < 0 or index >= len(variants):
            print("Invalid selection.")
            return None

        return variants[index]

    except ValueError:
        print("Please enter a number.")
        return None


def choose_status():
    """Let the user select a mastery status."""

    print("\nMASTERY STATUS")
    print("==============")

    for index, status in enumerate(STATUSES, start=1):
        print(f"{index}. {status}")

    print("0. Cancel")

    choice = input("\nSelect a status: ")

    if choice == "0":
        return None

    try:
        index = int(choice) - 1

        if index < 0 or index >= len(STATUSES):
            print("Invalid selection.")
            return None

        return STATUSES[index]

    except ValueError:
        print("Please enter a number.")
        return None


def choose_owned_variant():
    """Let the user select an owned variant, grouped by Sprite."""

    owned = collection["owned"]

    print("\nYOUR OWNED SPRITES")
    print("==================")

    if not owned:
        print("Your collection is empty.")
        return None

    # Organize owned variants using the master Sprite database.
    organized = []

    for sprite in ALL_SPRITES:
        for variant in sprite.variants:

            if variant.status != "Available":
                continue

            for entry in owned:

                if (
                    entry["name"] == sprite.name
                    and entry["variant"] == variant.name
                ):
                    organized.append(entry)

    # Display the organized collection.
    for index, entry in enumerate(organized, start=1):
        print(
            f"{index}. {entry['name']} "
            f"({entry['variant']}) - {entry['status']}"
        )

    print("0. Cancel")

    choice = input("\nSelect an owned Sprite: ")

    if choice == "0":
        return None

    try:
        index = int(choice) - 1

        if index < 0 or index >= len(organized):
            print("Invalid selection.")
            return None

        return organized[index]

    except ValueError:
        print("Please enter a number.")
        return None
# ============================================================
# COLLECTION ACTIONS
# ============================================================

def add_to_collection():
    """Add a new Sprite variant."""

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
    """Update an owned Sprite's mastery status."""

    entry = choose_owned_variant()

    if entry is None:
        return

    status = choose_status()

    if status is None:
        return

    update_status(
        entry["name"],
        entry["variant"],
        status
    )


def trade_sprite():
    """Record a trade involving an owned Sprite."""

    entry = choose_owned_variant()

    if entry is None:
        return

    record_trade(
        entry["name"],
        entry["variant"]
    )


def delete_sprite():
    """Remove a Sprite variant from the collection."""

    entry = choose_owned_variant()

    if entry is None:
        return

    confirm = input(
        f"\nRemove {entry['name']} ({entry['variant']})? (y/n): "
    ).strip().lower()

    if confirm == "y":
        remove_sprite(
            entry["name"],
            entry["variant"]
        )
    else:
        print("Removal cancelled.")


def clear_collection():
    """Reset the entire collection after confirmation."""

    print("\nWARNING: This will remove every owned Sprite!")

    confirm = input("Are you sure? (y/n): ").strip().lower()

    if confirm == "y":
        reset_collection()
    else:
        print("Reset cancelled.")


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        print("\nSPRITE COLLECTION MANAGER")
        print("=========================")

        print("1. Display Collection")
        print("2. Add Sprite")
        print("3. Update Mastery")
        print("4. Record Trade")
        print("5. Remove Sprite")
        print("6. Reset Collection")
        print("7. Exit")

        choice = input("\nChoose an option: ").strip()

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
            print("\nThanks for using Sprite Collection Manager!")
            break

        else:
            print("\nInvalid option. Please choose 1-7.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()