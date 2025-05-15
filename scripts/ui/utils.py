def set_widget_state(widget, state):
    """Définit l'état d'un widget et de ses enfants récursivement"""
    if widget.winfo_children():
        for child in widget.winfo_children():
            set_widget_state(child, state)
    
    if widget.winfo_class() in ('TEntry', 'TButton', 'Listbox', 'TCombobox'):
        try:
            widget.configure(state=state)
        except:
            pass