"""
PERSON 1: Design Database & Design Selection
Provides asset data for objects, wallpapers, textures, and solid RGB wall colors.
"""

DESIGNS = {
    "door": [
        {"id": "door_clasic_1", "name": "Classic Wooden Door 1", "path": "assets/doors/wooden_clasic_door_1.png"},
        {"id": "door_clasic_2", "name": "Classic Wooden Door 2", "path": "assets/doors/wooden_clasic_door_2.png"},
        {"id": "door_clasic_3", "name": "Classic Wooden Door 3", "path": "assets/doors/wooden_clasic_door_3.png"},
        {"id": "door_clasic_4", "name": "Classic Wooden Door 4", "path": "assets/doors/wooden_clasic_door_4.png"},
        {"id": "door_clasic_5", "name": "Classic Wooden Door 5", "path": "assets/doors/wooden_clasic_door_5.png"},
        {"id": "door_glass_1", "name": "Glass Wooden Door 1", "path": "assets/doors/wooden_glass_door_1.png"},
        {"id": "door_glass_2", "name": "Glass Wooden Door 2", "path": "assets/doors/wooden_glass_door_2.png"},
        {"id": "door_glass_3", "name": "Glass Wooden Door 3", "path": "assets/doors/wooden_glass_door_3.png"},
        {"id": "door_modern_1", "name": "Modern Wooden Door 1", "path": "assets/doors/wooden_modern_door_1.png"},
        {"id": "door_modern_2", "name": "Modern Wooden Door 2", "path": "assets/doors/wooden_modern_door_2.png"},
        {"id": "door_modern_3", "name": "Modern Wooden Door 3", "path": "assets/doors/wooden_modern_door_3.png"},
        {"id": "door_modern_4", "name": "Modern Wooden Door 4", "path": "assets/doors/wooden_modern_door_4.png"}
    ],
    
    "air_conditioner": [
        {"id": "ac_modern_1", "name": "Modern Wall AC", "path": "assets/air_conditioners/air_conditioner_modern.png"},
        {"id": "ac_premium_1", "name": "Premium Wall AC", "path": "assets/air_conditioners/air_conditioner_premium.png"},
    ],
    "curtain": [
        {"id": "curtain_cream_1", "name": "Cream Curtain Pair", "path": "assets/curtains/curtain_cream_pair.png"},
        {"id": "curtain_slate_1", "name": "Slate Blue Curtain Pair", "path": "assets/curtains/curtain_slate_pair.png"},
    ],
    "window": [
        {"id": "win_interior_white", "name": "Interior White-Frame Window", "path": "assets/windows/window_interior_white.png"},
        {"id": "win_interior_wood", "name": "Interior Wood-Frame Window", "path": "assets/windows/window_interior_wood.png"},
    ],

    "bookshelf": [
        {"id": "shelf_wood_1", "name": "Wooden Book Shelf 1", "path": "assets/bookshelf/wooden_book_shelf_1.png"},
        {"id": "shelf_wood_2", "name": "Wooden Book Shelf 2", "path": "assets/bookshelf/wooden_book_shelf_2.png"},
        {"id": "shelf_wood_3", "name": "Wooden Book Shelf 3", "path": "assets/bookshelf/wooden_book_shelf_3.png"},
        {"id": "shelf_wood_4", "name": "Wooden Book Shelf 4", "path": "assets/bookshelf/wooden_book_shelf_4.png"},
        {"id": "shelf_min_1", "name": "Minimalist Book Shelf 1", "path": "assets/bookshelf/wooden_minimalist_book_shelf_1.png"},
        {"id": "shelf_min_2", "name": "Minimalist Book Shelf 2", "path": "assets/bookshelf/wooden_minimalist_book_shelf_2.png"},
        {"id": "shelf_min_3", "name": "Minimalist Book Shelf 3", "path": "assets/bookshelf/wooden_minimalist_book_shelf_3.png"},
        {"id": "shelf_mod_1", "name": "Modern Book Shelf 1", "path": "assets/bookshelf/wooden_modern_book_shelf_1.png"},
        {"id": "shelf_mod_2", "name": "Modern Book Shelf 2", "path": "assets/bookshelf/wooden_modern_book_shelf_2.png"},
        {"id": "shelf_mod_3", "name": "Modern Book Shelf 3", "path": "assets/bookshelf/wooden_modern_book_shelf_3.png"},
        {"id": "shelf_mod_4", "name": "Modern Book Shelf 4", "path": "assets/bookshelf/wooden_modern_book_shelf_4.png"},
        {"id": "shelf_mod_5", "name": "Modern Book Shelf 5", "path": "assets/bookshelf/wooden_modern_book_shelf_5.png"},
        {"id": "shelf_mod_6", "name": "Modern Book Shelf 6", "path": "assets/bookshelf/wooden_modern_book_shelf_6.png"},
        {"id": "shelf_mod_7", "name": "Modern Book Shelf 7", "path": "assets/bookshelf/wooden_modern_book_shelf_7.png"}
    ],

    "table": [
        {"id": "table_modern_1", "name": "Modern Table 1", "path": "assets/tables/table_modern_1.png"},
        {"id": "table_modern_2", "name": "Modern Table 2", "path": "assets/tables/table_modern_2.png"},
        {"id": "table_study_1", "name": "Wooden Study Table 1", "path": "assets/tables/wooden_study_table_1.png"},
        {"id": "table_study_2", "name": "Wooden Study Table 2", "path": "assets/tables/wooden_study_table_2.png"},
        {"id": "table_study_3", "name": "Wooden Study Table 3", "path": "assets/tables/wooden_study_table_3.png"},
        {"id": "table_wood_1", "name": "Wooden Table 1", "path": "assets/tables/wooden_table_1.png"},
        {"id": "table_wood_2", "name": "Wooden Table 2", "path": "assets/tables/wooden_table_2.png"},
        {"id": "table_wood_3", "name": "Wooden Table 3", "path": "assets/tables/wooden_table_3.png"},
        {"id": "table_wood_4", "name": "Wooden Table 4", "path": "assets/tables/wooden_table_4.png"},
        {"id": "table_wood_5", "name": "Wooden Table 5", "path": "assets/tables/wooden_table_5.png"},
        {"id": "table_wood_6", "name": "Wooden Table 6", "path": "assets/tables/wooden_table_6.png"},
        {"id": "table_wood_7", "name": "Wooden Table 7", "path": "assets/tables/wooden_table_7.png"}
    ],

    "light": [
        {"id": "light_ceiling_1", "name": "Ceiling Light 1", "path": "assets/lights/ceiling_light_1.png"},
        {"id": "light_ceiling_2", "name": "Ceiling Light 2", "path": "assets/lights/ceiling_light_2.png"},
        {"id": "light_ceiling_3", "name": "Ceiling Light 3", "path": "assets/lights/ceiling_light_3.png"},
        {"id": "light_modern_1", "name": "Modern Light 1", "path": "assets/lights/modern_light_1.png"},
        {"id": "light_modern_2", "name": "Modern Light 2", "path": "assets/lights/modern_light_2.png"},
        {"id": "light_wall_1", "name": "Wall Light 1", "path": "assets/lights/wall_light_1.png"},
        {"id": "light_wall_2", "name": "Wall Light 2", "path": "assets/lights/wall_light_2.png"},
        {"id": "light_wall_3", "name": "Wall Light 3", "path": "assets/lights/wall_light_3.png"}
    ],

    "switchboard": [
        {"id": "switch_black_1", "name": "Black Switchboard 1", "path": "assets/switchboards/switch_board_black_1.png"},
        {"id": "switch_black_2", "name": "Black Switchboard 2", "path": "assets/switchboards/switch_board_black_2.png"},
        {"id": "switch_black_3", "name": "Black Switchboard 3", "path": "assets/switchboards/switch_board_black_3.png"},
        {"id": "switch_modern_1", "name": "Modern Switchboard 1", "path": "assets/switchboards/switch_board_modern_1.png"},
        {"id": "switch_modern_2", "name": "Modern Switchboard 2", "path": "assets/switchboards/switch_board_modern_2.png"},
        {"id": "switch_white_1", "name": "White Switchboard 1", "path": "assets/switchboards/switch_board_white_1.png"},
        {"id": "switch_white_2", "name": "White Switchboard 2", "path": "assets/switchboards/switch_board_white_2.png"},
        {"id": "switch_white_3", "name": "White Switchboard 3", "path": "assets/switchboards/switch_board_white_3.png"}
    ],

    "decoration": [
        # Clocks (Changed to PNG)
        {"id": "decor_clock_1", "name": "Clock Decoration 1", "path": "assets/decorations/clock_decoration_1.png"},
        {"id": "decor_clock_2", "name": "Clock Decoration 2", "path": "assets/decorations/clock_decoration_2.png"},
        {"id": "decor_clock_3", "name": "Clock Decoration 3", "path": "assets/decorations/clock_decoration_3.png"},
        {"id": "decor_clock_4", "name": "Clock Decoration 4", "path": "assets/decorations/clock_decoration_4.png"},

        # Frames (PNG files)
        {"id": "decor_frame_1", "name": "Frame Decoration 1", "path": "assets/decorations/frame_decoration_1.png"},
        {"id": "decor_frame_2", "name": "Frame Decoration 2", "path": "assets/decorations/frame_decoration_2.png"},
        {"id": "decor_frame_3", "name": "Frame Decoration 3", "path": "assets/decorations/frame_decoration_3.png"},
        {"id": "decor_frame_4", "name": "Frame Decoration 4", "path": "assets/decorations/frame_decoration_4.png"},
        {"id": "decor_frame_5", "name": "Frame Decoration 5", "path": "assets/decorations/frame_decoration_5.png"},

        # Plants (PNG files)
        {"id": "decor_plant_1", "name": "Plant Decoration 1", "path": "assets/decorations/plant_decoration_1.png"},
        {"id": "decor_plant_2", "name": "Plant Decoration 2", "path": "assets/decorations/plant_decoration_2.png"},
        {"id": "decor_plant_3", "name": "Plant Decoration 3", "path": "assets/decorations/plant_decoration_3.png"},
        {"id": "decor_plant_4", "name": "Plant Decoration 4", "path": "assets/decorations/plant_decoration_4.png"},
        {"id": "decor_plant_5", "name": "Plant Decoration 5", "path": "assets/decorations/plant_decoration_5.png"}
    ]
}

