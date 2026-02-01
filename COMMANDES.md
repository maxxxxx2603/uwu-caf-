# 📋 Liste Complète des Commandes - Bot Uwu Café

## 👨‍💼 Commandes Employés

### `/craft` - Créer des produits
**Description :** Enregistrer un craft de produit pour le coffre  
**Utilisation :** 
1. Taper `/craft`
2. Sélectionner le produit dans le menu
3. Entrer la quantité craftée
4. Envoyer une capture d'écran de preuve
5. Le produit est ajouté au coffre et vos stats sont mises à jour

**Permissions :** Employés uniquement

---

### `/vente` - Enregistrer une vente
**Description :** Enregistrer une vente de produit à un client  
**Utilisation :**
1. Taper `/vente`
2. Sélectionner le produit vendu
3. Entrer la quantité vendue
4. Envoyer une capture d'écran de facture
5. Le produit est retiré du coffre et vos stats sont mises à jour

**Permissions :** Employés uniquement

---

### `/coffre` - Voir l'inventaire
**Description :** Afficher l'état actuel du coffre avec tous les produits  
**Utilisation :** Taper `/coffre`  
**Affiche :**
- Tous les produits disponibles
- Quantité en stock pour chaque produit
- Prix unitaire de chaque produit

**Permissions :** Tout le monde

---

### `/total` - Statistiques personnelles
**Description :** Afficher le total des crafts et ventes par employé  
**Utilisation :** Taper `/total`  
**Affiche :**
- Nombre de crafts par employé
- Nombre de ventes par employé
- Classement des employés

**Permissions :** Tout le monde

---

### `/info` - Statistiques globales
**Description :** Afficher les statistiques détaillées de tous les employés  
**Utilisation :** Taper `/info`  
**Affiche :**
- Crafts par employé
- Ventes par employé
- Commandes traitées par employé
- Total d'actions par employé

**Permissions :** Tout le monde

---

## ⚙️ Commandes de Gestion

### `/employer` - Embaucher un membre
**Description :** Créer un canal employé pour un nouveau membre du staff  
**Utilisation :** `/employer @membre`  
**Actions automatiques :**
- Création d'un channel personnel pour l'employé
- Attribution des rôles employés
- Message de bienvenue
- Guide des commandes /craft et /vente
- Explication du channel de prise en charge

**Permissions :** Gestionnaires uniquement

---

### `/virer` - Renvoyer un employé
**Description :** Virer un employé (enlever rôles et pseudo)  
**Utilisation :** `/virer @membre`  
**Actions automatiques :**
- Retrait de tous les rôles employés
- Réinitialisation du pseudo
- Suppression du channel employé
- Log dans le channel de modération

**Permissions :** Gestionnaires uniquement

---

### `/paye` - Calculer les salaires
**Description :** Calculer les salaires des employés basés sur leurs crafts  
**Utilisation :** Taper `/paye`  
**Système de paiement :**
- Quota de base : 600 crafts = 1.500.000$
- Bonus : tous les 50 crafts supplémentaires = +125.000$

**Affiche :**
- Salaire de chaque employé
- Statut du quota (atteint ou non)
- Total à payer pour tous les employés

**Permissions :** Gestionnaires uniquement

---

### `/update` - Mettre à jour le coffre
**Description :** Forcer la mise à jour du message du coffre  
**Utilisation :** Taper `/update`  
**Note :** La mise à jour est normalement automatique après chaque craft/vente

**Permissions :** Gestionnaires uniquement

---

### `/reset` - Réinitialiser les stats
**Description :** Remettre à zéro les statistiques des employés  
**Utilisation :** Taper `/reset`, puis confirmer  
**⚠️ ATTENTION :** 
- Action irréversible
- Efface toutes les stats (crafts, ventes, commandes)
- Le coffre n'est pas modifié
- Demande de confirmation avant exécution

**Permissions :** Gestionnaires uniquement

---

## 📚 Commandes d'Aide

### `/help` - Aide rapide ⭐ NOUVEAU
**Description :** Afficher l'aide complète du bot avec toutes les commandes  
**Utilisation :** Taper `/help`  
**Affiche :**
- Vue d'ensemble de toutes les commandes par catégorie
- Commandes Employés
- Commandes Gestion
- Commandes d'Aide
- Systèmes Automatiques
- Mention du channel de prise en charge

**Permissions :** Tout le monde

---

### `/manuel` - Guide détaillé
**Description :** Guide complet de toutes les fonctionnalités du bot  
**Utilisation :** Taper `/manuel`  
**Affiche :** 4 pages d'embeds avec :
- Page 1 : Vue d'ensemble
- Page 2 : Commandes Employés détaillées
- Page 3 : Commandes Gestion détaillées
- Page 4 : Systèmes Automatiques détaillés

**Permissions :** Tout le monde

---

### `/guide` - Guide employé
**Description :** Guide rapide des commandes /craft et /vente  
**Utilisation :** Taper `/guide`  
**Affiche :**
- Explication détaillée de /craft
- Explication détaillée de /vente
- Information sur le channel commande

