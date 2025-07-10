# 🤖 Bot Messenger avec Intelligence DeepSeek

Ce projet est un bot Messenger intelligent utilisant l'IA de DeepSeek, hébergé sur Render.

## 🚀 Comment l'utiliser

### 1. Fichiers à configurer
- `main.py` : code principal
- `Procfile` : obligatoire pour Render
- `.env.example` : modèle à copier
- `requirements.txt` : dépendances

### 2. Variables d’environnement (sur Render)

Ajoute ces variables dans l’onglet "Environment":

- `VERIFY_TOKEN` → ton token Facebook
- `PAGE_ACCESS_TOKEN` → token de ta page Messenger
- `DEEPSEEK_API_KEY` → ta clé DeepSeek API

### 3. Lien Webhook

Copie l'URL générée par Render dans ton **Facebook Developer Console > Webhook > Callback URL**

---

## 📌 Important

- Ne publie **jamais** le fichier `.env` avec tes vraies clés.
- Utilise `.env.example` dans le dépôt GitHub.
