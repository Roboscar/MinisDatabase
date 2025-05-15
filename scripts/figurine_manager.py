import os
import sys
import tkinter as tk
from tkinter import messagebox

# Ajouter le répertoire scripts au path Python
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from services.collection import CollectionService
from services.image_service import ImageService
from ui.main_window import MainWindow

def main():
    """Point d'entrée principal de l'application"""
    # Chemins
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    images_dir = os.path.join(project_root, "images")
    
    # Créer les dossiers nécessaires
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(images_dir, "thumbnails"), exist_ok=True)
    os.makedirs(os.path.join(images_dir, "full"), exist_ok=True)
    
    # Services
    collection_service = CollectionService(os.path.join(data_dir, "collection.json"))
    image_service = ImageService(
        os.path.join(images_dir, "full"),
        os.path.join(images_dir, "thumbnails")
    )
    
    # Interface
    root = tk.Tk()
    app = MainWindow(root, collection_service, image_service)
    
    print("Démarrage du Gestionnaire de Collection de Figurines 3D")
    root.mainloop()

if __name__ == "__main__":
    main()