# ---------------------------------------------------------
# SOLID WALL COLORS (RGB Math instead of image files)
# Format: "Color Name": (Red, Green, Blue)
# ---------------------------------------------------------
WALL_COLORS = {
    # Basic / Core Colors
    "Pure White": (255, 255, 255),
    "Pitch Black": (0, 0, 0),
    "Basic Red": (255, 0, 0),
    "Basic Green": (0, 255, 0),
    "Basic Blue": (0, 0, 255),
    "Basic Yellow": (255, 255, 0),
    "Basic Orange": (255, 165, 0),
    "Basic Purple": (128, 0, 128),

    # Neutrals & Earth Tones
    "Warm Beige": (245, 245, 220),
    "Cream": (255, 253, 208),
    "Ivory": (255, 255, 240),
    "Sand": (194, 178, 128),
    "Taupe": (72, 60, 50),
    "Terracotta": (226, 114, 91),
    "Light Grey": (211, 211, 211),
    "Dark Grey": (169, 169, 169),
    "Charcoal": (54, 69, 79),

    # Pastels & Soft Tones
    "Light Blue": (173, 216, 230),
    "Mint Green": (152, 255, 152),
    "Sage Green": (188, 198, 163),
    "Blush Pink": (255, 182, 193),
    "Lavender": (230, 230, 250),
    "Peach": (255, 218, 185),
    "Powder Blue": (176, 224, 230),

    # Advanced / Deep / Moody Tones
    "Navy Blue": (0, 0, 128),
    "Midnight Blue": (25, 25, 112),
    "Emerald Green": (80, 200, 120),
    "Forest Green": (34, 139, 34),
    "Olive Green": (128, 128, 0),
    "Teal": (0, 128, 128),
    "Maroon": (128, 0, 0),
    "Burgundy": (141, 2, 31),
    "Plum": (142, 69, 133),
    "Dusty Rose": (220, 164, 164),
    "Mustard Yellow": (255, 219, 88),
    "Indigo": (75, 0, 130)
}

