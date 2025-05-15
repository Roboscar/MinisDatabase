import os
import json
import shutil
from jinja2 import Template  # pip install jinja2

def generate_site(template_path, output_dir, data_file):
    """Génère le site statique"""
    # Crée le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Charge les données
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Charge le template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Génère la page HTML
    html_content = template.render(figurines=data['figurines'])
    
    # Écrit le fichier HTML
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Site généré avec succès!")

def copy_assets(src_dir, dest_dir, subdirs=None):
    """Copie les ressources (CSS, JS, images) vers le répertoire de destination"""
    if subdirs is None:
        subdirs = []
    
    for subdir in subdirs:
        src_path = os.path.join(src_dir, subdir)
        dest_path = os.path.join(dest_dir, subdir)
        
        if os.path.exists(src_path):
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            print(f"Ressources {subdir} copiées.")

if __name__ == "__main__":
    # Structure du projet
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, "src")
    data_dir = os.path.join(project_root, "data")
    dist_dir = os.path.join(project_root, "dist")
    
    # Génère le site
    generate_site(
        os.path.join(src_dir, "template.html"),
        dist_dir,
        os.path.join(data_dir, "collection.json")
    )
    
    # Copie les ressources
    copy_assets(src_dir, dist_dir, ["css", "js"])
    copy_assets(os.path.join(project_root, "images"), 
                os.path.join(dist_dir, "images"),
                ["thumbnails", "full"])
    
    # Copie le fichier de données
    os.makedirs(os.path.join(dist_dir, "data"), exist_ok=True)
    shutil.copy(
        os.path.join(data_dir, "collection.json"),
        os.path.join(dist_dir, "data", "collection.json")
    )