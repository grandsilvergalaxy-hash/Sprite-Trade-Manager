
# ==========================================
# Sprite Database
# ==========================================

SPRITE_DATABASE_VERSION = 3


# ==========================================
# Variant Ability Definitions
# ==========================================

BASE_ABILITY = "None"

FORTUNE_ABILITY = "Reveals nearby chests"

CURSED_ABILITY = (
    "Increases chance of rare Sprite variants, "
    "water damages you."
)


# ==========================================
# Sprite Variant Class
# ==========================================

class SpriteVariant:
    def __init__(self, number, name, ability=BASE_ABILITY,
                 status="Available"):

        self.number = number
        self.name = name
        self.ability = ability
        self.status = status

    @property
    def display_name(self):
        """Return the complete variant name."""
        if self.name == "Base":
            return self.sprite_name

        return f"{self.name} {self.sprite_name}"

    def __str__(self):
        return f"{self.number}. {self.display_name}"


# ==========================================
# Variant Definitions
# ==========================================

def standard_variants(base_number):
    """Return Base, Fortune, and Cursed variants."""

    return [
        SpriteVariant(
            base_number,
            "Base"
        ),
        SpriteVariant(
            base_number + 1,
            "Fortune",
            FORTUNE_ABILITY
        ),
        SpriteVariant(
            base_number + 2,
            "Cursed",
            CURSED_ABILITY
        ),
    ]


def base_only(base_number):
    """Return only the Base variant."""

    return [
        SpriteVariant(
            base_number,
            "Base"
        )
    ]


# ==========================================
# Base Sprite Class
# ==========================================

class Sprite:
    max_level = 5

    def __init__(self, name, rarity, role, effect,
                 base_number, variants=None):

        self.name = name
        self.rarity = rarity
        self.role = role
        self.effect = effect

        # Standard variants are assigned automatically.
        # Individual Sprites can override this when necessary.
        self.variants = (
            variants
            if variants is not None
            else standard_variants(base_number)
        )

        # Connect each variant to its parent Sprite.
        for variant in self.variants:
            variant.sprite_name = self.name
            variant.sprite = self


# ==========================================
# Rarity Classes
# ==========================================

class RareSprite(Sprite):

    def __init__(self, name, role, effect, base_number,
                 variants=None):

        super().__init__(
            name, "Rare", role, effect, base_number, variants
        )


class EpicSprite(Sprite):

    def __init__(self, name, role, effect, base_number,
                 variants=None):

        super().__init__(
            name, "Epic", role, effect, base_number, variants
        )


class LegendarySprite(Sprite):

    def __init__(self, name, role, effect, base_number,
                 variants=None):

        super().__init__(
            name, "Legendary", role, effect, base_number, variants
        )


class MythicSprite(Sprite):

    def __init__(self, name, role, effect, base_number,
                 variants=None):

        super().__init__(
            name, "Mythic", role, effect, base_number, variants
        )


# ==========================================
# Rare Sprites
# ==========================================

halfpeeld = RareSprite(
    "Halfpeel'd",
    "Tracking fights",
    "Marks eliminations on the map, with a wider radius per level.",
    1
)

re_pete = RareSprite(
    "Re-Pete",
    "Sustained fights",
    "Faster reloads, with a chance that a reload refunds ammo.",
    5
)

barry_ofish = RareSprite(
    "Barry O'Fish",
    "Water rotations",
    "Reduces tactical sprint stamina drain in water. Grants Slap at max level.",
    9
)

wayfinder = RareSprite(
    "Wayfinder",
    "Collectors",
    "Reveals nearby Sprites and provides more items from Buried Chests.",
    13
)


# ==========================================
# Epic Sprites
# ==========================================

chester = EpicSprite(
    "Chester",
    "Looting",
    "Chance of extra Treasure Chest loot. Also prevents fall damage.",
    17
)

kelper = EpicSprite(
    "Kelper",
    "Sustain near water",
    "Restores health over time while in water, with more healing per level.",
    21
)

exmarks = EpicSprite(
    "Exmarks",
    "Sprite hunting",
    "Reveals Treasure Maps and Wanted Posters. Spawns a Treasure Map at max level.",
    25
)

lil_squibbly = EpicSprite(
    "Lil' Squibbly",
    "Fishing",
    "Jumping into a fishing hole fishes it, with bonus loot.",
    29
)


# ==========================================
# Mythic Sprites
# ==========================================

sweet_dreams = MythicSprite(
    "Sweet Dreams",
    "Loot",
    "Provides a random item at every level and Mythic loot at max level.",
    33,
    variants=base_only(33)
)


# ==========================================
# Legendary Sprites
# ==========================================

lil_flacko = LegendarySprite(
    "Lil' Flacko",
    "Landing on squads",
    "Landing creates a shockwave that knocks enemies back.",
    37
)

lil_uzi_vert_jr = LegendarySprite(
    "Lil' Uzi Vert Jr.",
    "Shield-heavy players",
    "Restoring shields creates a Chug Splash effect.",
    41
)

plundarrgh = MythicSprite(
    "Plundarrgh",
    "Aggressive looting",
    "Opening a chest boosts pickaxe and movement speed.",
    49
)

