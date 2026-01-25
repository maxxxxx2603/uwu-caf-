# Bot Discord - Uwu Café - Système de Ventes

Bot Discord pour gérer les ventes de produits de votre entreprise avec système de facturation.

## 🎯 Fonctionnalités

- ✅ Commande `/vente` utilisable partout
- ✅ Sélection de produit via menu déroulant
- ✅ Saisie de quantité via modal
- ✅ Upload de capture d'écran de facture
- ✅ Message récapitulatif avec image téléchargée
- ✅ Suppression automatique des messages intermédiaires
- ✅ Embed professionnel avec toutes les informations

## 📋 Prérequis

- Python 3.8+
- discord.py 2.3.2+
- Un bot Discord configuré

## 🚀 Installation

1. **Installer Python**
   - Téléchargez Python depuis [python.org](https://www.python.org/downloads/)
   - Assurez-vous de cocher "Add Python to PATH"

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Copiez `.env.example` vers `.env`
   - Ajoutez votre token Discord:
     ```
     DISCORD_TOKEN=votre_token_ici
     ```

## 🔧 Configuration du Bot Discord

1. **Créer une application Discord**
   - Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
   - Cliquez sur "New Application"
   - Donnez un nom à votre bot

2. **Créer le bot**
   - Allez dans l'onglet "Bot"
   - Cliquez sur "Add Bot"
   - Copiez le token et mettez-le dans `.env`

3. **Activer les intents**
   - Dans l'onglet "Bot"
   - Activez:
     - ✅ Presence Intent
     - ✅ Server Members Intent
     - ✅ Message Content Intent

4. **Inviter le bot**
   - Allez dans l'onglet "OAuth2" > "URL Generator"
   - Sélectionnez:
     - Scopes: `bot`, `applications.commands`
     - Permissions: `Send Messages`, `Attach Files`, `Embed Links`, `Read Messages`
   - Copiez l'URL et invitez le bot sur votre serveur

## 🎮 Utilisation

1. **Lancer le bot**
   ```bash
   python bot.py
   ```

2. **Utiliser la commande `/vente`**
   - Tapez `/vente` dans n'importe quel salon
   - Sélectionnez le produit vendu
   - Entrez la quantité
   - Envoyez la capture d'écran de la facture
   - Le bot créera automatiquement un message récapitulatif propre

## 📦 Liste des Produits

Le bot inclut par défaut ces produits (modifiables dans `bot.py`):
- Café Latte, Cappuccino, Espresso
- Thé Vert, Thé Noir
- Chocolat Chaud
- Smoothies (Fraise, Mangue)
- Viennoiseries (Croissant, Pain au Chocolat, Muffin, Cookie)
- Sandwichs (Jambon, Poulet)
- Salade César

## ✏️ Personnalisation

### Modifier les produits

Dans `bot.py`, ligne 18, modifiez la liste `PRODUITS`:
```python
PRODUITS = [
    "Votre Produit 1",
    "Votre Produit 2",
    # ...
]
```

### Modifier les couleurs

Changez les couleurs des embeds:
```python
discord.Color.blue()    # Bleu
discord.Color.green()   # Vert
discord.Color.red()     # Rouge
discord.Color.orange()  # Orange
```

## 🛠️ Dépannage

**Le bot ne démarre pas:**
- Vérifiez que le token est correct dans `.env`
- Assurez-vous que les dépendances sont installées

**La commande ne s'affiche pas:**
- Attendez quelques minutes (synchronisation Discord)
- Relancez le bot
- Vérifiez que le bot a les permissions `applications.commands`

**L'image ne s'affiche pas:**
- Vérifiez que le bot a la permission `Attach Files`
- Assurez-vous d'envoyer une image valide (PNG, JPG, etc.)

## � Déploiement sur Railway

### Étape 1: Préparer GitHub

1. **Créer un compte GitHub** (si nécessaire)
   - Allez sur [github.com](https://github.com)

2. **Pousser le code sur GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/maxxxxx2603/uwu-caf-.git
   git branch -M main
   git push -u origin main
   ```

### Étape 2: Déployer sur Railway

1. **Créer un compte Railway**
   - Allez sur [railway.app](https://railway.app)
   - Connectez-vous avec GitHub

2. **Créer un nouveau projet**
   - Cliquez sur "New Project"
   - Sélectionnez "Deploy from GitHub repo"
   - Choisissez votre repository `uwu-caf-`

3. **Configurer les variables d'environnement**
   - Dans les paramètres du projet, allez dans "Variables"
   - Ajoutez:
     - `DISCORD_TOKEN`: votre token Discord
     - `GUILD_ID`: l'ID de votre serveur (optionnel)

4. **Déploiement automatique**
   - Railway détectera automatiquement `railway.json` et `Procfile`
   - Le bot démarrera automatiquement
   - Vérifiez les logs pour confirmer que tout fonctionne

### Étape 3: Vérifier le déploiement

- Regardez les logs dans Railway
- Le bot devrait apparaître en ligne sur Discord
- Testez la commande `/vente`

### ⚙️ Fichiers de configuration Railway

Le projet inclut:
- `Procfile`: Définit comment démarrer le bot
- `railway.json`: Configuration Railway
- `runtime.txt`: Spécifie la version Python
- `requirements.txt`: Liste des dépendances

## 📝 Support

Pour toute question, contactez le développeur ou consultez la documentation Discord.py:
- [Documentation discord.py](https://discordpy.readthedocs.io/)
- [Guide Discord Developer](https://discord.com/developers/docs/)
- [Documentation Railway](https://docs.railway.app/)

## 📄 Licence

Ce projet est libre d'utilisation pour votre serveur Discord.
