import os
import shutil
from PIL import Image, ImageTk
from tkinter import messagebox

class ImageService:
    def __init__(self, full_dir, thumb_dir):
        self.full_dir = full_dir
        self.thumb_dir = thumb_dir
    
    def save_image(self, source_path, project_root):
        """Sauvegarde l'image et crée une miniature"""
        try:
            filename = os.path.basename(source_path)
            full_path = os.path.join(self.full_dir, filename)
            thumb_path = os.path.join(self.thumb_dir, filename)
            
            # Copier l'image originale
            shutil.copy2(source_path, full_path)
            
            # Créer la miniature
            img = Image.open(full_path)
            img.thumbnail((300, 300))
            img.save(thumb_path)
            
            return (
                os.path.relpath(full_path, project_root).replace('\\', '/'),
                os.path.relpath(thumb_path, project_root).replace('\\', '/')
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de traiter l'image: {str(e)}")
            return None, None
    
    def delete_image(self, full_path, thumb_path):
        """Supprime les fichiers image"""
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            return True
        except Exception as e:
            messagebox.showwarning("Attention", f"Impossible de supprimer les images: {str(e)}")
            return False

    def load_preview(self, image_path, preview_label, size=(300, 300)):
        """Charge une prévisualisation de l'image"""
        try:
            print(f"Chargement de l'image: {image_path}")  # Debug
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img.thumbnail(size)
                photo = ImageTk.PhotoImage(img)
                preview_label.config(image=photo)
                preview_label.image = photo  # Garder une référence
                print("Prévisualisation chargée avec succès")  # Debug
            else:
                print(f"Fichier introuvable: {image_path}")  # Debug
                self.clear_preview(preview_label)
        except Exception as e:
            print(f"Erreur de chargement: {str(e)}")  # Debug
            self.clear_preview(preview_label)
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")