# ---------------------------------------------------------
# WALLPAPERS & TEXTURES
# ---------------------------------------------------------
WALLPAPERS = [
    {"id": "wp_sage_botanical", "name": "Sage Botanical", "path": "assets/wallpapers/wallpaper_sage_botanical.png"},
    {"id": "wp_blush_floral", "name": "Blush Floral", "path": "assets/wallpapers/wallpaper_blush_floral.png"},
    {"id": "wp_navy_artdeco", "name": "Midnight Art Deco", "path": "assets/wallpapers/wallpaper_navy_artdeco.png"},
    {"id": "wp_linen_beige", "name": "Warm Linen", "path": "assets/wallpapers/wallpaper_linen_beige.png"},
    {"id": "wp_blue_geometry", "name": "Dusty Blue Geometry", "path": "assets/wallpapers/wallpaper_blue_geometry.png"},
    {"id": "wp_cream_pinstripe", "name": "Ivory Pinstripe", "path": "assets/wallpapers/wallpaper_cream_pinstripe.png"},
    {"id": "wp_terracotta_arch", "name": "Terracotta Arches", "path": "assets/wallpapers/wallpaper_terracotta_arch.png"},
    {"id": "wp_sage_waves", "name": "Soft Sage Waves", "path": "assets/wallpapers/wallpaper_sage_waves.png"},
    {"id": "wp_pattern_1", "name": "Classic Pattern 1", "path": "assets/wallpapers/wllpaper_pattern_1.png"},
    {"id": "wp_pattern_2", "name": "Classic Pattern 2", "path": "assets/wallpapers/wllpaper_pattern_2.png"},
    {"id": "wp_pattern_3", "name": "Classic Pattern 3", "path": "assets/wallpapers/wllpaper_pattern_3.png"}
]

