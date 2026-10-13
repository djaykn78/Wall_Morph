import os
from design_database import (
    get_designs, 
    get_wall_colours, 
    get_wallpapers, 
    get_textures
)

def run_tests():
    print("\n==================================================")
    print(" 🧪 TESTING PERSON 1 MODULE: DESIGN DATABASE")
    print("==================================================\n")

    # 1. Gather all object image assets
    all_assets = []
    categories = ["door", "window", "bookshelf", "table", "light", "switchboard", "decoration"]
    
    print("--- Loading Image Assets ---")
    for category in categories:
        items = get_designs(category)
        print(f" Loaded {len(items):02d} {category}(s)")
        all_assets.extend(items)
    
    # Gather wallpapers and textures
    wallpapers = get_wallpapers()
    textures = get_textures()
    all_assets.extend(wallpapers)
    all_assets.extend(textures)
    
    print(f" Loaded {len(wallpapers):02d} wallpapers")
    print(f" Loaded {len(textures):02d} textures")

    # 2. Test the File Paths
    print("\n--- Testing File Paths on Your Machine ---")
    missing_files = 0
    for asset in all_assets:
        if not os.path.exists(asset["path"]):
            print(f" ⚠ MISSING FILE: {asset['path']}")
            missing_files += 1

    if missing_files == 0:
        print(" ✅ All image file paths are valid!")

    # 3. Test the Solid RGB Wall Colors
    print("\n--- Testing Solid RGB Wall Colors ---")
    colors = get_wall_colours()
    invalid_colors = 0
    
    for color_name, rgb in colors.items():
        # Validate that the RGB is exactly 3 numbers, all between 0 and 255
        if len(rgb) != 3 or not all(0 <= val <= 255 for val in rgb):
            print(f" ⚠ INVALID RGB FOR '{color_name}': {rgb} (Must be 0-255)")
            invalid_colors += 1
            
    if invalid_colors == 0:
        print(f" ✅ All {len(colors)} RGB colors are mathematically correct!")

    # 4. Final Results
    print("\n==================================================")
    if missing_files == 0 and invalid_colors == 0:
        print(" 🎉 SUCCESS! Project is 100% ready for hand-off.")
        print(" Your asset maps and RGB color codes are perfect.")
    else:
        print(f" ❌ FAILED: {missing_files} missing files, {invalid_colors} invalid colors.")
        print(" Review the errors printed above before handing off.")
    print("==================================================\n")

if __name__ == "__main__":
    run_tests()