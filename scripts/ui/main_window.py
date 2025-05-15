import tkinter as tk
from tkinter import ttk, messagebox
import os
from .list_panel import FigurineListPanel
from .form_panel import FigurineFormPanel
from .utils import set_widget_state

class MainWindow:
    def __init__(self, root, collection_service, image_service):
        self.root = root
        self.collection_service = collection_service
        self.image_service = image_service
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.current_figurine = None
        self.selected_image_path = None
        
        self.root.title("Gestionnaire de Collection de Figurines 3D")
        self.root.geometry("950x650")
        self.root.minsize(800, 600)
        
        self.status_var = tk.StringVar(value="Prêt")
        
        self.setup_ui()
        self.collection_service.load()
        self.update_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Liste des figurines (côté gauche)
        self.list_panel = FigurineListPanel(main_frame, {
            'new_figurine': self.new_figurine,
            'select_figurine': self.on_figurine_select,
            'sort_change': self.on_sort_change
        })
        
        # Formulaire (côté droit)
        self.form_panel = FigurineFormPanel(main_frame, {
            'save': self.save_figurine,
            'delete': self.delete_figurine,
            'cancel': self.cancel_edit,
            'image_selected': self.handle_image_selection
        })
        
        # Barre de statut
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_ui(self):
        """Met à jour l'interface utilisateur"""
        figurine_names = [f.name for f in self.collection_service.collection]
        self.list_panel.update_list(figurine_names)
        self.form_panel.set_tag_suggestions(self.collection_service.get_all_tags())
    
    def toggle_form(self, enabled=True):
        """Active ou désactive le formulaire"""
        self.form_panel.set_enabled(enabled)
    
    def new_figurine(self):
        """Prépare le formulaire pour une nouvelle figurine"""
        self.current_figurine = None
        self.selected_image_path = None
        self.form_panel.clear()
        self.toggle_form(True)
        self.status_var.set("Création d'une nouvelle figurine")
    
    def on_figurine_select(self, index):
        """Gère la sélection d'une figurine dans la liste"""
        if index is not None:
            figurine = self.collection_service.collection[index]
            self.load_figurine(figurine)
    
    def load_figurine(self, figurine):
        """Charge une figurine dans le formulaire"""
        self.current_figurine = figurine
        self.form_panel.load_figurine(figurine)
        self.toggle_form(True)
        self.status_var.set(f"Modification de la figurine '{figurine.name}'")
    
    def save_figurine(self, data):
        """Sauvegarde les modifications de la figurine"""
        name = data['name']
        tags = data['tags']
        
        if not name:
            messagebox.showerror("Erreur", "Le nom de la figurine est obligatoire")
            return
        
        # Vérifier si le nom existe déjà
        if not self.current_figurine and self.collection_service.name_exists(name):
            messagebox.showerror("Erreur", f"Une figurine avec le nom '{name}' existe déjà")
            return
        
        try:
            # Traiter l'image si une nouvelle est sélectionnée
            full_image = ""
            thumbnail = ""
            if self.selected_image_path:
                full_image, thumbnail = self.image_service.save_image(
                    self.selected_image_path,
                    self.project_root
                )
                if not full_image or not thumbnail:
                    return  # L'erreur a déjà été affichée
            elif self.current_figurine:
                full_image = self.current_figurine.full_image
                thumbnail = self.current_figurine.thumbnail
            else:
                messagebox.showerror("Erreur", "Aucune image sélectionnée")
                return
            
            # Créer ou mettre à jour la figurine
            if self.current_figurine:
                # Mettre à jour
                if self.selected_image_path:
                    # Supprimer les anciennes images si elles ont changé
                    self.image_service.delete_old_images(
                        self.current_figurine.full_image,
                        self.current_figurine.thumbnail,
                        full_image,
                        self.project_root
                    )
                
                self.collection_service.update_figurine(
                    self.current_figurine,
                    name=name,
                    full_image=full_image,
                    thumbnail=thumbnail,
                    tags=tags
                )
                self.status_var.set(f"Figurine '{name}' mise à jour")
            else:
                # Créer nouvelle figurine
                self.collection_service.add_figurine(
                    name=name,
                    full_image=full_image,
                    thumbnail=thumbnail,
                    tags=tags
                )
                self.status_var.set(f"Nouvelle figurine '{name}' créée")
            
            # Sauvegarder et mettre à jour l'interface
            if self.collection_service.save():
                self.update_ui()
                self.toggle_form(False)
                self.current_figurine = None
                self.selected_image_path = None
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def delete_figurine(self):
        """Supprime la figurine actuelle"""
        if not self.current_figurine:
            return
        
        if messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer la figurine '{self.current_figurine.name}' ?"
        ):
            try:
                # Supprimer les images
                self.image_service.delete_image(
                    os.path.join(self.project_root, self.current_figurine.full_image),
                    os.path.join(self.project_root, self.current_figurine.thumbnail)
                )
                
                # Supprimer de la collection
                self.collection_service.remove_figurine(self.current_figurine)
                
                if self.collection_service.save():
                    self.status_var.set(f"Figurine '{self.current_figurine.name}' supprimée")
                    self.update_ui()
                    self.toggle_form(False)
                    self.current_figurine = None
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def cancel_edit(self):
        self.toggle_form(False)
        self.form_panel.clear()
        self.status_var.set("Édition annulée")
    
    def handle_image_selection(self, path):
        """Gère la sélection d'une nouvelle image"""
        if path:
            print(f"Traitement de la nouvelle image: {path}")  # Debug
            self.selected_image_path = path
            self.image_service.load_preview(path, self.form_panel.preview_label)
    
    def on_sort_change(self, criterion):
        """Gère le changement de critère de tri"""
        self.collection_service.sort(criterion)
        self.update_ui()