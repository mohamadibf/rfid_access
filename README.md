# 🎯 rfid_access


---

## ⚙️ Prérequis

- Python 3.9 ou supérieur
- Git
- pip (inclus avec Python)
- virtualenv : `pip install virtualenv`

---

## 🚀 Installation du projet

### 1. Cloner le dépôt

```bash
git clone https://github.com/mohamadibf/rfid_access.git
cd rfid_access
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration initiale

### 1. Appliquer les migrations

```bash
python manage.py migrate
```

### 2. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 3. Lancer le serveur de développement

```bash
python manage.py runserver
```

Puis ouvrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/) dans le navigateur.

---

## 🔐 Accès à l'administration Django

- Lien : [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- Utiliser les identifiants du superutilisateur

---



## 📌 Remarques

Si vous installez de nouvelles bibliothèques :

```bash
pip freeze > requirements.txt
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Forkez le projet, créez une branche, proposez un pull request.

---

## 📄 Licence

Ce projet est sous licence MIT (ou autre à préciser).
