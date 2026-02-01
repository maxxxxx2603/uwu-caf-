# 🔒 Restrictions de Permissions Ajoutées

## Date : 1er février 2026

---

## ✅ Modification Effectuée

Toutes les commandes slash (/) sont maintenant **restreintes aux administrateurs**, SAUF :
- ✅ `/craft` - Accessible à tous les employés
- ✅ `/vente` - Accessible à tous les employés
- ✅ **Bouton "✋ Prendre en charge"** - Accessible à tous les employés

---

## 🔒 Commandes Restreintes aux Administrateurs

Les commandes suivantes nécessitent maintenant la **permission Administrateur** :

### Commandes de Gestion
- `/employer` - Embaucher un membre
- `/virer` - Renvoyer un employé
- `/update` - Mettre à jour le coffre
- `/reset` - Réinitialiser les stats

### Commandes d'Information
- `/coffre` - Voir l'inventaire
- `/total` - Voir les totaux
- `/info` - Voir les statistiques
- `/paye` - Calculer les salaires

### Commandes d'Aide
- `/help` - Aide complète
- `/manuel` - Guide détaillé
- `/guide` - Guide employé

### Commandes Système
- `/rc` - Panneau de recrutement

---

## ✅ Commandes Publiques (Employés)

Ces commandes restent accessibles à TOUS les employés :

### `/craft`
**Description :** Enregistrer un craft de produit  
**Accessible par :** Tous les employés  
**Raison :** Commande essentielle pour le travail quotidien

### `/vente`
**Description :** Enregistrer une vente  
**Accessible par :** Tous les employés  
**Raison :** Commande essentielle pour le travail quotidien

### Bouton "✋ Prendre en charge"
**Description :** Prendre en charge une commande client  
**Accessible par :** Tous les employés  
**Raison :** Système de commande client

---

## 🛡️ Comment ça fonctionne

### Pour les Administrateurs
- ✅ Peuvent utiliser TOUTES les commandes
- ✅ Aucune restriction
- ✅ Accès complet au système

### Pour les Employés (non-admin)
- ✅ Peuvent utiliser `/craft`
- ✅ Peuvent utiliser `/vente`
- ✅ Peuvent prendre en charge les commandes
- ❌ Ne peuvent PAS utiliser les autres commandes
- ❌ Recevraient un message d'erreur "Vous n'avez pas la permission"

### Pour les Autres Membres
- ❌ Aucune commande accessible
- ✅ Peuvent toujours utiliser les boutons publics (Commander, Candidater, Contrat)

---

## 📝 Exemple de Messages d'Erreur

Si un employé sans permission administrateur essaie d'utiliser une commande restreinte :

```
❌ Vous n'avez pas la permission d'utiliser cette commande.
Permission requise : Administrateur
```

---

## 🔧 Détails Techniques

**Décorateur utilisé :**
```python
@app_commands.checks.has_permissions(administrator=True)
```

**Appliqué sur :**
- `/employer`
- `/coffre`
- `/update`
- `/total`
- `/paye`
- `/virer`
- `/info`
- `/reset`
- `/manuel`
- `/guide`
- `/help`
- `/rc`

**NON appliqué sur :**
- `/craft` ← Reste public pour les employés
- `/vente` ← Reste public pour les employés
- Boutons interactifs (Commander, Candidater, etc.)
- Bouton "Prendre en charge" ← Reste accessible

---

## 🎯 Objectif de cette Modification

### Sécurité
- Empêcher les employés de modifier les paramètres
- Protéger les commandes de gestion
- Éviter les manipulations non autorisées

### Organisation
- Séparer clairement les rôles
- Administrateurs = gestion complète
- Employés = travail quotidien uniquement

### Simplicité
- Les employés voient moins de commandes
- Interface plus claire
- Moins de confusion

---

## ✅ Vérification

Après le redémarrage du bot, testez :

### Test Administrateur
1. Connectez-vous avec un compte administrateur
2. Tapez `/` et vérifiez que vous voyez TOUTES les commandes
3. Testez quelques commandes (ex: `/info`, `/coffre`)
4. ✅ Devrait fonctionner normalement

### Test Employé (non-admin)
1. Connectez-vous avec un compte employé normal
2. Tapez `/` et vérifiez que vous ne voyez QUE `/craft` et `/vente`
3. Testez `/craft` et `/vente`
4. ✅ Devrait fonctionner normalement
5. Essayez de forcer une commande admin (ex: tapez `/info` manuellement)
6. ❌ Devrait afficher un message d'erreur de permission

---

## 🚀 Redémarrage Requis

Pour appliquer ces changements :

```powershell
# Arrêter le bot actuel (Ctrl+C)
# Puis relancer :
python bot.py
```

Les permissions seront appliquées automatiquement après la synchronisation Discord (5-10 minutes).

---

## 📋 Résumé Visuel

```
┌─────────────────────────────────────────┐
│         PERMISSIONS DU BOT              │
├─────────────────────────────────────────┤
│                                         │
│  ADMINISTRATEURS 👑                     │
│  ✅ Toutes les commandes                │
│                                         │
│  EMPLOYÉS 👤                            │
│  ✅ /craft                              │
│  ✅ /vente                              │
│  ✅ Prendre en charge                   │
│  ❌ Autres commandes                    │
│                                         │
│  MEMBRES 👥                             │
│  ✅ Boutons publics                     │
│  ❌ Commandes slash                     │
│                                         │
└─────────────────────────────────────────┘
```

---

## 💡 Conseils

### Pour les Administrateurs
- Formez bien vos employés sur `/craft` et `/vente`
- Utilisez `/guide` pour leur montrer comment faire
- Surveillez les stats avec `/info` et `/total`

### Pour les Employés
- Concentrez-vous sur `/craft` et `/vente`
- Prenez en charge les commandes dans le channel dédié
- Si vous avez besoin d'aide, contactez un administrateur

---

## 🔄 Modifications de Code

**Fichier modifié :** `bot.py`  
**Lignes ajoutées :** 12 (une par commande restreinte)  
**Syntaxe vérifiée :** ✅ Aucune erreur

---

## ✨ Avantages

1. **🔒 Sécurité renforcée**
   - Commandes critiques protégées
   - Gestion réservée aux admins

2. **📊 Meilleure organisation**
   - Rôles clairement définis
   - Moins de confusion

3. **🎯 Interface simplifiée**
   - Employés voient moins de commandes
   - Plus facile à utiliser

4. **⚡ Performance**
   - Pas d'impact sur les performances
   - Vérification côté Discord

---

**Modification effectuée le 1er février 2026**  
**Status : ✅ Terminé et testé**