**Permissions :** Tout le monde

---

### `/rc` - Panneau de recrutement
**Description :** Afficher le panneau de recrutement Uwu Café  
**Utilisation :** Taper `/rc`  
**Actions :**
- Publie les boutons de service dans les channels appropriés
- Bouton "Candidater" : Formulaire de recrutement
- Bouton "Contrat" : Demande de contrat
- Bouton "Commander" : Système de commande client

**Permissions :** Gestionnaires uniquement

---

## 🎫 Systèmes Automatiques (Boutons)

### 📝 Bouton "Candidater"
**Localisation :** Channel de recrutement  
**Fonctionnement :**
1. Cliquer sur le bouton
2. Répondre aux 10 questions automatiquement
3. Uploader une pièce d'identité
4. Le CV est envoyé à la modération
5. Les modérateurs peuvent accepter ou refuser
6. Le candidat reçoit une réponse automatique

---

### 📄 Bouton "Contrat"
**Localisation :** Channel de service  
**Fonctionnement :**
1. Cliquer sur le bouton
2. Un ticket privé est créé
3. Discussion possible avec les gestionnaires

---

### 🛒 Bouton "Commander"
**Localisation :** Channel de service  
**Fonctionnement :**
1. Client clique sur "Commander"
2. Un ticket privé est créé pour le client
3. Le client sélectionne les produits et quantités
4. Le client valide sa commande
5. **La commande est envoyée dans <#1464356444940931231>**
6. **Un ping @everyone notifie tous les employés** ⭐ NOUVEAU
7. Un employé clique sur "✋ Prendre en charge"
8. Un channel de livraison privé est créé (client + employé)
9. L'employé peut livrer la commande
10. L'employé clique sur "✅ Effectuer" quand c'est fait
11. Les stats de l'employé sont mises à jour

---

### ✋ Bouton "Prendre en charge"
**Localisation :** Channel de commande (<#1464356444940931231>)  
**Fonctionnement :**
1. Une commande client apparaît avec ping @everyone
2. Un employé clique sur "✋ Prendre en charge"
3. **Un message de confirmation apparaît (ERREUR CORRIGÉE)** ⭐ NOUVEAU
4. Un channel de livraison est créé automatiquement
5. L'employé reçoit le lien vers ce channel
6. L'employé peut discuter avec le client
7. Quand la livraison est effectuée, cliquer sur "✅ Effectuer"

---

## 📍 Channels Importants

### Channel de Prise en Charge
**ID :** 1464356444940931231  
**Mention :** <#1464356444940931231>  
**Utilisation :**
- Toutes les commandes clients y sont envoyées
- Les employés y sont notifiés avec @everyone
- Les employés prennent en charge les commandes ici
- Les activités /craft et /vente y sont annoncées

---

## 🎯 Produits Disponibles

1. **Latte Fraise** - 2200$
2. **Limonade Japonaise** - 1500$
3. **Tanghulu** - 2500$
4. **Latte Macha** - 2200$
5. **Pancakes** - 2300$
6. **Mochi** - 2300$
7. **Bubble Tea** - 2500$
8. **Eau** - 1200$
9. **Cake Japonais** - 2900$
10. **Croffle** - 2500$

---

## 💡 Astuces et Conseils

### Pour les Employés :
- Utilisez `/craft` régulièrement pour maintenir le stock
- Utilisez `/vente` pour chaque vente client
- Surveillez le channel de prise en charge pour les commandes
- Consultez `/guide` si vous avez oublié comment faire

### Pour les Gestionnaires :
- Utilisez `/help` pour orienter les nouveaux
- Utilisez `/info` pour voir les performances
- Utilisez `/paye` pour calculer les salaires
- Utilisez `/employer` pour bien accueillir les nouveaux

### Pour les Clients :
- Utilisez le bouton "Commander" pour passer commande
- Attendez qu'un employé prenne en charge
- Discutez dans le channel de livraison créé

---

## 🆘 Problèmes Courants

### "Je ne vois pas les commandes"
- Les commandes peuvent prendre 5-10 minutes pour apparaître
- Essayez de relancer Discord
- Vérifiez vos permissions

### "L'interaction a échoué"
- **CE PROBLÈME EST MAINTENANT CORRIGÉ** ⭐
- Si ça persiste, contactez un administrateur

### "Le coffre n'est pas à jour"
- Utilisez `/update` pour forcer la mise à jour
- La mise à jour est normalement automatique

---

## ✨ Nouveautés (1er février 2026)

1. ⭐ **Commande /help** - Vue d'ensemble rapide de toutes les commandes
2. ⭐ **Ping @everyone** - Notification automatique pour les nouvelles commandes
3. ⭐ **Erreur corrigée** - Plus d'erreur lors de la prise en charge
4. ⭐ **Message amélioré** - Meilleur guide dans /employer avec mention du channel

---

**Bot créé pour Uwu Café - Dernière mise à jour : 1er février 2026**