TEXTURES = [
    {"id": "tex_brick_1", "name": "Brick Texture 1", "path": "assets/Textures/texture_brick_1.png"},
    {"id": "tex_brick_2", "name": "Brick Texture 2", "path": "assets/Textures/texture_brick_2.png"},
    {"id": "tex_stone_1", "name": "Stone Texture 1", "path": "assets/Textures/texture_stone_1.png"},
    {"id": "tex_stone_2", "name": "Stone Texture 2", "path": "assets/Textures/texture_stone_2.png"},
    {"id": "tex_stone_3", "name": "Stone Texture 3", "path": "assets/Textures/texture_stone_3.png"},
    {"id": "tex_wood_1", "name": "Wooden Texture 1", "path": "assets/Textures/texture_wooden_1.png"},
    {"id": "tex_wood_2", "name": "Wooden Texture 2", "path": "assets/Textures/texture_wooden_2.png"}
]

# ---------------------------------------------------------
# DATA RETRIEVAL FUNCTIONS (For Person 6 / Team Use)
# ---------------------------------------------------------

# Category aliases are deliberately separate from DESIGNS so detector labels
# can expand without requiring every category to have assets immediately.
TYPE_ALIASES = {
    "doors": "door", "windows": "window", "air conditioner": "air_conditioner", "ac": "air_conditioner", "air_conditioners": "air_conditioner", "bookshelves": "bookshelf",
    "shelves": "bookshelf", "tables": "table", "desks": "table",
    "lights": "light", "switchboards": "switchboard",
    "decorations": "decoration", "wardrobes": "wardrobe",
    "cupboard": "wardrobe", "cabinet": "wardrobe", "curtains": "curtain",
    "beds": "bed", "cots": "bed", "whiteboards": "whiteboard",
}


def normalize_object_type(object_type: str) -> str:
    """Normalize category names for consistent database lookups."""
    if not isinstance(object_type, str):
        return ""
    cleaned = "_".join(object_type.strip().lower().replace("-", " ").split())
    return TYPE_ALIASES.get(cleaned, cleaned)


def get_object_types(include_empty: bool = False) -> list:
    """Return known design categories; optionally include common detector-only types."""
    categories = set(DESIGNS)
    if include_empty:
        categories.update({"wardrobe", "curtain", "bed", "whiteboard", "air_conditioner"})
    return sorted(categories)


def get_designs(object_type: str) -> list:
    """Return designs for a category, or [] when it has no designs yet.

    Unknown categories are valid: detection/manual selection can support a new
    type before its replacement assets have been added.
    """
    return list(DESIGNS.get(normalize_object_type(object_type), []))


def get_design(object_id: str) -> dict:
    """Return one design by ID, or None if it is not registered."""
    for category in DESIGNS.values():
        for design in category:
            if design["id"] == object_id:
                return design
    return None


def register_design_category(object_type: str) -> str:
    """Create an empty design category and return its normalized key."""
    category = normalize_object_type(object_type)
    if not category:
        raise ValueError("object_type must be a non-empty string")
    DESIGNS.setdefault(category, [])
    return category


def add_design(object_type: str, design_id: str, name: str, path: str) -> dict:
    """Register a design asset under any category, including newly added types.

    This registers metadata only; ensure ``path`` points to an existing asset.
    Duplicate IDs are rejected to prevent ambiguous design selection.
    """
    category = register_design_category(object_type)
    if not isinstance(design_id, str) or not design_id.strip():
        raise ValueError("design_id must be a non-empty string")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    if not isinstance(path, str) or not path.strip():
        raise ValueError("path must be a non-empty string")
    if get_design(design_id) is not None:
        raise ValueError(f"Design ID already exists: {design_id}")
    item = {"id": design_id.strip(), "name": name.strip(), "path": path.strip()}
    DESIGNS[category].append(item)
    return dict(item)


def get_wall_colours() -> dict:
    """Return solid RGB wall colors."""
    return dict(WALL_COLORS)


def get_wallpapers() -> list:
    """Return wallpaper image assets."""
    return list(WALLPAPERS)


def get_textures() -> list:
    """Return texture image assets."""
    return list(TEXTURES)

# Robust asset resolution: works even when Streamlit is launched from another folder.
from pathlib import Path as _Path
_PROJECT_DIR = _Path(__file__).resolve().parent

def resolve_asset_path(path: str) -> str:
    """Resolve a database asset path relative to this project directory."""
    candidate = _Path(path)
    if candidate.is_absolute():
        return str(candidate)
    return str((_PROJECT_DIR / candidate).resolve())
