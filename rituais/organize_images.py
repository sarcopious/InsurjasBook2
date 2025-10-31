
import os
import shutil
import re
import unicodedata

def normalize_for_comparison(text):
    # Remove parenthesized element names, e.g., " (Sangue)"
    text = re.sub(r'\s*\((Conhecimento|Energia|Morte|Sangue)\)\s*$', '', text, flags=re.IGNORECASE)
    # Normalize accents, convert to lower case, and remove non-alphanumeric characters
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-zA-Z0-9]+', '', text).lower()
    return text

def organize_images():
    rituais_dir = os.path.abspath("c:\\Insurjas\\Diagramação\\ReactPDF\\output\\rituais")
    
    ritual_to_circle_map = {} # {normalized_ritual_name: (circle_name, ritual_type_folder)}

    # 1. Parse all markdown files to build a map of rituals to their circles.
    for md_filename in os.listdir(rituais_dir):
        if not md_filename.endswith(".md"):
            continue

        ritual_type_folder_name = os.path.splitext(md_filename)[0]
        md_filepath = os.path.join(rituais_dir, md_filename)

        with open(md_filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_circle = None
        for i, line in enumerate(lines):
            circle_match = re.match(r"^\s*###\s*(\d+º Círculo)\s*$", line)
            if circle_match:
                current_circle = circle_match.group(1).replace("º", " Circulo")
                continue

            ritual_match = re.match(r"^\s*(?:###|#)\s*(.+)\s*$", line)
            if ritual_match:
                ritual_name = ritual_match.group(1).strip()
                
                # Handle Varia case
                effective_circle = current_circle
                if "Varia" in ritual_type_folder_name:
                     for j in range(i + 1, min(i + 5, len(lines))):
                        varia_match = re.search(r"\*\*(VARIA \d+)\*\*", lines[j])
                        if varia_match:
                            effective_circle = varia_match.group(1)
                            break
                
                if effective_circle:
                    normalized_ritual_name = normalize_for_comparison(ritual_name)
                    ritual_to_circle_map[normalized_ritual_name] = (effective_circle, ritual_type_folder_name)

    # 2. Find all images and move them to the correct circle folder.
    search_locations = [os.path.join(rituais_dir, "rituaismisturados")]
    for item in os.listdir(rituais_dir):
        path = os.path.join(rituais_dir, item)
        if os.path.isdir(path) and item.startswith("Rituais de"):
            search_locations.append(path)

    for location in search_locations:
        if not os.path.isdir(location):
            continue
            
        for filename in os.listdir(location):
            if not filename.lower().endswith('.png'):
                continue

            # Ensure we are processing a file
            if not os.path.isfile(os.path.join(location, filename)):
                continue

            image_name_without_ext = os.path.splitext(filename)[0]
            normalized_image_name = normalize_for_comparison(image_name_without_ext)

            if normalized_image_name in ritual_to_circle_map:
                circle_name, ritual_type_folder = ritual_to_circle_map[normalized_image_name]
                
                destination_folder = os.path.join(rituais_dir, ritual_type_folder, circle_name)
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                
                old_path = os.path.join(location, filename)
                new_path = os.path.join(destination_folder, filename)

                if old_path != new_path and os.path.exists(old_path):
                    shutil.move(old_path, new_path)
                    print(f"Moved {filename} to {os.path.join(ritual_type_folder, circle_name)}")

if __name__ == "__main__":
    organize_images()