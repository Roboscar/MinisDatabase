import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

class FigurineFormPanel:
    def __init__(self, parent, callbacks):
        """
        callbacks requis:
        - 'save': Pour sauvegarder les données (reçoit un dict)
        - 'delete': Pour supprimer la figurine
        - 'cancel': Pour annuler l'édition
        - 'image_selected': Pour gérer la sélection d'une nouvelle image
        - 'update_preview': Pour mettre à jour la prévisualisation d'une image
        """
        self.parent = parent
        self.callbacks = callbacks
        
        # Frame principale
        self.frame = ttk.Frame(parent)
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Variables
        self.name_var = tk.StringVar()
        self.new_tag_var = tk.StringVar()
        self.current_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Formulaire d'édition
        form_frame = ttk.LabelFrame(self.frame, text="Détails de la figurine", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nom
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=tk.W + tk.E, pady=5)
        
        # Image
        ttk.Label(form_frame, text="Image:").grid(row=1, column=0, sticky=tk.W, pady=5)
        image_frame = ttk.Frame(form_frame)
        image_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        self.image_path_label = ttk.Label(image_frame, text="Aucune image sélectionnée")
        self.image_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(image_frame, text="Parcourir...", command=self.browse_image).pack(side=tk.RIGHT)
        
        # Prévisualisation
        self.preview_frame = ttk.LabelFrame(form_frame, text="Prévisualisation", padding="5")
        self.preview_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W + tk.E + tk.N + tk.S, pady=10)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Tags
        self.setup_tags_section(form_frame)
        
        # Boutons d'action
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Supprimer", command=self.callbacks['delete']).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Annuler", command=self.callbacks['cancel']).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=5)
    
    def setup_tags_section(self, parent):
        tags_frame = ttk.LabelFrame(parent, text="Tags", padding="5")
        tags_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W + tk.E + tk.N + tk.S, pady=5)
        
        # Ajout de tag
        tag_entry_frame = ttk.Frame(tags_frame)
        tag_entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.tag_entry = ttk.Combobox(tag_entry_frame, textvariable=self.new_tag_var)
        self.tag_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(tag_entry_frame, text="Ajouter Tag", command=self.add_tag).pack(side=tk.RIGHT)
        
        # Liste des tags
        tags_list_frame = ttk.Frame(tags_frame)
        tags_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tags_listbox = tk.Listbox(tags_list_frame, height=5, exportselection=False)
        self.tags_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tags_scrollbar = ttk.Scrollbar(tags_list_frame, orient=tk.VERTICAL, command=self.tags_listbox.yview)
        tags_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tags_listbox.config(yscrollcommand=tags_scrollbar.set)
        
        ttk.Button(tags_frame, text="Supprimer Tag", command=self.remove_tag).pack(side=tk.RIGHT, pady=(5, 0))
    
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
            self.image_path_label.config(text=os.path.basename(filename))
            print(f"Image sélectionnée: {filename}")  # Debug
            if 'image_selected' in self.callbacks:
                self.callbacks['image_selected'](filename)
            else:
                print("Callback 'image_selected' manquant")  # Debug
    
    def add_tag(self):
        """Ajoute un tag à la liste"""
        tag = self.new_tag_var.get().strip()
        if tag:
            # Vérifier si le tag existe déjà dans la liste
            existing_tags = list(self.tags_listbox.get(0, tk.END))
            if tag not in existing_tags:
                self.tags_listbox.insert(tk.END, tag)
                self.new_tag_var.set("")  # Effacer le champ
    
    def remove_tag(self):
        selection = self.tags_listbox.curselection()
        if selection:
            self.tags_listbox.delete(selection[0])
    
    def save(self):
        data = {
            'name': self.name_var.get().strip(),
            'tags': list(self.tags_listbox.get(0, tk.END))
        }
        self.callbacks['save'](data)
    
    def clear(self):
        self.name_var.set("")
        self.image_path_label.config(text="Aucune image sélectionnée")
        self.tags_listbox.delete(0, tk.END)
        self.clear_preview()
    
    def clear_preview(self):
        self.preview_label.config(image="")
        self.preview_label.image = None
        self.current_image = None
    
    def set_tag_suggestions(self, tags):
        self.tag_entry['values'] = tags
    
    def update_preview(self, image_path):
        """Met à jour la prévisualisation de l'image"""
        if image_path:
            self.callbacks['update_preview'](image_path, self.preview_label)
    
    def load_figurine(self, figurine):
        """Charge les données d'une figurine dans le formulaire"""
        self.name_var.set(figurine.name)
        self.image_path_label.config(text=figurine.full_image)
        
        # Charger les tags
        self.tags_listbox.delete(0, tk.END)
        for tag in figurine.tags:
            self.tags_listbox.insert(tk.END, tag)
    
    def set_enabled(self, enabled):
        """Active ou désactive tous les widgets du formulaire"""
        state = "normal" if enabled else "disabled"
        for widget in self.frame.winfo_children():
            if widget.winfo_class() in ('TEntry', 'TButton', 'Listbox', 'TCombobox'):
                try:
                    widget.configure(state=state)
                except:
                    pass