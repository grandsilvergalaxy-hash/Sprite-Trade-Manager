# ==========================================
# SPRITE TRADE MANAGER
# Version 1.3.0
# ==========================================

import backup
import collection
import sprites

# ==========================================
# DISPLAY SETTINGS
# ==========================================

APP_NAME = "SPRITE TRADE MANAGER"
APP_VERSION = "1.3.0"

LINE = "=" * 55
SHORT_LINE = "-" * 55


# ==========================================
# GENERAL INPUT FUNCTIONS
# ==========================================

def pause():
    input("\nPress Enter to continue...")


def get_number(prompt):
    """Request a valid whole number from the user."""

    while True:
        value = input(prompt).strip()

        try:
            return int(value)

        except ValueError:
            print("Please enter a valid number.")


def get_yes_no(prompt):
    """Request a Yes or No answer."""

    while True:
        answer = input(prompt).strip().lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print("Please enter Y or N.")


def print_header(title):
    print("\n" + LINE)
    print(f"{title:^55}")
    print(LINE)


# ==========================================
# CATALOG DISPLAY
# ==========================================

def display_catalog():
    """Print every available numbered Sprite variant."""

    print_header("SPRITE DATABASE")

    variants = sprites.list_variants()

    print(f"{sprites.count_sprites()} Sprites | "
          f"{sprites.count_variants()} Variants\n")

    for variant in variants:
        print(f"{variant.number:>3}  {variant.display_name}")

    print("\n" + SHORT_LINE)
    print("Enter a Sprite number to inspect it.")
    print("[0] Back")


# ==========================================
# SPRITE DATABASE
# ==========================================

def sprite_database_menu():
    """Browse the catalog and inspect individual variants."""

    while True:
        display_catalog()

        number = get_number("\nSprite number: ")

        if number == 0:
            return

        variant = sprites.get_variant(number)

        if variant is None:
            print("That number is not in the Sprite database.")
            pause()
            continue

        sprites.display_variant_info(
            variant,
            collection.collection
        )

        pause()


# ==========================================
# ADD SPRITE
# ==========================================

def add_sprite_menu():
    """Add a numbered Sprite variant to the collection."""

    while True:
        print_header("ADD SPRITE")

        print("1. Browse Sprite Database")
        print("2. Enter Sprite Number")
        print("0. Back")

        choice = get_number("\nSelection: ")

        if choice == 0:
            return

        if choice == 1:
            display_catalog()

        elif choice == 2:
            pass

        else:
            print("Invalid selection.")
            pause()
            continue

        number = get_number("\nSprite number (0 to cancel): ")

        if number == 0:
            continue

        variant = sprites.get_variant(number)

        if variant is None:
            print("Invalid Sprite number.")
            pause()
            continue

        if collection.is_owned(variant):
            print("You already own this Sprite variant.")
            pause()
            continue

        print(f"\nSelected: {variant.display_name}")

        print("\nMastery Status")
        print("1. Unmastered")
        print("2. Mastered")
        print("3. Level 5")

        status_choice = get_number("\nSelect mastery status: ")

        statuses = {
            1: "Unmastered",
            2: "Mastered",
            3: "Level 5",
        }

        if status_choice not in statuses:
            print("Invalid mastery status.")
            pause()
            continue

        first_edition = get_yes_no(
            "Is this a First Edition (FE)? (Y/N): "
        )

        won_match = get_yes_no(
            "Did you win a match with this Sprite (WM)? (Y/N): "
        )

        collection.add_sprite(
            variant,
            status=statuses[status_choice],
            first_edition=first_edition,
            won_match=won_match,
        )

        pause()


# ==========================================
# OWNED SPRITE SELECTION
# ==========================================

def select_owned_sprite():
    """Allow the user to select an owned Sprite by number."""

    if not collection.collection["owned"]:
        print("\nYour collection is empty.")
        return None

    print_header("YOUR OWNED SPRITES")

    for entry in sorted(
            collection.collection["owned"],
            key=lambda item: item["number"]
    ):
        print(
            f"{entry['number']:>3}  "
            f"{entry['name']} - {entry['variant']} "
            f"[{entry['status']}]"
        )

    print("\n[0] Back")

    number = get_number("\nEnter Sprite number: ")

    if number == 0:
        return None

    variant = sprites.get_variant(number)

    if variant is None or not collection.is_owned(variant):
        print("That Sprite is not in your collection.")
        pause()
        return None

    return variant


# ==========================================
# EDIT OWNED SPRITE
# ==========================================

def edit_mastery(variant):
    """Change the mastery status of an owned Sprite."""

    entry = collection.find_owned(variant)

    if entry is None:
        return

    print_header("EDIT MASTERY")

    print(f"Sprite: {variant.display_name}")
    print(f"Current Status: {entry['status']}")

    print("\n1. Unmastered")
    print("2. Mastered")
    print("3. Level 5")
    print("0. Back")

    choice = get_number("\nNew status: ")

    statuses = {
        1: "Unmastered",
        2: "Mastered",
        3: "Level 5",
    }

    if choice == 0:
        return

    if choice not in statuses:
        print("Invalid selection.")
        return

    collection.update_status(variant, statuses[choice])


def edit_first_edition(variant):
    """Toggle First Edition."""

    entry = collection.find_owned(variant)

    if entry is None:
        return

    current = entry["first_edition"]

    print(f"\nFirst Edition: {'Yes' if current else 'No'}")

    new_value = get_yes_no(
        "Set First Edition to Yes? (Y/N): "
    )

    collection.update_first_edition(variant, new_value)

    print("First Edition updated.")


