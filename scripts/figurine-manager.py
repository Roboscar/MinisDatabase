import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from datetime import datetime  # Ajouter en haut du fichier

class FigurineManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire de Collection de Figurines 3D")
        self.root.geometry("950x650")
        self.root.minsize(800, 600)
        
        # Chemins des dossiers - adaptés pour fonctionner depuis le dossier scripts
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.script_dir)  # Remonte d'un niveau
        self.data_dir = os.path.join(self.project_root, "data")
        self.images_dir = os.path.join(self.project_root, "images")
        self.thumbnails_dir = os.path.join(self.images_dir, "thumbnails")
        self.full_images_dir = os.path.join(self.images_dir, "full")
        
        # Créer les dossiers s'ils n'existent pas
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
        os.makedirs(self.full_images_dir, exist_ok=True)
        
        # Chemin du fichier JSON
        self.collection_file = os.path.join(self.data_dir, "collection.json")
        
        # Charger la collection
        self.collection = self.load_collection()
        
        # Variables
        self.current_figurine = None
        self.selected_image_path = None
        self.all_tags = self.extract_all_tags()
        
        # Interface
        self.setup_ui()
        
        # Remplir la liste des figurines
        self.update_figurines_list()
    
    def load_collection(self):
        """Charge la collection depuis le fichier JSON ou crée une nouvelle collection"""
        if os.path.exists(self.collection_file):
            try:
                with open(self.collection_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("figurines", [])
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Erreur", f"Impossible de charger la collection: {str(e)}")
                return []
        else:
            return []
    
    def save_collection(self):
        """Sauvegarde la collection dans le fichier JSON"""
        try:
            with open(self.collection_file, 'w', encoding='utf-8') as f:
                json.dump({"figurines": self.collection}, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder la collection: {str(e)}")
            return False
    
    def extract_all_tags(self):
        """Extrait tous les tags uniques de la collection"""
        tags = set()
        for figurine in self.collection:
            tags.update(figurine.get("tags", []))
        return sorted(list(tags))
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Créer un canvas avec scrollbar
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Créer le canvas et la scrollbar
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        # Frame principale qui contiendra tout le contenu
        main_frame = ttk.Frame(canvas, padding="10")
        
        # Configurer le canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Placer les widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Créer une fenêtre dans le canvas pour le contenu
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Côté gauche - Liste des figurines
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Titre et boutons pour la liste
        list_actions = ttk.Frame(left_frame)
        list_actions.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(list_actions, text="Figurines", font=("", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(list_actions, text="Nouvelle", command=self.new_figurine).pack(side=tk.RIGHT)
        
        # Ajouter les contrôles de tri
        sort_frame = ttk.Frame(list_actions)
        sort_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(sort_frame, text="Trier par:").pack(side=tk.LEFT)
        
        self.sort_var = tk.StringVar(value="name_asc")
        sort_combobox = ttk.Combobox(sort_frame, textvariable=self.sort_var, width=20, state="readonly")
        sort_combobox["values"] = [
            "Nom (A-Z)",
            "Nom (Z-A)",
            "Plus récent",
            "Plus ancien"
        ]
        sort_combobox.pack(side=tk.LEFT, padx=5)
        sort_combobox.bind("<<ComboboxSelected>>", self.on_sort_change)
        
        # Liste des figurines avec scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.figurines_listbox = tk.Listbox(list_frame, exportselection=False)
        self.figurines_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.figurines_listbox.bind('<<ListboxSelect>>', self.on_figurine_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.figurines_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.figurines_listbox.config(yscrollcommand=scrollbar.set)
        
        # Côté droit - Détails de la figurine
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Formulaire d'édition
        form_frame = ttk.LabelFrame(right_frame, text="Détails de la figurine", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nom
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=tk.W + tk.E, pady=5)
        
        # Image
        ttk.Label(form_frame, text="Image:").grid(row=1, column=0, sticky=tk.W, pady=5)
        image_frame = ttk.Frame(form_frame)
        image_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        self.image_path_label = ttk.Label(image_frame, text="Aucune image sélectionnée")
        self.image_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(image_frame, text="Parcourir...", command=self.browse_image).pack(side=tk.RIGHT)
        
        # Prévisualisation de l'image
        self.preview_frame = ttk.LabelFrame(form_frame, text="Prévisualisation", padding="5")
        self.preview_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W + tk.E + tk.N + tk.S, pady=10)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Tags
        tags_label_frame = ttk.LabelFrame(form_frame, text="Tags", padding="5")
        tags_label_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W + tk.E + tk.N + tk.S, pady=5)
        
        # Ajouter un tag
        tag_entry_frame = ttk.Frame(tags_label_frame)
        tag_entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.new_tag_var = tk.StringVar()
        self.tag_entry = ttk.Combobox(tag_entry_frame, textvariable=self.new_tag_var)
        self.tag_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.update_tags_combobox()
        
        ttk.Button(tag_entry_frame, text="Ajouter Tag", command=self.add_tag).pack(side=tk.RIGHT)
        
        # Liste des tags
        tags_frame = ttk.Frame(tags_label_frame)
        tags_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tags_listbox = tk.Listbox(tags_frame, height=5, exportselection=False)
        self.tags_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tags_scrollbar = ttk.Scrollbar(tags_frame, orient=tk.VERTICAL, command=self.tags_listbox.yview)
        tags_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tags_listbox.config(yscrollcommand=tags_scrollbar.set)
        
        # Boutons pour gérer les tags
        tags_buttons_frame = ttk.Frame(tags_label_frame)
        tags_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(tags_buttons_frame, text="Supprimer Tag", command=self.remove_tag).pack(side=tk.RIGHT)
        
        # Boutons d'action
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Supprimer", command=self.delete_figurine).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=self.cancel_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Enregistrer", command=self.save_figurine).pack(side=tk.LEFT, padx=5)
        
        # Désactiver le formulaire au démarrage
        self.toggle_form_state(False)
        
        # Configurer le scrolling
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ajuster la largeur de la fenêtre du canvas
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        # Lier les événements
        main_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Configurer le scrolling avec la molette de la souris
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Barre de statut (doit être en dehors du canvas)
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Prêt")
    
    def toggle_form_state(self, enabled=True):
        """Active ou désactive le formulaire"""
        state = "normal" if enabled else "disabled"
        
        # Les widgets du formulaire de détails (côté droit)
        form_frame = self.root.winfo_children()[0].winfo_children()[1]  # Main frame -> Right frame
        self.set_widget_state(form_frame, state)
        
        # La liste des figurines et le bouton "Nouvelle" doivent toujours rester actifs
        self.figurines_listbox.configure(state='normal')
        for widget in self.root.winfo_children()[0].winfo_children()[0].winfo_children():  # Main frame -> Left frame
            if isinstance(widget, ttk.Button):  # Bouton "Nouvelle"
                widget.configure(state='normal')
    
    def set_widget_state(self, widget, state):
        """Définit l'état d'un widget et de ses enfants récursivement"""
        if widget.winfo_children():
            for child in widget.winfo_children():
                self.set_widget_state(child, state)
        
        if widget.winfo_class() in ('TEntry', 'TButton', 'Listbox', 'TCombobox'):
            try:
                widget.configure(state=state)
            except:
                pass
    
    def update_figurines_list(self):
        """Met à jour la liste des figurines"""
        self.figurines_listbox.delete(0, tk.END)
        
        # Afficher les figurines
        for figurine in self.collection:
            self.figurines_listbox.insert(tk.END, figurine.get("name", "Sans nom"))
    
    def update_tags_combobox(self):
        """Met à jour la liste déroulante des tags existants"""
        self.all_tags = self.extract_all_tags()
        self.tag_entry['values'] = self.all_tags
    
    def on_figurine_select(self, event):
        """Gère la sélection d'une figurine dans la liste"""
        selection = self.figurines_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if 0 <= index < len(self.collection):
            self.load_figurine(self.collection[index])
    
    def new_figurine(self):
        """Prépare le formulaire pour une nouvelle figurine"""
        self.current_figurine = None
        self.selected_image_path = None
        
        # Réinitialiser les champs
        self.name_var.set("")
        self.image_path_label.config(text="Aucune image sélectionnée")
        self.clear_preview()
        self.tags_listbox.delete(0, tk.END)
        
        # Activer le formulaire
        self.toggle_form_state(True)
        self.status_var.set("Création d'une nouvelle figurine")
    
    def load_figurine(self, figurine):
        """Charge les détails d'une figurine dans le formulaire"""
        self.current_figurine = figurine
        
        # Remplir les champs
        self.name_var.set(figurine.get("name", ""))
        
        # Afficher l'image
        self.selected_image_path = None
        self.image_path_label.config(text=figurine.get("fullImage", ""))
        self.load_preview(os.path.join(self.project_root, figurine.get("fullImage", "")))
        
        # Charger les tags
        self.tags_listbox.delete(0, tk.END)
        for tag in figurine.get("tags", []):
            self.tags_listbox.insert(tk.END, tag)
        
        # Activer le formulaire
        self.toggle_form_state(True)
        self.status_var.set(f"Modification de la figurine '{figurine.get('name', '')}'")
    
    def browse_image(self):
        """Ouvre un dialogue pour sélectionner une image"""
        filetypes = (
            ("Images", "*.jpg *.jpeg *.png"),
            ("Tous les fichiers", "*.*")
        )
        
        filename = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=filetypes
        )
        
        if filename:
            self.selected_image_path = filename
            self.image_path_label.config(text=os.path.basename(filename))
            self.load_preview(filename)
    
    def load_preview(self, image_path):
        """Charge une prévisualisation de l'image"""
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                
                # Redimensionner l'image pour la prévisualisation (max 300x300)
                img.thumbnail((300, 300))
                
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo)
                self.preview_label.image = photo  # Garder une référence pour éviter la garbage collection
            else:
                self.clear_preview()
        except Exception as e:
            self.clear_preview()
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")
    
    def clear_preview(self):
        """Efface la prévisualisation de l'image"""
        self.preview_label.config(image="")
        self.preview_label.image = None
    
    def add_tag(self):
        """Ajoute un tag à la liste des tags de la figurine"""
        tag = self.new_tag_var.get().strip()
        if tag:
            # Vérifier si le tag existe déjà dans la liste
            tags = list(self.tags_listbox.get(0, tk.END))
            if tag not in tags:
                self.tags_listbox.insert(tk.END, tag)
                self.new_tag_var.set("")  # Effacer le champ
    
    def remove_tag(self):
        """Supprime un tag de la liste des tags de la figurine"""
        selection = self.tags_listbox.curselection()
        if selection:
            self.tags_listbox.delete(selection[0])
    
    def save_figurine(self):
        """Sauvegarde les modifications de la figurine"""
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showerror("Erreur", "Le nom de la figurine est obligatoire")
            return
        
        # Vérifier si le nom existe déjà dans la collection
        for figurine in self.collection:
            if figurine.get("name") == name and figurine != self.current_figurine:
                messagebox.showerror("Erreur", f"Une figurine avec le nom '{name}' existe déjà")
                return
        
        # Récupérer les tags
        tags = list(self.tags_listbox.get(0, tk.END))
        
        # Traiter l'image si une nouvelle est sélectionnée
        if self.selected_image_path:
            filename = os.path.basename(self.selected_image_path)
            full_path = os.path.join(self.full_images_dir, filename)
            thumb_path = os.path.join(self.thumbnails_dir, filename)
            
            # Copier l'image dans le dossier des images complètes
            shutil.copy2(self.selected_image_path, full_path)
            
            # Créer une miniature
            try:
                img = Image.open(full_path)
                img.thumbnail((300, 300))
                img.save(thumb_path)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer la miniature: {str(e)}")
                return
            
            full_image_path = f"images/full/{filename}"
            thumbnail_path = f"images/thumbnails/{filename}"
        elif self.current_figurine:
            # Conserver les chemins d'image existants
            full_image_path = self.current_figurine.get("fullImage", "")
            thumbnail_path = self.current_figurine.get("thumbnail", "")
        else:
            messagebox.showerror("Erreur", "Aucune image sélectionnée")
            return
        
        # Ajouter la date de modification
        current_time = datetime.now().isoformat()
        
        # Créer ou mettre à jour la figurine
        if self.current_figurine:
            # Mettre à jour une figurine existante
            
            # Si l'image a changé, supprimer l'ancienne
            if self.selected_image_path and self.current_figurine.get("fullImage"):
                old_full = os.path.join(self.project_root, self.current_figurine.get("fullImage", ""))
                old_thumb = os.path.join(self.project_root, self.current_figurine.get("thumbnail", ""))
                
                try:
                    if os.path.exists(old_full) and os.path.basename(old_full) != os.path.basename(full_image_path):
                        os.remove(old_full)
                    if os.path.exists(old_thumb) and os.path.basename(old_thumb) != os.path.basename(thumbnail_path):
                        os.remove(old_thumb)
                except OSError as e:
                    messagebox.showwarning("Attention", f"Impossible de supprimer les anciennes images: {str(e)}")
            
            # Mettre à jour les informations
            self.current_figurine.update({
                "name": name,
                "fullImage": full_image_path,
                "thumbnail": thumbnail_path,
                "tags": tags,
                "modified_date": current_time  # Ajouter la date
            })
            
            self.status_var.set(f"Figurine '{name}' mise à jour")
        else:
            # Créer une nouvelle figurine
            
            # Trouver le prochain ID disponible
            next_id = 1
            if self.collection:
                next_id = max([f.get("id", 0) for f in self.collection]) + 1
            
            # Créer la nouvelle figurine
            new_figurine = {
                "id": next_id,
                "name": name,
                "fullImage": full_image_path,
                "thumbnail": thumbnail_path,
                "tags": tags,
                "modified_date": current_time  # Ajouter la date
            }
            
            self.collection.append(new_figurine)
            self.status_var.set(f"Nouvelle figurine '{name}' créée")
        
        # Sauvegarder la collection
        if self.save_collection():
            # Mettre à jour l'interface
            self.update_figurines_list()
            self.update_tags_combobox()
            
            # Réinitialiser le formulaire et le désactiver
            self.toggle_form_state(False)
            self.current_figurine = None
            self.selected_image_path = None
    
    def delete_figurine(self):
        """Supprime la figurine actuelle"""
        if not self.current_figurine:
            return
        
        name = self.current_figurine.get("name", "")
        confirm = messagebox.askyesno(
            "Confirmation", 
            f"Êtes-vous sûr de vouloir supprimer la figurine '{name}' ?"
        )
        
        if confirm:
            # Supprimer les fichiers image
            try:
                full_path = os.path.join(self.project_root, self.current_figurine.get("fullImage", ""))
                thumb_path = os.path.join(self.project_root, self.current_figurine.get("thumbnail", ""))
                
                if os.path.exists(full_path):
                    os.remove(full_path)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
            except OSError as e:
                messagebox.showwarning("Attention", f"Impossible de supprimer les images: {str(e)}")
            
            # Supprimer la figurine de la collection
            self.collection.remove(self.current_figurine)
            
            # Sauvegarder la collection
            if self.save_collection():
                self.status_var.set(f"Figurine '{name}' supprimée")
                
                # Mettre à jour l'interface
                self.update_figurines_list()
                self.update_tags_combobox()
                
                # Réinitialiser le formulaire et le désactiver
                self.toggle_form_state(False)
                self.current_figurine = None
                self.selected_image_path = None
    
    def cancel_edit(self):
        """Annule l'édition en cours"""
        self.toggle_form_state(False)
        self.current_figurine = None
        self.selected_image_path = None
        self.status_var.set("Édition annulée")
    
    def sort_collection(self):
        """Trie la collection selon le critère sélectionné"""
        sort_type = self.sort_var.get()
        
        if sort_type == "Nom (A-Z)":
            self.collection.sort(key=lambda x: x.get("name", "").lower())
        elif sort_type == "Nom (Z-A)":
            self.collection.sort(key=lambda x: x.get("name", "").lower(), reverse=True)
        elif sort_type == "Plus récent":
            self.collection.sort(key=lambda x: x.get("modified_date", ""), reverse=True)
        elif sort_type == "Plus ancien":
            self.collection.sort(key=lambda x: x.get("modified_date", ""))
        
        # Mettre à jour l'affichage après le tri
        self.update_figurines_list()
    
    def on_sort_change(self, event):
        """Appelé quand l'utilisateur change le critère de tri"""
        self.sort_collection()

def main():
    root = tk.Tk()
    app = FigurineManager(root)
    root.mainloop()

if __name__ == "__main__":
    # Affiche des informations de démarrage
    print("Démarrage du Gestionnaire de Collection de Figurines 3D")
    main()
