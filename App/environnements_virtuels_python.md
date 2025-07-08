# Les environnements virtuels en Python

---

## Qu’est-ce qu’un environnement virtuel Python ?
Un **environnement virtuel** est un espace isolé dans lequel on peut installer des packages Python **sans interagir avec le reste du système**. Cela permet :
- D’avoir des versions de bibliothèques propres à un projet
- D’éviter les conflits de dépendances entre projets
- De garder le système Python global propre

---

## Pourquoi utiliser un environnement virtuel ?
- Un projet A utilise `pandas==1.5.0`, un projet B `pandas==2.0.0`
- Tester différentes versions d’un package sans tout casser
- Collaborer facilement (les dépendances sont listées et reproductibles)

> C'est indispensable pour tout projet professionnel ou collaboratif.

---

## Créer un environnement virtuel
### Avec `venv` (standard Python)
```bash
python -m venv mon_env
```
Cela crée un dossier `mon_env/` contenant Python, pip et les répertoires d’installation.

### Activer l’environnement virtuel
- **Sous Windows :**
```bash
mon_env\Scripts\activate
```
- **Sous macOS/Linux :**
```bash
source mon_env/bin/activate
```

Une fois activé :
- Le prompt change (`(mon_env)`)
- `pip install` installera les packages **dans cet environnement seulement**

---

## Installer des packages dans l’environnement
```bash
pip install numpy pandas requests
```

## Lister les packages installés
```bash
pip list
```

## Exporter les dépendances pour les partager
```bash
pip freeze > requirements.txt
```

## Reproduire un environnement depuis un fichier
```bash
pip install -r requirements.txt
```

---

## Désactiver l’environnement virtuel
```bash
deactivate
```

---

## Alternatives à `venv`
### `virtualenv`
- Plus ancien, un peu plus flexible

### `conda`
- Outil de gestion d’environnements + installation de packages
- Très utilisé en data science (Anaconda)

---

## Bonnes pratiques
- Toujours créer un environnement par projet
- Versionner le fichier `requirements.txt`
- Ne pas installer globalement (sauf si besoin système)

---

## Ressources utiles
- https://docs.python.org/3/library/venv.html
- https://pip.pypa.io
- https://realpython.com/python-virtual-environments-a-primer/