def edit_won_match(variant):
    """Toggle Won Match."""

    entry = collection.find_owned(variant)

    if entry is None:
        return

    current = entry["won_match"]

    print(f"\nWon Match: {'Yes' if current else 'No'}")

    new_value = get_yes_no(
        "Set Won Match to Yes? (Y/N): "
    )

    collection.update_won_match(variant, new_value)

    print("Won Match updated.")


def edit_sprite_menu():
    """Choose an owned Sprite and edit its attributes."""

    while True:
        print_header("EDIT OWNED SPRITE")

        variant = select_owned_sprite()

        if variant is None:
            return

        while True:
            entry = collection.find_owned(variant)

            print_header("SPRITE ATTRIBUTES")

            print(f"Sprite: {variant.display_name}")
            print(f"Mastery: {entry['status']}")
            print(
                f"First Edition: "
                f"{'Yes' if entry['first_edition'] else 'No'}"
            )
            print(
                f"Won Match: "
                f"{'Yes' if entry['won_match'] else 'No'}"
            )

            print("\n1. Edit Mastery")
            print("2. Edit First Edition")
            print("3. Edit Won Match")
            print("4. Record Trade / Loss")
            print("0. Back")

            choice = get_number("\nSelection: ")

            if choice == 0:
                break

            elif choice == 1:
                edit_mastery(variant)

            elif choice == 2:
                edit_first_edition(variant)

            elif choice == 3:
                edit_won_match(variant)

            elif choice == 4:
                if get_yes_no(
                        "Record this Sprite as traded or lost? (Y/N): "
                ):
                    collection.record_trade(variant)

            else:
                print("Invalid selection.")

            pause()


# ==========================================
# COLLECTION
# ==========================================

def view_collection_menu():
    """Display the personal Sprite collection."""

    collection.display_collection()

    pause()

def collection_statistics_menu():
    """Display collection statistics."""

    stats = collection.get_collection_stats()

    print_header("COLLECTION STATISTICS")

    print(f"Total Owned:       {stats['total']}")
    print(f"Unmastered:        {stats['unmastered']}")
    print(f"Mastered:          {stats['mastered']}")
    print(f"Level 5:           {stats['level_5']}")

    print(SHORT_LINE)

    print(f"First Edition:     {stats['first_edition']}")
    print(f"Won Match:         {stats['won_match']}")

    print(SHORT_LINE)

    print(f"Database Sprites:  {sprites.count_sprites()}")
    print(f"Database Variants: {sprites.count_variants()}")

    pause()


# ==========================================
# TRADE ADVERTISEMENT
# ==========================================

def trade_ad_menu():
    """Generate and display the collection trade advertisement."""

    print_header("TRADE ADVERTISEMENT")

    collection.display_trade_ad()

    print("\nYou can copy the advertisement above.")

    pause()


# ==========================================
# REMOVE SPRITE
# ==========================================

def remove_sprite_menu():
    """Remove a Sprite record after confirmation."""

    print_header("REMOVE SPRITE")

    variant = select_owned_sprite()

    if variant is None:
        return

    if get_yes_no(
            f"Remove {variant.display_name} from your collection? (Y/N): "
    ):
        collection.remove_sprite(variant)

    pause()


# ==========================================
# RESET COLLECTION
# ==========================================

def reset_collection_menu():
    """Reset the entire collection after confirmation."""

    print_header("RESET COLLECTION")

    print("WARNING: This will remove every owned Sprite record.")

    if get_yes_no("\nAre you absolutely sure? (Y/N): "):
        if get_yes_no("Confirm collection reset? (Y/N): "):
            collection.reset_collection()

    pause()


# ==========================================
# MAIN MENU
# ==========================================

def display_main_menu():
    print_header(f"{APP_NAME} v{APP_VERSION}")

    print("\nCOLLECTION")
    print("1. View Collection")
    print("2. Add Sprite")
    print("3. Edit Owned Sprite")

    print("\nSPRITE DATABASE")
    print("4. Browse Sprite Database")

    print("\nTRADING")
    print("5. Create Trade Advertisement")

    print("\nMANAGEMENT")
    print("6. Collection Statistics")
    print("7. Remove Sprite")
    print("8. Reset Collection")

    print("\n0. Exit")

    print("\n" + LINE)


def main():
    print_header(f"{APP_NAME} v{APP_VERSION}")

    print("Initializing collection...")

    try:
        backup.initialize_collection()

        if not collection.load_collection():
            print("\nUnable to load your collection.")
            print("Please check your save file and backup.")
            return

    except Exception as error:
        print(f"\nStartup error: {error}")
        print("The application will now close.")
        return

    print("Collection loaded successfully!")

    pause()

    while True:

        display_main_menu()

        choice = get_number("Select an option: ")

        if choice == 0:
            print("\nThanks for using Sprite Trade Manager!")
            break

        elif choice == 1:
            view_collection_menu()

        elif choice == 2:
            add_sprite_menu()

        elif choice == 3:
            edit_sprite_menu()

        elif choice == 4:
            sprite_database_menu()

        elif choice == 5:
            trade_ad_menu()

        elif choice == 6:
            collection_statistics_menu()

        elif choice == 7:
            remove_sprite_menu()

        elif choice == 8:
            reset_collection_menu()

        else:
            print("Invalid selection.")
            pause()


# ==========================================
# PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
