# coding: utf-8
import os
import json
from PIL import Image  # Nécessite l'installation de Pillow (pip install Pillow)

def create_thumbnails(input_folder, output_folder, size=(300, 300)):
    """Crée des miniatures pour toutes les images dans le dossier d'entrée"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(os.path.join(input_folder, filename))
            img.thumbnail(size)
            img.save(os.path.join(output_folder, filename))
            print(f"Thumbnail created for {filename}")

def create_collection_json(image_folder, output_json, default_tags=None):
    """Crée un fichier JSON avec les métadonnées des figurines"""
    if default_tags is None:
        default_tags = []
    
    collection = []
    
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Ici vous pouvez extraire des informations du nom de fichier si vous avez une convention
            # Par exemple: "dragon_red_large.jpg" pourrait donner les tags ["dragon", "red", "large"]
            name = os.path.splitext(filename)[0]  # Nom sans extension
            
            figurine = {
                "id": len(collection) + 1,
                "name": name.replace("_", " ").title(),
                "thumbnail": f"images/thumbnails/{filename}",
                "fullImage": f"images/full/{filename}",
                "tags": default_tags.copy()  # À personnaliser pour chaque figurine
            }
            collection.append(figurine)
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({"figurines": collection}, f, indent=2, ensure_ascii=False)
    
    print(f"Created collection with {len(collection)} figurines")

# Exemple d'utilisation
if __name__ == "__main__":
    create_thumbnails("images/full", "images/thumbnails")
    create_collection_json("images/full", "data/collection.json", ["figurine", "3d"])