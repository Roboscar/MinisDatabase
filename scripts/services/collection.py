import os
import json
from tkinter import messagebox
from models.figurine import Figurine  # Import absolu

class CollectionService:
    def __init__(self, collection_file):
        self.collection_file = collection_file
        self._collection = []
        self.load()
    
    def load(self):
        """Charge la collection depuis le fichier JSON"""
        if os.path.exists(self.collection_file):
            try:
                with open(self.collection_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._collection = [Figurine.from_dict(fig) for fig in data.get("figurines", [])]
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger la collection: {str(e)}")
                self._collection = []
        else:
            self._collection = []
    
    def save(self):
        """Sauvegarde la collection dans le fichier JSON"""
        try:
            with open(self.collection_file, 'w', encoding='utf-8') as f:
                data = {"figurines": [fig.to_dict() for fig in self._collection]}
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder la collection: {str(e)}")
            return False
    
    def add_figurine(self, name, full_image, thumbnail, tags):
        """Ajoute une nouvelle figurine à la collection"""
        next_id = 1
        if self._collection:
            next_id = max(f.id for f in self._collection) + 1
        
        figurine = Figurine(
            id=next_id,
            name=name,
            full_image=full_image,
            thumbnail=thumbnail,
            tags=tags
        )
        self._collection.append(figurine)
        return figurine
    
    def update_figurine(self, figurine, **kwargs):
        """Met à jour une figurine existante"""
        for key, value in kwargs.items():
            setattr(figurine, key, value)
    
    def remove_figurine(self, figurine):
        """Supprime une figurine de la collection"""
        self._collection.remove(figurine)
    
    def name_exists(self, name):
        """Vérifie si une figurine avec ce nom existe déjà"""
        return any(f.name.lower() == name.lower() for f in self._collection)
    
    def get_all_tags(self):
        """Récupère tous les tags uniques de la collection"""
        tags = set()
        for figurine in self._collection:
            tags.update(figurine.tags)
        return sorted(list(tags))
    
    @property
    def collection(self):
        return self._collection