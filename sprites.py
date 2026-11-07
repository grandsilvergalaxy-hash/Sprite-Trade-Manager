
# ==========================================
# Sprite Database
# ==========================================

class SpriteVariant:
    def __init__(self, name, status="Available"):
        self.name = name
        self.status = status

    def __str__(self):
        if self.status == "Available":
            return self.name

        return f"{self.name} ({self.status})"


# ==========================================
# Base Sprite Class
# ==========================================

class Sprite:
    max_level = 5

    def __init__(self, name, role, effect, variants=None):
        self.name = name
        self.role = role
        self.effect = effect
        self.variants = variants if variants is not None else []

    def display_info(self):
        print(f"\nName: {self.name}")
        print(f"Rarity: {self.rarity}")
        print(f"Role: {self.role}")
        print(f"Effect: {self.effect}")
        print(f"Max Level: {self.max_level}")

        print("Variants:")
        for variant in self.variants:
            print(f" - {variant}")


# ==========================================
# Rarity Classes
# ==========================================

class RareSprite(Sprite):
    rarity = "Rare"


class EpicSprite(Sprite):
    rarity = "Epic"


class LegendarySprite(Sprite):
    rarity = "Legendary"


class MythicSprite(Sprite):
    rarity = "Mythic"


# ==========================================
# Variant Definitions
# ==========================================

def standard_variants():
    return [
        SpriteVariant("Base"),
        SpriteVariant("Fortune"),
        SpriteVariant("Cursed", status="Coming Soon")
    ]


def base_only():
    return [
        SpriteVariant("Base")
    ]


def uzi_variants():
    return [
        SpriteVariant("Base", status="Coming Soon"),
        SpriteVariant("Fortune", status="Coming Soon"),
        SpriteVariant("Cursed", status="Coming Soon")
    ]


# ==========================================
# Rare Sprites
# ==========================================

halfpeeld = RareSprite(
    "Halfpeel'd",
    "Tracking fights",
    "Marks eliminations on the map, with a wider radius per level.",
    standard_variants()
)

re_pete = RareSprite(
    "Re-Pete",
    "Sustained fights",
    "Faster reloads, with a chance that a reload refunds ammo.",
    standard_variants()
)

barry_ofish = RareSprite(
    "Barry O'Fish",
    "Water rotations",
    "Reduces tactical sprint stamina drain in water. Grants Slap at max level.",
    standard_variants()
)

wayfinder = RareSprite(
    "Wayfinder",
    "Collectors",
    "Reveals nearby Sprites and provides more items from Buried Chests.",
    standard_variants()
)


# ==========================================
# Epic Sprites
# ==========================================

chester = EpicSprite(
    "Chester",
    "Looting",
    "Chance of extra Treasure Chest loot. Also prevents fall damage.",
    standard_variants()
)

exmarks = EpicSprite(
    "Exmarks",
    "Sprite hunting",
    "Reveals Treasure Maps and Wanted Posters. Spawns a Treasure Map at max level.",
    standard_variants()
)

kelper = EpicSprite(
    "Kelper",
    "Sustain near water",
    "Restores health over time while in water, with more healing per level.",
    standard_variants()
)

lil_squibbly = EpicSprite(
    "Lil' Squibbly",
    "Fishing",
    "Jumping into a fishing hole fishes it, with bonus loot.",
    standard_variants()
)


# ==========================================
# Legendary Sprites
# ==========================================

lil_flacko = LegendarySprite(
    "Lil' Flacko",
    "Landing on squads",
    "Landing creates a shockwave that knocks enemies back.",
    standard_variants()
)

lil_uzi_vert_jr = LegendarySprite(
    "Lil' Uzi Vert Jr.",
    "Shield-heavy players",
    "Restoring shields creates a Chug Splash effect.",
    uzi_variants()
)

transponder_snail = LegendarySprite(
    "Transponder Snail",
    "Squads and building",
    "Provides extra resources from pickups, shared with equipped teammates.",
    base_only()
)


# ==========================================
# Mythic Sprites
# ==========================================

sweet_dreams = MythicSprite(
    "Sweet Dreams",
    "Loot",
    "Provides a random item at every level and Mythic loot at max level.",
    base_only()
)

plundarrgh = MythicSprite(
    "Plundarrgh",
    "Aggressive looting",
    "Opening a chest boosts pickaxe and movement speed.",
    standard_variants()
)


# ==========================================
# Master Sprite Database
# ==========================================

ALL_SPRITES = [
    halfpeeld,
    re_pete,
    barry_ofish,
    wayfinder,

    chester,
    exmarks,
    kelper,
    lil_squibbly,

    lil_flacko,
    lil_uzi_vert_jr,
    transponder_snail,

    sweet_dreams,
    plundarrgh
]


# ==========================================
# Sprite Lookup and Validation
# ==========================================

def normalize_name(name):
    """Normalize names for case-insensitive lookup."""

    return (
        name.strip()
        .casefold()
        .replace("'", "")
        .replace("’", "")
    )


# Dictionary for fast Sprite lookups
SPRITE_DATABASE = {
    normalize_name(sprite.name): sprite
    for sprite in ALL_SPRITES
}


def get_sprite(name):
    """Find a Sprite by name. Returns None if not found."""

    return SPRITE_DATABASE.get(normalize_name(name))


def list_sprites():
    """Display every Sprite in the database."""

    for sprite in ALL_SPRITES:
        print(f"{sprite.name} - {sprite.rarity}")


def count_sprites():
    """Count Sprites by rarity."""

    rarity_counts = {}

    for sprite in ALL_SPRITES:
        rarity_counts[sprite.rarity] = rarity_counts.get(sprite.rarity, 0) + 1

    return rarity_counts


# ==========================================
# Test the Database
# ==========================================

if __name__ == "__main__":

    print("SPRITE DATABASE")
    print("================")

    list_sprites()

    print("\nSPRITE COUNTS")
    print("================")

    for rarity, count in count_sprites().items():
        print(f"{rarity}: {count}")

    print(f"\nTotal Sprites: {len(ALL_SPRITES)}")

    # Test name lookup
    print("\nLOOKUP TEST")
    print("================")

    sprite = get_sprite("Lil Flacko")

    if sprite:
        sprite.display_info()
    else:
        print("Sprite not found.")
