from json import dump, loads
from os import path, environ

CONST_PATH = path.join(environ['APPDATA'], 'CabiLib', 'Constantes.json').replace('\\', '/')

def load_constantes():
    """Charge toutes les constantes depuis le fichier JSON."""
    with open(CONST_PATH, encoding='utf-8') as f:
        return loads(f.read())

def save_constantes(data):
    """Écrit toutes les constantes dans le fichier JSON."""
    with open(CONST_PATH, 'w', encoding='utf-8') as f:
        dump(data, f, ensure_ascii=False, indent=2)

def get_constante(key):
    """Récupère une constante par sa clé."""
    data = load_constantes()
    return data.get(key)

def set_constante(key, value):
    """Modifie une constante et sauvegarde le fichier."""
    data = load_constantes()
    data[key] = value
    save_constantes(data)