transponder_snail = LegendarySprite(
    "Transponder Snail",
    "Squads and building",
    "Provides extra resources from pickups, shared with equipped teammates.",
    57,
    variants=base_only(57)
)


# ==========================================
# Sprite Database List
# ==========================================

ALL_SPRITES = [
    halfpeeld,
    re_pete,
    barry_ofish,
    wayfinder,

    chester,
    kelper,
    exmarks,
    lil_squibbly,

    sweet_dreams,

    lil_flacko,
    lil_uzi_vert_jr,
    plundarrgh,

    transponder_snail,
]


# ==========================================
# Numbered Variant Database
# ==========================================

ALL_VARIANTS = [
    variant
    for sprite in ALL_SPRITES
    for variant in sprite.variants
]

VARIANT_DATABASE = {
    variant.number: variant
    for variant in ALL_VARIANTS
}


# ==========================================
# Database Lookup Functions
# ==========================================

def get_variant(number):
    """Find a variant using its permanent catalog number."""

    return VARIANT_DATABASE.get(number)


def list_variants():
    """Return all cataloged variants in number order."""

    return sorted(
        ALL_VARIANTS,
        key=lambda variant: variant.number
    )


def list_sprites():
    """Return all Sprites in database order."""

    return ALL_SPRITES.copy()


# ==========================================
# Database Counting
# ==========================================

def count_sprites():
    """Return the total number of Sprites."""

    return len(ALL_SPRITES)


def count_variants():
    """Return the total number of cataloged variants."""

    return len(ALL_VARIANTS)


def count_available_variants():
    """Return the number of available variants."""

    return sum(
        1
        for variant in ALL_VARIANTS
        if variant.status == "Available"
    )


# ==========================================
# Collection Lookup
# ==========================================

def get_collection_entry(collection_data, sprite, variant):
    """
    Find a user's collection entry for a specific variant.

    Supports the collection dictionary format:

    {
        "owned": [
            {
                "name": "Chester",
                "variant": "Fortune",
                "status": "Level 5",
                "first_edition": True,
                "won_match": False
            }
        ]
    }
    """

    if collection_data is None:
        return None

    if isinstance(collection_data, dict):
        collection_data = collection_data.get("owned", [])

    if not isinstance(collection_data, list):
        return None

    for entry in collection_data:

        if not isinstance(entry, dict):
            continue

        if (
            entry.get("name") == sprite.name
            and entry.get("variant") == variant.name
        ):
            return entry

    return None


# ==========================================
# Sprite Variant Display
# ==========================================

def display_variant_info(variant, collection_data=None):
    """
    Display Sprite details, selected variant ability,
    and personal collection information.
    """

    if variant is None:
        print("Invalid Sprite number.")
        return

    sprite = variant.sprite

    print("\n========== Sprite Database ==========\n")

    print(f"{variant.number}. {variant.display_name}")
    print()
    print(f"Rarity: {sprite.rarity}")
    print(f"Role: {sprite.role}")
    print(f"Effect: {sprite.effect}")
    print(f"Max Level: {sprite.max_level}")
    print(f"Ability: {variant.ability}")

    print("\n========== Personal Collection ==========\n")

    entry = get_collection_entry(
        collection_data,
        sprite,
        variant
    )

    if entry is None:
        print("Sprite is not owned.")

    else:
        status = entry.get("status", "Unmastered")

        previously_level_5 = status in ("Mastered", "Level 5")

        first_edition = entry.get("first_edition", False)
        won_match = entry.get("won_match", False)

        print("Ownership: Owned")
        print(f"Mastery: {status}")
        print(
            f"Previously Level 5: "
            f"{'Yes' if previously_level_5 else 'No'}"
        )
        print(f"First Edition (FE): {'Yes' if first_edition else 'No'}")
        print(f"Won Match (WM): {'Yes' if won_match else 'No'}")

    print("\n========================================")


# ==========================================
# Full Sprite Display
# ==========================================

def display_sprite_info(sprite, collection_data=None):
    """Display all variant information for a Sprite."""

    if sprite is None:
        print("Sprite not found.")
        return

    print("\n========== Sprite Information ==========\n")

    print(f"Name: {sprite.name}")
    print(f"Rarity: {sprite.rarity}")
    print(f"Role: {sprite.role}")
    print(f"Effect: {sprite.effect}")
    print(f"Max Level: {sprite.max_level}")

    print("\nVariants:")

    for variant in sprite.variants:
        print(
            f"{variant.number}. {variant.display_name}"
        )
        print(f"   Ability: {variant.ability}")

        entry = get_collection_entry(
            collection_data,
            sprite,
            variant
        )

        if entry is None:
            print("   Sprite is not owned.")

        else:
            status = entry.get("status", "Unmastered")

            previously_level_5 = status in ("Mastered", "Level 5")

            print("   Ownership: Owned")
            print(f"   Mastery: {status}")
            print(
                f"   Previously Level 5: "
                f"{'Yes' if previously_level_5 else 'No'}"
            )
            print(
                f"   FE: {'Yes' if entry.get('first_edition', False) else 'No'}"
            )
            print(
                f"   WM: {'Yes' if entry.get('won_match', False) else 'No'}"
            )

    print("\n========================================")
