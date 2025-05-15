import tkinter as tk
from tkinter import ttk

class FigurineListPanel:
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        
        # Frame principale
        self.frame = ttk.Frame(parent, width=300)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        self.setup_ui()
    
    def setup_ui(self):
        # Titre et boutons pour la liste
        list_actions = ttk.Frame(self.frame)
        list_actions.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(list_actions, text="Figurines", font=("", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(list_actions, text="Nouvelle", command=self.callbacks['new_figurine']).pack(side=tk.RIGHT)
        
        # Contrôles de tri
        sort_frame = ttk.Frame(list_actions)
        sort_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(sort_frame, text="Trier par:").pack(side=tk.LEFT)
        
        self.sort_var = tk.StringVar(value="Nom (A-Z)")
        self.sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, width=20, state="readonly")
        self.sort_combo["values"] = ["Nom (A-Z)", "Nom (Z-A)", "Plus récent", "Plus ancien"]
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.callbacks['sort_change'](self.sort_var.get()))
        
        # Liste avec scrollbar
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(list_frame, exportselection=False)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', lambda e: self.callbacks['select_figurine'](self.get_selection()))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
    
    def get_selection(self):
        """Retourne l'index de l'élément sélectionné"""
        selection = self.listbox.curselection()
        return selection[0] if selection else None
    
    def update_list(self, items):
        """Met à jour la liste des figurines"""
        self.listbox.delete(0, tk.END)
        for item in items:
            self.listbox.insert(tk.END, item)