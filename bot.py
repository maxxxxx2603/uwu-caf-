import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp
from io import BytesIO
import asyncio
import json
from datetime import timedelta

load_dotenv()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Liste des produits disponibles avec prix
PRODUITS = {
    "Latte Fraise": 2200,
    "Limonade Japonaise": 1500,
    "Tanghulu": 2500,
    "Latte Macha": 2200,
    "Pancakes": 2300,
    "Mochi": 2300,
    "Bubble Tea": 2500,
    "Eau": 1200,
    "Cake Japonais": 2900,
    "Croffle": 2500
}

# Coffre - Inventaire des produits
COFFRE_FILE = "coffre.json"
STATS_FILE = "stats_employes.json"
COFFRE_MESSAGE_FILE = "coffre_message.json"

def load_coffre():
    """Charger l'inventaire du coffre"""
    if os.path.exists(COFFRE_FILE):
        with open(COFFRE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Initialiser avec 0 pour tous les produits
        return {produit: 0 for produit in PRODUITS.keys()}

def save_coffre(coffre_data):
    """Sauvegarder l'inventaire du coffre"""
    with open(COFFRE_FILE, 'w', encoding='utf-8') as f:
        json.dump(coffre_data, f, ensure_ascii=False, indent=2)

def load_coffre_message_info():
    """Charger les infos du message coffre (channel_id, message_id)"""
    if os.path.exists(COFFRE_MESSAGE_FILE):
        with open(COFFRE_MESSAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_coffre_message_info(channel_id, message_id):
    """Sauvegarder les infos du message coffre"""
    with open(COFFRE_MESSAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump({"channel_id": channel_id, "message_id": message_id}, f)

async def update_coffre_message():
    """Mettre à jour le message du coffre en temps réel"""
    info = load_coffre_message_info()
    if not info:
        return
    
    try:
        channel = bot.get_channel(info["channel_id"])
        if not channel:
            return
        
        message = await channel.fetch_message(info["message_id"])
        
        embed = discord.Embed(
            title="🗄️ Inventaire du Coffre - Uwu Café",
            description="État des stocks en temps réel",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        for produit, quantite in coffre_inventory.items():
            prix = PRODUITS.get(produit, 0)
            embed.add_field(
                name=f"📦 {produit}",
                value=f"**{quantite}** unités | {prix}$ l'unité",
                inline=True
            )
        
        embed.set_footer(text="Mis à jour automatiquement via /craft et /vente")
        
        await message.edit(embed=embed)
    except Exception as e:
        print(f"Erreur lors de la mise à jour du message coffre: {e}")

def load_stats():
    """Charger les statistiques des employés"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_stats(stats_data):
    """Sauvegarder les statistiques des employés"""
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

async def update_employee_stat(user_id, user_name, stat_type, amount=1):
    """Mettre à jour les statistiques d'un employé et le message coffre"""
    stats = load_stats()
    user_id_str = str(user_id)
    
    if user_id_str not in stats:
        stats[user_id_str] = {
            "name": user_name,
            "crafts": 0,
            "ventes": 0,
            "commandes": 0
        }
    
    stats[user_id_str]["name"] = user_name  # Mettre à jour le nom
    stats[user_id_str][stat_type] += amount
    save_stats(stats)
    
    # Mettre à jour le message coffre
    await update_coffre_message()

# Charger le coffre au démarrage
coffre_inventory = load_coffre()

@bot.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} commande(s) synchronisée(s)')
    except Exception as e:
        print(f'❌ Erreur lors de la synchronisation: {e}')

class ProduitSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=f"{produit} - {prix}$",
                value=produit
            ) 
            for produit, prix in PRODUITS.items()
        ]
        super().__init__(
            placeholder="Choisissez un produit...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        self.view.produit_choisi = self.values[0]
        await interaction.response.send_modal(QuantiteModal(self.view))

class QuantiteModal(discord.ui.Modal, title="Quantité"):
    def __init__(self, view):
        super().__init__()
        self.vente_view = view
    
    quantite = discord.ui.TextInput(
        label="Quantité vendue",
        placeholder="Entrez la quantité...",
        required=True,
        min_length=1,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            qte = int(self.quantite.value)
            if qte <= 0:
                await interaction.response.send_message(
                    "❌ La quantité doit être supérieure à 0!",
                    ephemeral=False
                )
                return
            
            self.vente_view.quantite = qte
            self.vente_view.interaction_user = interaction.user
            
            # Sauvegarder le message du modal pour le supprimer plus tard
            prix_unitaire = PRODUITS[self.vente_view.produit_choisi]
            prix_total = prix_unitaire * qte
            
            # Demander la capture d'écran
            embed = discord.Embed(
                title="📸 Capture d'écran de la facture",
                description=f"**Produit:** {self.vente_view.produit_choisi}\n"
                           f"**Prix unitaire:** {prix_unitaire}$\n"
                           f"**Quantité:** {qte}\n"
                           f"**Prix total:** {prix_total}$\n\n"
                           "Veuillez envoyer la capture d'écran de la facture dans ce salon.",
                color=discord.Color.blue()
            )
            response_msg = await interaction.response.send_message(embed=embed)
            self.vente_view.modal_message = await interaction.original_response()
            
            # Attendre la capture d'écran
            def check(m):
                return (m.author == interaction.user and 
                       m.channel == interaction.channel and 
                       len(m.attachments) > 0)
            
            try:
                msg = await bot.wait_for('message', timeout=300.0, check=check)
                
                # Télécharger l'image
                attachment = msg.attachments[0]
                
                # Vérifier que c'est une image
                if not attachment.content_type or not attachment.content_type.startswith('image/'):
                    await interaction.followup.send(
                        "❌ Veuillez envoyer une image valide!",
                        ephemeral=False
                    )
                    return
                
                # Télécharger l'image
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image_file = discord.File(
                                BytesIO(image_data),
                                filename=f"facture_{self.vente_view.produit_choisi.replace(' ', '_')}.png"
                            )
                
                # Calculer les prix
                prix_unitaire = PRODUITS[self.vente_view.produit_choisi]
                prix_total = prix_unitaire * qte
                
                # RETIRER DU COFFRE
                global coffre_inventory
                if self.vente_view.produit_choisi not in coffre_inventory:
                    coffre_inventory[self.vente_view.produit_choisi] = 0
                coffre_inventory[self.vente_view.produit_choisi] -= qte
                save_coffre(coffre_inventory)
                await update_coffre_message()
                
                # METTRE À JOUR LES STATS
                await update_employee_stat(interaction.user.id, interaction.user.name, "ventes", qte)
                
                # Créer le message récapitulatif
                embed_final = discord.Embed(
                    title="💰 Vente Enregistrée",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed_final.add_field(
                    name="👤 Vendeur",
                    value=interaction.user.mention,
                    inline=True
                )
                embed_final.add_field(
                    name="📦 Produit",
                    value=self.vente_view.produit_choisi,
                    inline=True
                )
                embed_final.add_field(
                    name="🔢 Quantité",
                    value=f"-{qte}",
                    inline=True
                )
                embed_final.add_field(
                    name="💵 Prix unitaire",
                    value=f"{prix_unitaire}$",
                    inline=True
                )
                embed_final.add_field(
                    name="💰 Prix total",
                    value=f"{prix_total}$",
                    inline=True
                )
                embed_final.add_field(
                    name="🗄️ Stock Restant",
                    value=f"**{coffre_inventory[self.vente_view.produit_choisi]}** unités",
                    inline=False
                )
                embed_final.set_image(url=f"attachment://{image_file.filename}")
                embed_final.set_footer(
                    text=f"Vente par {interaction.user.name}",
                    icon_url=interaction.user.display_avatar.url
                )
                
                # Envoyer le message final
                final_message = await interaction.channel.send(
                    embed=embed_final,
                    file=image_file
                )
                
                # Supprimer TOUS les messages intermédiaires
                messages_to_delete = []
                try:
                    # Message du modal (capture d'écran demandée)
                    if hasattr(self.vente_view, 'modal_message'):
                        messages_to_delete.append(self.vente_view.modal_message)
                    
                    # Message de l'utilisateur avec l'image
                    messages_to_delete.append(msg)
                    
                    # Message initial de la commande /vente
                    if hasattr(self.vente_view, 'initial_message'):
                        messages_to_delete.append(self.vente_view.initial_message)
                    
                    # Supprimer tous les messages
                    await interaction.channel.delete_messages(messages_to_delete)
                except:
                    # Si delete_messages échoue, essayer un par un
                    try:
                        await interaction.delete_original_response()
                    except:
                        pass
                    try:
                        await msg.delete()
                    except:
                        pass
                    if hasattr(self.vente_view, 'initial_message'):
                        try:
                            await self.vente_view.initial_message.delete()
                        except:
                            pass
                
            except TimeoutError:
                await interaction.followup.send(
                    "⏱️ Temps écoulé! Veuillez réessayer la commande /vente.",
                    ephemeral=False
                )
        
        except ValueError:
            await interaction.response.send_message(
                "❌ Veuillez entrer un nombre valide!",
                ephemeral=False
            )

class VenteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.produit_choisi = None
        self.quantite = None
        self.initial_message = None
        self.modal_message = None
        self.interaction_user = None
        self.add_item(ProduitSelect())

@bot.tree.command(name="vente", description="Enregistrer une vente de produit")
async def vente(interaction: discord.Interaction):
    """Commande pour enregistrer une vente"""
    embed = discord.Embed(
        title="💼 Nouvelle Vente",
        description="Sélectionnez le produit vendu:",
        color=discord.Color.blue()
    )
    
    view = VenteView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
    view.initial_message = await interaction.original_response()

# ==================== COMMANDE /EMPLOYER ====================

@bot.tree.command(name="employer", description="Créer un canal employé pour un nouveau membre du staff")
@app_commands.describe(membre="Le membre à embaucher")
@app_commands.checks.has_permissions(administrator=True)
async def employer(interaction: discord.Interaction, membre: discord.Member):
    """Commande pour créer un canal employé"""
    guild = interaction.guild
    
    # Utiliser simplement le pseudo Discord
    nom_channel = membre.name.lower().replace(" ", "-")
    
    # Créer le canal dans la catégorie employés
    employee_category = discord.utils.get(guild.categories, id=EMPLOYEE_CATEGORY)
    
    if not employee_category:
        await interaction.response.send_message(
            "❌ Catégorie employés introuvable!",
            ephemeral=False
        )
        return
    
    # Créer le canal
    employee_channel = await guild.create_text_channel(
        name=nom_channel,
        category=employee_category,
        topic=f"Canal personnel de {membre.mention}"
    )
    
    # Permissions
    await employee_channel.set_permissions(guild.default_role, read_messages=False)
    await employee_channel.set_permissions(membre, read_messages=True, send_messages=True)
    
    # Attribuer les rôles employés
    role1 = guild.get_role(EMPLOYEE_ROLE_1)
    role2 = guild.get_role(EMPLOYEE_ROLE_2)
    
    roles_ajoutes = []
    try:
        if role1:
            await membre.add_roles(role1)
            roles_ajoutes.append(role1.mention)
        if role2:
            await membre.add_roles(role2)
            roles_ajoutes.append(role2.mention)
    except discord.errors.Forbidden:
        pass  # Ignorer si pas les permissions
    
    # Message de bienvenue dans le canal
    embed_welcome = discord.Embed(
        title="🎉 Bienvenue dans l'équipe !",
        description=f"Bienvenue {membre.mention} dans l'équipe du **Uwu Café** !\n\n"
                   f"Ce canal est votre espace personnel pour:\n"
                   f"• Recevoir des informations importantes\n"
                   f"• Gérer vos commandes\n"
                   f"• Communiquer avec la direction\n\n"
                   f"Bon travail ! ☕",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed_welcome.set_thumbnail(url=membre.display_avatar.url)
    
    await employee_channel.send(embed=embed_welcome)
    
    # Message explicatif des commandes
    embed_commandes = discord.Embed(
        title="📋 Guide des Commandes Employé - /craft et /vente",
        description="**Voici les commandes essentielles que vous devez utiliser :**\n\n"
                   "Ces deux commandes sont au cœur de votre travail au café !",
        color=discord.Color.blue()
    )

    embed_commandes.add_field(
        name="☕ /craft - Créer des produits",
        value="**Craft des produits pour le coffre**\n"
              "Cette commande vous permet de créer des produits et de les ajouter au coffre du café.\n"
              "• Sélectionnez le produit à crafter\n"
              "• Indiquez la quantité\n"
              "• Les produits seront ajoutés à votre compteur personnel et au coffre général\n"
              "• Votre progression sera trackée dans vos statistiques",
        inline=False
    )

    embed_commandes.add_field(
        name="💰 /vente - Vendre aux clients",
        value="**Vendre des produits aux clients**\n"
              "Cette commande vous permet d'enregistrer une vente.\n"
              "• Sélectionnez le produit vendu\n"
              "• Indiquez la quantité vendue\n"
              "• Les produits seront retirés du coffre\n"
              "• L'argent gagné sera comptabilisé\n"
              "• Vos ventes seront enregistrées dans vos statistiques",
        inline=False
    )

    embed_commandes.add_field(
        name="📢 Channel de Prise en Charge",
        value=f"Le **channel commande** (<#1464356444940931231>) est l'endroit où :\n"
              f"• Les clients passent leurs commandes\n"
              f"• Vous pouvez prendre en charge les commandes avec le bouton ✋\n"
              f"• Toutes les activités `/craft` et `/vente` sont annoncées\n"
              f"• L'équipe suit l'activité en temps réel",
        inline=False
    )

    embed_commandes.set_footer(text="💡 Utilisez ces commandes pour contribuer au café !")

    await employee_channel.send(embed=embed_commandes)

    # Réponse à la commande
    await interaction.response.send_message(
        f"✅ Canal employé créé: {employee_channel.mention}\n"
        f"Rôles: {', '.join(roles_ajoutes) if roles_ajoutes else 'À ajouter manuellement'}",
        ephemeral=False
    )

# ==================== COMMANDE /AIDEEMPLOYÉ ====================

@bot.tree.command(name="aideemployé", description="Afficher le guide des commandes employé")
@app_commands.checks.has_permissions(administrator=True)
async def aideemploye(interaction: discord.Interaction):
    """Guide simple des commandes employé"""
    
    embed = discord.Embed(
        title="📋 Guide Employé",
        description="**Les 2 commandes essentielles :**",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="☕ /craft",
        value="Craft de produits du Uwu Café",
        inline=True
    )

    embed.add_field(
        name="💰 /vente",
        value="Vente de produits du Uwu Café",
        inline=True
    )

    embed.add_field(
        name="📍 Channel de Commande",
        value=f"**Rendez-vous ici:** <#1464356444940931231>\n"
              f"• Prenez en charge les commandes clients\n"
              f"• Suivez l'activité du café en direct",
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)

# ==================== COMMANDE /COFFRE ====================

@bot.tree.command(name="coffre", description="Afficher l'inventaire du coffre")
@app_commands.checks.has_permissions(administrator=True)
async def coffre(interaction: discord.Interaction):
    """Afficher l'état actuel du coffre avec mise à jour automatique"""
    global coffre_inventory
    
    embed = discord.Embed(
        title="🗄️ Inventaire du Coffre - Uwu Café",
        description="État des stocks en temps réel",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    
    # Ajouter chaque produit
    for produit, quantite in coffre_inventory.items():
        prix = PRODUITS.get(produit, 0)
        embed.add_field(
            name=f"📦 {produit}",
            value=f"**{quantite}** unités | {prix}$ l'unité",
            inline=True
        )
    
    embed.set_footer(text="Mis à jour automatiquement via /craft et /vente")
    
    await interaction.response.send_message(embed=embed)
    
    # Sauvegarder l'ID du message pour les mises à jour futures
    message = await interaction.original_response()
    save_coffre_message_info(interaction.channel_id, message.id)

# ==================== COMMANDE /UPDATE ====================

@bot.tree.command(name="update", description="Mettre à jour les données du coffre")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    """Forcer la mise à jour du message coffre"""
    await update_coffre_message()
    await interaction.response.send_message("✅ Données du coffre mises à jour !", ephemeral=False)

# ==================== COMMANDE /TOTAL ====================

@bot.tree.command(name="total", description="Afficher le total des crafts et ventes par employé")
@app_commands.checks.has_permissions(administrator=True)
async def total(interaction: discord.Interaction):
    """Afficher les totaux de crafts et ventes par employé"""
    stats = load_stats()
    
    if not stats:
        await interaction.response.send_message(
            "📊 Aucune donnée disponible.",
            ephemeral=False
        )
        return
    
    embed = discord.Embed(
        title="📊 Total des Crafts et Ventes",
        description="Performance des employés",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    
    # Trier par crafts
    sorted_by_crafts = sorted(
        stats.items(),
        key=lambda x: x[1]["crafts"],
        reverse=True
    )
    
    for user_id, data in sorted_by_crafts:
        embed.add_field(
            name=f"👤 {data['name']}",
            value=f"🛠️ **Crafts:** {data['crafts']}\n💰 **Ventes:** {data['ventes']}",
            inline=True
        )
    
    embed.set_footer(text="Totaux en temps réel")
    await interaction.response.send_message(embed=embed)

# ==================== COMMANDE /PAYE ====================

@bot.tree.command(name="paye", description="Calculer les salaires des employés")
@app_commands.checks.has_permissions(administrator=True)
async def paye(interaction: discord.Interaction):
    """Calculer les salaires basés sur les crafts"""
    stats = load_stats()
    
    if not stats:
        await interaction.response.send_message(
            "📊 Aucune donnée de crafts disponible.",
            ephemeral=False
        )
        return
    
    embed = discord.Embed(
        title="💰 Calcul des Salaires - Uwu Café",
        description="**Système de paiement:**\n"
                   "• Quota de base: **600 crafts** = 1.500.000$\n"
                   "• Bonus: tous les **50 crafts** supplémentaires = +125.000$",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    
    total_payes = 0
    
    # Trier par crafts
    sorted_by_crafts = sorted(
        stats.items(),
        key=lambda x: x[1]["crafts"],
        reverse=True
    )
    
    for user_id, data in sorted_by_crafts:
        crafts = data["crafts"]
        
        if crafts >= 600:
            # Salaire de base
            salaire = 1500000
            
            # Calcul des bonus (crafts au-dessus de 600)
            crafts_bonus = crafts - 600
            nombre_bonus = crafts_bonus // 50
            salaire += nombre_bonus * 125000
            
            total_payes += salaire
            
            # Formater le salaire avec des espaces
            salaire_formatte = f"{salaire:,}".replace(",", " ")
            
            status = "✅ Quota atteint"
            if nombre_bonus > 0:
                status += f" + {nombre_bonus} bonus"
        else:
            # Pas encore le quota
            salaire = 0
            salaire_formatte = "0"
            restant = 600 - crafts
            status = f"❌ Quota non atteint ({restant} crafts restants)"
        
        embed.add_field(
            name=f"👤 {data['name']}",
            value=f"🛠️ Crafts: **{crafts}**\n"
                  f"💵 Salaire: **{salaire_formatte}$**\n"
                  f"{status}",
            inline=True
        )
    
    total_formatte = f"{total_payes:,}".replace(",", " ")
    embed.set_footer(text=f"Total à payer: {total_formatte}$")
    
    await interaction.response.send_message(embed=embed)

# ==================== COMMANDE /CRAFT ====================

class CraftProduitSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=produit, value=produit)
            for produit in PRODUITS.keys()
        ]
        super().__init__(placeholder="Sélectionnez le produit crafté", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        produit = self.values[0]
        self.view.produit_choisi = produit
        
        # Ouvrir le modal pour la quantité
        modal = CraftQuantiteModal(self.view)
        await interaction.response.send_modal(modal)

class CraftQuantiteModal(discord.ui.Modal, title="Quantité Craftée"):
    def __init__(self, view):
        super().__init__()
        self.craft_view = view
    
    quantite = discord.ui.TextInput(
        label="Quantité craftée",
        placeholder="Entrez la quantité...",
        required=True,
        min_length=1,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            qte = int(self.quantite.value)
            if qte <= 0:
                await interaction.response.send_message(
                    "❌ La quantité doit être supérieure à 0!",
                    ephemeral=False
                )
                return
            
            self.craft_view.quantite = qte
            self.craft_view.interaction_user = interaction.user
            
            # Demander la capture d'écran
            embed = discord.Embed(
                title="📸 Capture d'écran du craft",
                description=f"**Produit:** {self.craft_view.produit_choisi}\n"
                           f"**Quantité:** {qte}\n\n"
                           "Veuillez envoyer la capture d'écran de la preuve du craft dans ce salon.",
                color=discord.Color.blue()
            )
            response_msg = await interaction.response.send_message(embed=embed)
            self.craft_view.modal_message = await interaction.original_response()
            
            # Attendre la capture d'écran
            def check(m):
                return (m.author == interaction.user and 
                       m.channel == interaction.channel and 
                       len(m.attachments) > 0)
            
            try:
                msg = await bot.wait_for('message', timeout=300.0, check=check)
                
                # Télécharger l'image
                attachment = msg.attachments[0]
                
                # Vérifier que c'est une image
                if not attachment.content_type or not attachment.content_type.startswith('image/'):
                    await interaction.followup.send(
                        "❌ Veuillez envoyer une image valide!",
                        ephemeral=False
                    )
                    return
                
                # Télécharger l'image
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image_file = discord.File(
                                BytesIO(image_data),
                                filename=f"craft_{self.craft_view.produit_choisi.replace(' ', '_')}.png"
                            )
                
                # AJOUTER AU COFFRE
                global coffre_inventory
                if self.craft_view.produit_choisi not in coffre_inventory:
                    coffre_inventory[self.craft_view.produit_choisi] = 0
                coffre_inventory[self.craft_view.produit_choisi] += qte
                save_coffre(coffre_inventory)
                await update_coffre_message()
                
                # METTRE À JOUR LES STATS
                await update_employee_stat(interaction.user.id, interaction.user.name, "crafts", qte)
                
                # Créer le message récapitulatif
                embed_final = discord.Embed(
                    title="✅ Craft Enregistré",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed_final.add_field(
                    name="👤 Crafteur",
                    value=interaction.user.mention,
                    inline=True
                )
                embed_final.add_field(
                    name="📦 Produit",
                    value=self.craft_view.produit_choisi,
                    inline=True
                )
                embed_final.add_field(
                    name="🔢 Quantité",
                    value=f"+{qte}",
                    inline=True
                )
                embed_final.add_field(
                    name="🗄️ Stock Total",
                    value=f"**{coffre_inventory[self.craft_view.produit_choisi]}** unités",
                    inline=False
                )
                embed_final.set_image(url=f"attachment://{image_file.filename}")
                embed_final.set_footer(
                    text=f"Craft par {interaction.user.name}",
                    icon_url=interaction.user.display_avatar.url
                )
                
                # Envoyer le message final
                final_message = await interaction.channel.send(
                    embed=embed_final,
                    file=image_file
                )
                
                # Supprimer les messages intermédiaires
                messages_to_delete = []
                try:
                    if hasattr(self.craft_view, 'modal_message'):
                        messages_to_delete.append(self.craft_view.modal_message)
                    messages_to_delete.append(msg)
                    if hasattr(self.craft_view, 'initial_message'):
                        messages_to_delete.append(self.craft_view.initial_message)
                    
                    await interaction.channel.delete_messages(messages_to_delete)
                except:
                    try:
                        await interaction.delete_original_response()
                    except:
                        pass
                    try:
                        await msg.delete()
                    except:
                        pass
                    if hasattr(self.craft_view, 'initial_message'):
                        try:
                            await self.craft_view.initial_message.delete()
                        except:
                            pass
                
            except TimeoutError:
                await interaction.followup.send(
                    "⏱️ Temps écoulé! Veuillez réessayer la commande /craft.",
                    ephemeral=False
                )
        
        except ValueError:
            await interaction.response.send_message(
                "❌ Veuillez entrer un nombre valide!",
                ephemeral=False
            )

class CraftView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.produit_choisi = None
        self.quantite = None
        self.initial_message = None
        self.modal_message = None
        self.interaction_user = None
        self.add_item(CraftProduitSelect())

@bot.tree.command(name="craft", description="Enregistrer un craft de produit")
async def craft(interaction: discord.Interaction):
    """Commande pour enregistrer un craft"""
    embed = discord.Embed(
        title="🛠️ Nouveau Craft",
        description="Sélectionnez le produit crafté:",
        color=discord.Color.blue()
    )
    
    view = CraftView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
    view.initial_message = await interaction.original_response()

# ==================== COMMANDE /VIRER ====================

@bot.tree.command(name="virer", description="Virer un employé (enlever rôles et pseudo)")
@app_commands.describe(membre="Le membre à virer")
@app_commands.checks.has_permissions(administrator=True)
async def virer(interaction: discord.Interaction, membre: discord.Member):
    """Commande pour virer un employé"""
    guild = interaction.guild
    
    # Rôle à conserver
    ROLE_A_GARDER = 1407470187212439660
    role_a_garder = guild.get_role(ROLE_A_GARDER)
    
    try:
        # Enlever tous les rôles sauf le rôle spécifié et @everyone
        roles_a_enlever = [role for role in membre.roles if role.id != ROLE_A_GARDER and role != guild.default_role]
        
        if roles_a_enlever:
            await membre.remove_roles(*roles_a_enlever, reason=f"Viré par {interaction.user.name}")
        
        # Enlever le surnom (nickname)
        if membre.nick:
            await membre.edit(nick=None, reason=f"Viré par {interaction.user.name}")
        
        # Supprimer le channel employé s'il existe
        channel_name = membre.name.lower().replace(" ", "-")
        for channel in guild.channels:
            if channel.name == channel_name and isinstance(channel, discord.TextChannel):
                try:
                    await channel.delete(reason=f"Membre viré par {interaction.user.name}")
                except:
                    pass
                break
        
        # Envoyer un log dans MODERATION_CHANNEL
        try:
            moderation_channel = guild.get_channel(MODERATION_CHANNEL)
            if moderation_channel:
                log_embed = discord.Embed(
                    title="🚫 Employé Viré",
                    description=f"**Membre:** {membre.mention} ({membre.name})\n"
                               f"**Viré par:** {interaction.user.mention}\n"
                               f"**Rôles enlevés:** {len(roles_a_enlever)}",
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                await moderation_channel.send(embed=log_embed)
        except Exception as e:
            print(f"Erreur lors de l'envoi du log: {e}")
        
        await interaction.response.send_message(
            f"✅ {membre.mention} a été viré.\n"
            f"• {len(roles_a_enlever)} rôle(s) enlevé(s)\n"
            f"• Pseudo réinitialisé\n"
            f"• Channel employé supprimé",
            ephemeral=False
        )
        
    except discord.errors.Forbidden:
        await interaction.response.send_message(
            "❌ Je n'ai pas les permissions nécessaires pour virer ce membre.",
            ephemeral=False
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Erreur lors du renvoi: {e}",
            ephemeral=False
        )

# ==================== COMMANDE /INFO ====================

@bot.tree.command(name="info", description="Afficher les statistiques des employés")
@app_commands.checks.has_permissions(administrator=True)
async def info(interaction: discord.Interaction):
    """Afficher les stats de tous les employés"""
    stats = load_stats()
    
    if not stats:
        await interaction.response.send_message(
            "📊 Aucune statistique disponible pour le moment.",
            ephemeral=False
        )
        return
    
    embed = discord.Embed(
        title="📊 Statistiques des Employés - Uwu Café",
        description="Performance de l'équipe",
        color=discord.Color.purple(),
        timestamp=discord.utils.utcnow()
    )
    
    # Trier par nombre total d'actions
    sorted_stats = sorted(
        stats.items(),
        key=lambda x: x[1]["crafts"] + x[1]["ventes"] + x[1]["commandes"],
        reverse=True
    )
    
    for user_id, data in sorted_stats:
        total_actions = data["crafts"] + data["ventes"] + data["commandes"]
        embed.add_field(
            name=f"👤 {data['name']}",
            value=f"🛠️ Crafts: **{data['crafts']}**\n"
                  f"💰 Ventes: **{data['ventes']}**\n"
                  f"🛒 Commandes: **{data['commandes']}**\n"
                  f"📈 Total: **{total_actions}**",
            inline=True
        )
    
    embed.set_footer(text="Statistiques mises à jour en temps réel")
    await interaction.response.send_message(embed=embed)

# ==================== COMMANDE /RESET ====================

@bot.tree.command(name="reset", description="Remettre à zéro les statistiques des employés")
@app_commands.checks.has_permissions(administrator=True)
async def reset(interaction: discord.Interaction):
    """Remettre à zéro les statistiques des employés uniquement"""
    
    # Créer une vue de confirmation
    class ConfirmResetView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.value = None
        
        @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = True
            self.stop()
            
            # Reset des stats uniquement
            save_stats({})
            
            await interaction.response.send_message(
                "✅ **Reset effectué !**\n\n"
                "• Statistiques des employés effacées\n"
                "• Le coffre n'a pas été modifié",
                ephemeral=False
            )
        
        @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = False
            self.stop()
            await interaction.response.send_message("❌ Reset annulé.", ephemeral=False)
    
    view = ConfirmResetView()
    await interaction.response.send_message(
        "⚠️ **ATTENTION : Reset des statistiques**\n\n"
        "Cette action va :\n"
        "• Effacer toutes les statistiques des employés (crafts, ventes, commandes)\n\n"
        "**Le coffre ne sera pas modifié**\n\n"
        "**Cette action est irréversible !**\n\n"
        "Voulez-vous vraiment continuer ?",
        view=view,
        ephemeral=False
    )

# ==================== COMMANDE /MANUEL ====================

@bot.tree.command(name="manuel", description="Guide complet de toutes les fonctionnalités du bot")
@app_commands.checks.has_permissions(administrator=True)
async def manuel(interaction: discord.Interaction):
    """Afficher un guide complet du bot"""
    
    # Page 1 - Vue d'ensemble
    embed1 = discord.Embed(
        title="📖 Manuel du Bot Uwu Café",
        description="Bienvenue dans le guide complet du bot ! Ce bot gère toutes les opérations du café.",
        color=discord.Color.purple()
    )
    
    embed1.add_field(
        name="🎯 Fonctionnalités Principales",
        value="• **Gestion des ventes et crafts**\n"
              "• **Système de recrutement**\n"
              "• **Gestion du coffre et inventaire**\n"
              "• **Statistiques des employés**\n"
              "• **Système de commandes clients**\n"
              "• **Paie des employés**",
        inline=False
    )
    
    embed1.set_footer(text="Page 1/4 - Vue d'ensemble")
    
    # Page 2 - Commandes Employés
    embed2 = discord.Embed(
        title="👨‍💼 Commandes Employés",
        color=discord.Color.blue()
    )
    
    embed2.add_field(
        name="☕ /craft",
        value="**Enregistrer un craft de produit**\n"
              "• Sélectionnez le produit à crafter\n"
              "• Indiquez la quantité\n"
              "• Le produit est ajouté au coffre\n"
              "• Vos stats personnelles sont mises à jour\n"
              "• Une annonce est publiée dans le channel commande",
        inline=False
    )
    
    embed2.add_field(
        name="💰 /vente",
        value="**Enregistrer une vente client**\n"
              "• Sélectionnez le produit vendu\n"
              "• Indiquez la quantité vendue\n"
              "• Uploadez une capture d'écran de la facture\n"
              "• Le produit est retiré du coffre\n"
              "• L'argent est comptabilisé\n"
              "• Vos stats sont mises à jour",
        inline=False
    )
    
    embed2.add_field(
        name="🗄️ /coffre",
        value="**Afficher l'inventaire du coffre**\n"
              "• Voir tous les produits disponibles\n"
              "• Quantité en stock pour chaque produit\n"
              "• Prix unitaire de chaque produit\n"
              "• Mise à jour automatique après craft/vente",
        inline=False
    )
    
    embed2.set_footer(text="Page 2/4 - Commandes Employés")
    
    # Page 3 - Commandes Gestion
    embed3 = discord.Embed(
        title="⚙️ Commandes Gestion",
        color=discord.Color.gold()
    )
    
    embed3.add_field(
        name="👤 /employer",
        value="**Embaucher un nouveau membre**\n"
              "• Créer un channel privé pour l'employé\n"
              "• Attribuer les rôles employés\n"
              "• Envoyer un message de bienvenue\n"
              "• Expliquer les commandes /craft et /vente",
        inline=False
    )
    
    embed3.add_field(
        name="🚫 /virer",
        value="**Virer un employé**\n"
              "• Enlever tous les rôles employés\n"
              "• Supprimer le préfixe du pseudo\n"
              "• Fermer son channel personnel",
        inline=False
    )
    
    embed3.add_field(
        name="📊 /info",
        value="**Statistiques détaillées des employés**\n"
              "• Nombre de crafts par employé\n"
              "• Nombre de ventes par employé\n"
              "• Nombre de commandes traitées\n"
              "• Classement des meilleurs employés",
        inline=False
    )
    
    embed3.add_field(
        name="📈 /total",
        value="**Résumé global**\n"
              "• Total des crafts de tous les employés\n"
              "• Total des ventes de tous les employés\n"
              "• Vue d'ensemble de l'activité",
        inline=False
    )
    
    embed3.add_field(
        name="💵 /paye",
        value="**Calculer les salaires**\n"
              "• Salaire basé sur les crafts et ventes\n"
              "• 15$ par craft\n"
              "• 25$ par vente\n"
              "• Total pour chaque employé",
        inline=False
    )
    
    embed3.add_field(
        name="🔄 /update",
        value="**Mettre à jour le message du coffre**\n"
              "• Force la mise à jour de l'affichage\n"
              "• Rafraîchir l'inventaire",
        inline=False
    )
    
    embed3.add_field(
        name="⚠️ /reset",
        value="**Réinitialiser les statistiques**\n"
              "• Efface toutes les stats des employés\n"
              "• Le coffre n'est pas modifié\n"
              "• Action irréversible",
        inline=False
    )
    
    embed3.set_footer(text="Page 3/4 - Commandes Gestion")
    
    # Page 4 - Système de Recrutement et Commandes
    embed4 = discord.Embed(
        title="🎫 Systèmes Automatiques",
        color=discord.Color.green()
    )
    
    embed4.add_field(
        name="📝 /rc - Système de Recrutement",
        value="**Panneau de candidature automatique**\n"
              "• Bouton pour candidater\n"
              "• Formulaire de 10 questions automatique\n"
              "• Upload de pièce d'identité\n"
              "• Envoi automatique à la modération\n"
              "• Boutons accepter/refuser\n"
              "• Messages automatiques au candidat\n"
              "• Attribution automatique des rôles",
        inline=False
    )
    
    embed4.add_field(
        name="🍰 Système de Commande Client",
        value="**Via le bouton 'Commander'**\n"
              "• Création d'un ticket privé client\n"
              "• Menu déroulant de produits\n"
              "• Sélection de quantités\n"
              "• Calcul automatique du prix total\n"
              "• Envoi de la commande aux employés\n"
              "• Bouton pour prendre en charge\n"
              "• Création d'un channel de livraison\n"
              "• Bouton de validation de livraison",
        inline=False
    )
    
    embed4.add_field(
        name="📋 Système de Contrat",
        value="**Via le bouton 'Contrat'**\n"
              "• Création d'un ticket privé\n"
              "• Permet de discuter des contrats\n"
              "• Gestion personnalisée",
        inline=False
    )
    
    embed4.add_field(
        name="💡 Fonctionnalités Automatiques",
        value="• **Mise à jour du coffre en temps réel**\n"
              "• **Notifications dans le channel commande**\n"
              "• **Sauvegarde automatique des données**\n"
              "• **Messages privés automatiques**\n"
              "• **Gestion des tickets automatique**",
        inline=False
    )
    
    embed4.set_footer(text="Page 4/4 - Systèmes Automatiques")
    
    # Envoyer tous les embeds
    await interaction.response.send_message(embed=embed1, ephemeral=False)
    await interaction.followup.send(embed=embed2, ephemeral=False)
    await interaction.followup.send(embed=embed3, ephemeral=False)
    await interaction.followup.send(embed=embed4, ephemeral=False)

# ==================== COMMANDE /HELP ====================

@bot.tree.command(name="help", description="Afficher l'aide complète du bot avec toutes les commandes")
@app_commands.checks.has_permissions(administrator=True)
async def help_command(interaction: discord.Interaction):
    """Afficher le guide complet du bot avec liste de toutes les commandes"""
    
    # Page 1 - Vue d'ensemble et liste des commandes
    embed1 = discord.Embed(
        title="📖 Aide - Bot Uwu Café",
        description="**Bienvenue dans le système du café !**\n\n"
                   "Voici toutes les commandes disponibles organisées par catégorie.",
        color=discord.Color.purple()
    )
    
    embed1.add_field(
        name="👨‍💼 Commandes Employés",
        value="• `/craft` - Créer des produits pour le coffre\n"
              "• `/vente` - Enregistrer une vente client\n"
              "• `/coffre` - Voir l'inventaire actuel\n"
              "• `/total` - Voir vos statistiques personnelles\n"
              "• `/info` - Statistiques de tous les employés",
        inline=False
    )
    
    embed1.add_field(
        name="⚙️ Commandes Gestion",
        value="• `/employer` - Embaucher un nouveau membre\n"
              "• `/virer` - Renvoyer un employé\n"
              "• `/paye` - Calculer les salaires\n"
              "• `/update` - Mettre à jour le coffre\n"
              "• `/reset` - Réinitialiser les stats",
        inline=False
    )
    
    embed1.add_field(
        name="📚 Commandes d'Aide",
        value="• `/help` - Cette aide (vue d'ensemble)\n"
              "• `/manuel` - Guide détaillé complet\n"
              "• `/guide` - Guide rapide /craft et /vente\n"
              "• `/rc` - Panneau de recrutement",
        inline=False
    )
    
    embed1.add_field(
        name="🎫 Systèmes Automatiques",
        value="• **Bouton Candidater** - Formulaire de recrutement\n"
              "• **Bouton Commander** - Système de commande client\n"
              "• **Bouton Contrat** - Demande de contrat\n"
              "• **Prise en charge** - Channel <#1464356444940931231>",
        inline=False
    )
    
    embed1.set_footer(text="💡 Tapez /manuel pour un guide détaillé de chaque commande !")
    
    await interaction.response.send_message(embed=embed1, ephemeral=False)

# ==================== COMMANDE /GUIDE ====================

@bot.tree.command(name="guide", description="Guide des commandes employé (/craft et /vente)")
@app_commands.checks.has_permissions(administrator=True)
async def guide(interaction: discord.Interaction):
    """Afficher le guide des commandes employé"""
    
    embed_commandes = discord.Embed(
        title="📋 Commandes Disponibles",
        description="Voici les commandes que vous pouvez utiliser :",
        color=discord.Color.blue()
    )
    
    embed_commandes.add_field(
        name="☕ /craft",
        value="**Craft des produits pour le coffre**\n"
              "Cette commande vous permet de créer des produits et de les ajouter au coffre du café.\n"
              "• Sélectionnez le produit à crafter\n"
              "• Indiquez la quantité\n"
              "• Les produits seront ajoutés à votre compteur personnel et au coffre général\n"
              "• Votre progression sera trackée dans vos statistiques",
        inline=False
    )
    
    embed_commandes.add_field(
        name="💰 /vente",
        value="**Vendre des produits aux clients**\n"
              "Cette commande vous permet d'enregistrer une vente.\n"
              "• Sélectionnez le produit vendu\n"
              "• Indiquez la quantité vendue\n"
              "• Les produits seront retirés du coffre\n"
              "• L'argent gagné sera comptabilisé\n"
              "• Vos ventes seront enregistrées dans vos statistiques",
        inline=False
    )
    
    embed_commandes.add_field(
        name="📢 À propos du channel commande",
        value=f"Le **channel commande** est l'endroit où toutes vos actions sont enregistrées publiquement.\n"
              f"• Chaque `/craft` et `/vente` y est automatiquement annoncé\n"
              f"• Cela permet à l'équipe de voir l'activité en temps réel\n"
              f"• C'est un outil de transparence et de suivi",
        inline=False
    )
    
    embed_commandes.set_footer(text="💡 Utilisez ces commandes pour contribuer au café !")
    
    await interaction.response.send_message(embed=embed_commandes, ephemeral=False)

# ==================== CONFIGURATION DES CHANNELS ET ROLES ====================

ANNOUNCEMENT_CHANNEL = 1407470188248436797
CV_SUBMISSION_CHANNEL = 1407470188248436801
MODERATION_CHANNEL = 1464307411434213569
ID_CARD_STORAGE = 1436821324071702609
CONTRACT_CATEGORY = 1410396669907832953
ORDER_CHANNEL = 1464356444940931231
EMPLOYEE_CATEGORY = 1438632483158491196

ACCEPTED_ROLE_ID = 1407470187212439662
WAITING_RC_ROLE_ID = 1407470187212439662
WAITING_INTERVIEW_CHANNEL = 1464308111987703909
EMPLOYEE_ROLE_1 = 0  # TODO: Remplacer si necessaire
EMPLOYEE_ROLE_2 = 0  # TODO: Remplacer si necessaire
EMPLOYEE_ROLE_1 = 1407470187221094461
EMPLOYEE_ROLE_2 = 1407470187221094467

# Stockage des données CV
cv_data_storage = {}

# ==================== QUESTIONS CV ====================

CV_QUESTIONS = [
    "**Question 1/10** 📝\nQuel est votre **nom et prénom** ?",
    "**Question 2/10** 🎂\nQuel est votre **âge (RP)** ?",
    "**Question 3/10** 📱\nQuel est votre **numéro de téléphone** ?",
    "**Question 4/10** 💼\nQuels sont vos **métiers précédents / expérience** ?",
    "**Question 5/10** ✨\nQuelles sont vos **motivations** pour rejoindre Uwu Café ?",
    "**Question 6/10** 🏙️\nQuelle est votre **ancienneté en ville** ?",
    "**Question 7/10** 🎮\nQuel est votre **âge HRP** ?",
    "**Question 8/10** ⏰\nCombien avez-vous de **total heures** sur le serveur ?",
    "**Question 9/10** 🚗\nAvez-vous des **permis** ? Si oui, lesquels ?",
    "**Question 10/10** 🆔\nEnvoyez votre **pièce d'identité** (capture d'écran)"
]

# ==================== SYSTÈME DE RECRUTEMENT ====================

class ApplyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📝 Candidater", style=discord.ButtonStyle.primary, custom_id="candidater_btn")
    async def candidater(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        cv_category = discord.utils.get(guild.categories, id=CV_SUBMISSION_CHANNEL)
        
        # Créer un ticket pour la candidature
        ticket_channel = await guild.create_text_channel(
            name=f"cv-{interaction.user.name}",
            category=cv_category,
            topic=f"Candidature de {interaction.user.name}"
        )
        
        # Permissions du ticket
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        
        # Initialiser les données CV
        cv_data_storage[interaction.user.id] = {
            "user": interaction.user,
            "channel": ticket_channel,
            "answers": [],
            "question_index": 0
        }
        
        # Envoyer la première question
        embed = discord.Embed(
            title="📋 Candidature Uwu Café",
            description=CV_QUESTIONS[0],
            color=discord.Color.blue()
        )
        await ticket_channel.send(f"{interaction.user.mention}", embed=embed)
        
        await interaction.response.send_message(
            f"✅ Votre ticket de candidature a été créé: {ticket_channel.mention}",
            ephemeral=True
        )
    
    @discord.ui.button(label="📄 Contrat", style=discord.ButtonStyle.secondary, custom_id="contrat_btn")
    async def contrat(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        contract_category = discord.utils.get(guild.categories, id=CONTRACT_CATEGORY)
        
        # Créer un ticket pour le contrat
        ticket_channel = await guild.create_text_channel(
            name=f"contrat-{interaction.user.name}",
            category=contract_category,
            topic=f"Contrat de {interaction.user.name}"
        )
        
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        
        embed = discord.Embed(
            title="📄 Demande de Contrat",
            description=f"Ticket ouvert pour {interaction.user.mention}\n\nUn membre du staff va vous aider.",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed)
        
        await interaction.response.send_message(
            f"✅ Votre ticket de contrat a été créé: {ticket_channel.mention}",
            ephemeral=True
        )
    
    @discord.ui.button(label="🛒 Commander", style=discord.ButtonStyle.success, custom_id="commander_btn")
    async def commander(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        
        # Créer un ticket de commande privé
        ticket_channel = await guild.create_text_channel(
            name=f"commande-{interaction.user.name}",
            topic=f"Commande de {interaction.user.name}"
        )
        
        # Permissions: seulement l'utilisateur peut voir
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        
        # Embed de bienvenue dans le ticket
        embed = discord.Embed(
            title="🛒 Nouvelle Commande",
            description=f"Bienvenue {interaction.user.mention} !\n\n"
                       "Sélectionnez les produits que vous souhaitez commander ci-dessous.\n"
                       "Vous pouvez commander plusieurs produits.",
            color=discord.Color.gold()
        )
        
        # Créer la vue avec le sélecteur de produits pour commande
        view = ProductSelectView(interaction.user, ticket_channel, {})
        await ticket_channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(
            f"✅ Votre ticket de commande a été créé: {ticket_channel.mention}",
            ephemeral=True
        )

class ProductSelectView(discord.ui.View):
    """Vue pour sélectionner un produit"""
    
    def __init__(self, user: discord.User, channel: discord.TextChannel, order: dict):
        super().__init__()
        self.user = user
        self.channel = channel
        self.order = order
    
    @discord.ui.select(
        placeholder="Choisissez un produit",
        options=[discord.SelectOption(label=f"{product} - {price}$", value=product) for product, price in PRODUITS.items()]
    )
    async def product_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Sélectionner un produit"""
        product = select.values[0]
        
        # Créer le modal pour la quantité
        modal = QuantityModal_Order(self, product)
        await interaction.response.send_modal(modal)
    
    async def on_quantity_submit(self, product: str, quantity: int, interaction: discord.Interaction):
        """Traiter la quantité saisie"""
        # Ajouter à la commande
        if product not in self.order:
            self.order[product] = 0
        self.order[product] += quantity
        
        # Calculer le prix
        price = PRODUITS[product] * quantity
        
        # Afficher la confirmation
        order_text = "\n".join([f"• {prod} x{qty} = {PRODUITS[prod] * qty}$" for prod, qty in self.order.items()])
        total_price = sum(PRODUITS[prod] * qty for prod, qty in self.order.items())
        
        embed = discord.Embed(
            title="🛒 Votre commande",
            description=order_text,
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="💰 Total",
            value=f"**{total_price}$**",
            inline=False
        )
        
        # Boutons pour continuer ou valider
        view = OrderActionView(self.user, self.channel, self.order)
        await self.channel.send(embed=embed, view=view)

class QuantityModal_Order(discord.ui.Modal, title="Quantité"):
    """Modal pour entrer la quantité d'un produit"""
    
    def __init__(self, parent_view: ProductSelectView, product: str):
        super().__init__()
        self.parent_view = parent_view
        self.product = product
    
    quantity_input = discord.ui.TextInput(
        label="Quantité",
        placeholder="Entrez la quantité souhaitée",
        required=True,
        min_length=1,
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            quantity = int(self.quantity_input.value)
            if quantity <= 0:
                await interaction.response.send_message(
                    "❌ La quantité doit être supérieure à 0!",
                    ephemeral=False
                )
                return
            
            await interaction.response.defer()
            await self.parent_view.on_quantity_submit(self.product, quantity, interaction)
        except ValueError:
            await interaction.response.send_message(
                "❌ Veuillez entrer un nombre valide!",
                ephemeral=False
            )

class OrderActionView(discord.ui.View):
    """Boutons pour gérer la commande"""
    
    def __init__(self, user: discord.User, channel: discord.TextChannel, order: dict):
        super().__init__()
        self.user = user
        self.channel = channel
        self.order = order
    
    @discord.ui.button(label="➕ Ajouter un produit", style=discord.ButtonStyle.primary)
    async def add_product(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ajouter un autre produit"""
        await interaction.response.defer()
        
        view = ProductSelectView(self.user, self.channel, self.order)
        embed = discord.Embed(
            title="📦 Sélectionnez un autre produit",
            description="Cliquez sur le menu déroulant",
            color=discord.Color.gold()
        )
        
        await self.channel.send(embed=embed, view=view)
    
    @discord.ui.button(label="✅ Valider", style=discord.ButtonStyle.success)
    async def validate_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Valider la commande"""
        await interaction.response.defer()
        
        # RETIRER DU COFFRE
        global coffre_inventory
        for product, qty in self.order.items():
            if product not in coffre_inventory:
                coffre_inventory[product] = 0
            coffre_inventory[product] -= qty
        save_coffre(coffre_inventory)
        await update_coffre_message()
        
        # Créer le résumé de commande avec prix
        order_text = "\n".join([f"• {product} x{qty} = {PRODUITS[product] * qty}$" for product, qty in self.order.items()])
        total_price = sum(PRODUITS[product] * qty for product, qty in self.order.items())
        
        embed = discord.Embed(
            title="🎉 Commande validée !",
            description=f"Voici votre commande :\n\n{order_text}",
            color=discord.Color.green()
        )
        embed.add_field(
            name="💰 Total à payer",
            value=f"**{total_price}$**",
            inline=False
        )
        embed.set_footer(text="Un employé prendra bientôt en charge votre commande")
        await self.channel.send(embed=embed)
        
        # Envoyer un message privé au client
        try:
            dm_embed = discord.Embed(
                title="📦 Résumé de votre commande",
                description=f"Bonjour {self.user.mention} !\n\nVoici le détail de votre commande :",
                color=discord.Color.blurple()
            )
            dm_embed.add_field(
                name="Produits commandés",
                value=order_text,
                inline=False
            )
            dm_embed.add_field(
                name="💰 Montant Total",
                value=f"**{total_price}$**",
                inline=False
            )
            dm_embed.add_field(
                name="📋 Statut",
                value="Un employé se chargera bientôt de votre commande. Vérifiez sur le Discord, un channel sera créé pour vous !",
                inline=False
            )
            
            await self.user.send(embed=dm_embed)
        except Exception as e:
            print(f"Impossible d'envoyer le DM: {e}")
        
        # Envoyer la commande au channel des employés
        try:
            guild = self.channel.guild
            order_channel = guild.get_channel(ORDER_CHANNEL)
            
            if order_channel:
                embed_order = discord.Embed(
                    title="🆕 Nouvelle Commande",
                    description=f"Commande de {self.user.mention}\n\n{order_text}",
                    color=discord.Color.gold()
                )
                embed_order.add_field(
                    name="Client",
                    value=f"{self.user.name} ({self.user.mention})",
                    inline=True
                )
                embed_order.add_field(
                    name="💰 Total",
                    value=f"**{total_price}$**",
                    inline=True
                )
                embed_order.add_field(
                    name="Ticket",
                    value=f"{self.channel.mention}",
                    inline=True
                )
                
                # Bouton pour prendre en charge
                view = OrderStatusView(self.user, guild, order_text, total_price)
                # Ping @everyone pour notifier les employés
                order_message = await order_channel.send(content="@everyone", embed=embed_order, view=view)
                view.order_message = order_message
                
                # Confirmer à l'utilisateur que sa commande a été envoyée
                confirm_embed = discord.Embed(
                    title="✅ Commande envoyée !",
                    description="Votre commande a été envoyée aux employés.\n\nUn employé la prendra en charge très bientôt et un channel privé sera créé pour vous.",
                    color=discord.Color.green()
                )
                await self.channel.send(embed=confirm_embed)
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande au channel: {e}")
        
        # Attendre 3 secondes puis fermer le channel de commande
        await asyncio.sleep(3)
        try:
            await self.channel.delete()
        except Exception as e:
            print(f"Erreur lors de la fermeture du channel de commande: {e}")

class OrderStatusView(discord.ui.View):
    """Vue pour gérer la prise en charge des commandes"""
    
    def __init__(self, customer: discord.User, guild: discord.Guild, order_text: str, total_price: int = 0):
        super().__init__()
        self.customer = customer
        self.guild = guild
        self.order_text = order_text
        self.total_price = total_price
        self.order_message = None
    
    @discord.ui.button(label="✋ Prendre en charge", style=discord.ButtonStyle.success)
    async def take_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Un employé prend en charge la commande"""
        await interaction.response.defer()
        
        try:
            employee = interaction.user
            
            # METTRE À JOUR LES STATS - 1 commande prise
            await update_employee_stat(employee.id, employee.name, "commandes", 1)
            
            # Créer un salon privé avec le client et l'employé
            overwrites = {
                self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self.customer: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                employee: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                self.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            ticket_channel = await self.guild.create_text_channel(
                name=f"livraison-{self.customer.name}-{employee.name}",
                overwrites=overwrites,
                category=None
            )
            
            # Message de bienvenue
            embed = discord.Embed(
                title="🍰 Ticket de Livraison",
                description=f"Employé: {employee.mention}\nClient: {self.customer.mention}",
                color=discord.Color.blurple()
            )
            
            embed.add_field(
                name="📦 Commande",
                value=self.order_text,
                inline=False
            )
            
            embed.add_field(
                name="💰 Total à payer",
                value=f"**{self.total_price}$**",
                inline=False
            )
            
            embed.add_field(
                name="💬 Communication",
                value="Vous pouvez discuter de l'arrangement de la livraison ici",
                inline=False
            )
            
            await ticket_channel.send(embed=embed)
            
            # Notifier les participants
            await ticket_channel.send(f"✅ {employee.mention} a pris en charge la commande de {self.customer.mention}!")
            
            # Ajouter le bouton d'accomplissement
            view = DeliveryCompleteView(ticket_channel, self.order_message, self.customer, self.order_text, self.total_price)
            embed_complete = discord.Embed(
                title="📋 Actions",
                description="Cliquez sur le bouton ci-dessous quand la livraison est effectuée",
                color=discord.Color.green()
            )
            await ticket_channel.send(embed=embed_complete, view=view)
            
            # Supprimer le channel de commande original du client
            try:
                # Chercher le channel de commande par nom
                channel_name = f"commande-{self.customer.name}"
                for guild_channel in self.guild.channels:
                    if guild_channel.name == channel_name:
                        await guild_channel.delete()
                        print(f"Channel de commande {channel_name} supprimé")
                        break
            except Exception as e:
                print(f"Impossible de supprimer le channel de commande: {e}")
            
            # Modifier le message original pour montrer que c'est en cours
            embed_updated = discord.Embed(
                title="🆕 Nouvelle Commande",
                description=f"Commande de {self.customer.mention}\n\n{self.order_text}",
                color=discord.Color.yellow()
            )
            embed_updated.add_field(
                name="Client",
                value=f"{self.customer.name} ({self.customer.mention})",
                inline=True
            )
            embed_updated.add_field(
                name="Employé",
                value=f"{employee.name} ({employee.mention})",
                inline=True
            )
            embed_updated.add_field(
                name="Statut",
                value="✅ En cours",
                inline=False
            )
            embed_updated.add_field(
                name="Ticket",
                value=f"{ticket_channel.mention}",
                inline=False
            )
            
            # Mettre à jour le message original si disponible
            if self.order_message:
                await self.order_message.edit(embed=embed_updated, view=None)
            else:
                await interaction.message.edit(embed=embed_updated, view=None)
            
            # Confirmer la prise en charge à l'employé
            await interaction.followup.send(
                f"✅ Vous avez pris en charge la commande ! Un channel privé a été créé: {ticket_channel.mention}",
                ephemeral=False
            )

        except Exception as e:
            print(f"Erreur lors de la prise en charge de la commande: {e}")
            await interaction.followup.send(f"❌ Erreur: {e}", ephemeral=False)

class DeliveryCompleteView(discord.ui.View):
    """Vue pour compléter la livraison"""
    
    def __init__(self, ticket_channel: discord.TextChannel, order_message: discord.Message = None, customer: discord.User = None, order_text: str = "", total_price: int = 0):
        super().__init__()
        self.ticket_channel = ticket_channel
        self.order_message = order_message
        self.customer = customer
        self.order_text = order_text
        self.total_price = total_price
    
    @discord.ui.button(label="✅ Effectuer", style=discord.ButtonStyle.success)
    async def complete_delivery(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Marquer la livraison comme effectuée"""
        await interaction.response.defer()
        
        try:
            employee = interaction.user
            
            # Mettre à jour le message de commande original
            if self.order_message:
                try:
                    # Créer un nouvel embed avec le statut "Effectué"
                    new_embed = discord.Embed(
                        title="✅ Commande Effectuée",
                        description=f"Commande de {self.customer.mention}\n\n{self.order_text}",
                        color=discord.Color.green()
                    )
                    new_embed.add_field(
                        name="Client",
                        value=f"{self.customer.name} ({self.customer.mention})",
                        inline=True
                    )
                    new_embed.add_field(
                        name="Employé",
                        value=f"{employee.name} ({employee.mention})",
                        inline=True
                    )
                    new_embed.add_field(
                        name="💰 Total",
                        value=f"**{self.total_price}$**",
                        inline=True
                    )
                    new_embed.add_field(
                        name="Statut",
                        value="✅ Effectué",
                        inline=False
                    )
                    
                    await self.order_message.edit(embed=new_embed, view=None)
                except Exception as e:
                    print(f"Erreur lors de la mise à jour du message: {e}")
            
            # Envoyer un message de confirmation
            embed = discord.Embed(
                title="🎉 Commande Effectuée !",
                description="La livraison a été marquée comme terminée.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Effectué par {employee.name}")
            
            await self.ticket_channel.send(embed=embed)
            
            # Attendre 3 secondes avant de fermer le channel
            await asyncio.sleep(3)
            
            # Supprimer le channel
            await self.ticket_channel.delete()
            
        except Exception as e:
            print(f"Erreur lors de la fermeture du channel: {e}")
            await interaction.followup.send(f"❌ Erreur: {e}", ephemeral=False)

class DecisionView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)
        self.user_data = user_data
    
    @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.green, custom_id="accept_cv")
    async def accepter(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Defer pour eviter l'expiration
        await interaction.response.defer(ephemeral=False)
        
        user = self.user_data["user"]
        guild = interaction.guild

        # Attribuer le role
        role = guild.get_role(1407470187212439662)
        if role:
            try:
                await user.add_roles(role)
            except Exception as e:
                print(f"Erreur lors de l'attribution du role: {e}")

        # Envoyer la carte d'identite dans ID_CARD_STORAGE
        try:
            if interaction.message.embeds and interaction.message.embeds[0].image:
                id_url = interaction.message.embeds[0].image.url

                async with aiohttp.ClientSession() as session:
                    async with session.get(id_url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image_file = discord.File(
                                BytesIO(image_data),
                                filename=f"id_{user.name}.png"
                            )

                            storage_channel = guild.get_channel(ID_CARD_STORAGE)
                            if storage_channel:
                                await storage_channel.send(
                                    f"**✅ Piece d'identite de {user.mention}** (Accepte - En attente RC)",
                                    file=image_file
                                )
        except Exception as e:
            print(f"Erreur lors de l'envoi de la carte d'identite: {e}")

        # Channel d'attente
        waiting_channel = guild.get_channel(1464308111987703909)
        waiting_channel_mention = waiting_channel.mention if waiting_channel else "le salon d'attente"

        # Envoyer un message de log dans MODERATION_CHANNEL
        try:
            moderation_channel = guild.get_channel(MODERATION_CHANNEL)
            if moderation_channel:
                log_embed = discord.Embed(
                    title="✅ Candidature Acceptee - En attente RC",
                    description=f"**Candidat:** {user.mention} ({user.name})\n"
                               f"**Accepte par:** {interaction.user.mention}\n"
                               f"**Statut:** En attente d'entretien\n"
                               f"**Channel d'attente:** {waiting_channel_mention}",
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                await moderation_channel.send(embed=log_embed)
        except Exception as e:
            print(f"Erreur lors de l'envoi du log: {e}")

        # Modifier l'embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.orange()
        embed.title = "✅ Candidature Acceptee - En attente RC"

        # Desactiver les boutons
        for item in self.children:
            item.disabled = True

        await interaction.message.edit(embed=embed, view=self)

        # DM au candidat
        try:
            dm_message = (
                f"🎉 **Felicitations !**\n\n"
                f"Votre candidature pour **Uwu Cafe** a ete **acceptee** !\n\n"
                f"Vous etes maintenant en attente d'entretien.\n"
                f"Veuillez vous rendre dans le salon {waiting_channel_mention} pour mettre vos disponibilites."
            )
            await user.send(dm_message)
        except Exception as e:
            print(f"Erreur lors de l'envoi du DM: {e}")

        # Supprimer le ticket CV
        try:
            cv_channel = self.user_data.get("channel")
            if cv_channel and isinstance(cv_channel, discord.TextChannel):
                await cv_channel.delete()
                print(f"Ticket CV {cv_channel.name} supprime")
        except Exception as e:
            print(f"Erreur lors de la suppression du ticket CV: {e}")

        # Confirmation
        await interaction.followup.send(
            f"✅ Candidature de {user.mention} acceptee ! Role attribue et redirige vers {waiting_channel_mention}",
            ephemeral=False
        )


    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red, custom_id="reject_cv")
    async def refuser(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = self.user_data["user"]
        guild = interaction.guild
        
        # Envoyer un message de log dans MODERATION_CHANNEL
        try:
            moderation_channel = guild.get_channel(MODERATION_CHANNEL)
            if moderation_channel:
                log_embed = discord.Embed(
                    title="❌ Candidature Refusée",
                    description=f"**Candidat:** {user.mention} ({user.name})\n"
                               f"**Refusé par:** {interaction.user.mention}",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                await moderation_channel.send(embed=log_embed)
        except Exception as e:
            print(f"Erreur lors de l'envoi du log: {e}")
        
        # Modifier l'embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "❌ Candidature Refusée"
        
        # Désactiver les boutons
        for item in self.children:
            item.disabled = True
        
        await interaction.message.edit(embed=embed, view=self)
        
        # DM au candidat
        try:
            await user.send(
                f"❌ **Candidature Refusée**\n\n"
                f"Nous sommes désolés, mais votre candidature pour Uwu Café n'a pas été retenue.\n"
                f"N'hésitez pas à retenter votre chance ultérieurement !\n\n"
                f"Merci pour votre intérêt. 🙏"
            )
        except:
            pass
        
        # Supprimer le ticket CV
        try:
            ticket_channel_name = f"cv-{user.name}"
            for channel in guild.channels:
                if channel.name == ticket_channel_name:
                    await channel.delete()
                    print(f"Ticket CV {ticket_channel_name} supprimé")
                    break
        except Exception as e:
            print(f"Erreur lors de la suppression du ticket CV: {e}")
        
        await interaction.response.send_message(
            f"❌ Candidature de {user.mention} refusée.",
            ephemeral=False
        )

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author.bot:
        return
    
    # Commande .payes
    if message.content.lower() == ".payes":
        stats = load_stats()
        
        if not stats:
            await message.channel.send("📊 Aucune donnée de crafts disponible.")
            return
        
        embed = discord.Embed(
            title="💰 Calcul des Salaires - Uwu Café",
            description="**Système de paiement:**\n"
                       "• Quota de base: **600 crafts** = 1.500.000$\n"
                       "• Bonus: tous les **50 crafts** supplémentaires = +125.000$",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        total_payes = 0
        
        # Trier par crafts
        sorted_by_crafts = sorted(
            stats.items(),
            key=lambda x: x[1]["crafts"],
            reverse=True
        )
        
        for user_id, data in sorted_by_crafts:
            crafts = data["crafts"]
            
            if crafts >= 600:
                # Salaire de base
                salaire = 1500000
                
                # Calcul des bonus (crafts au-dessus de 600)
                crafts_bonus = crafts - 600
                nombre_bonus = crafts_bonus // 50
                salaire += nombre_bonus * 125000
                
                total_payes += salaire
                
                # Formater le salaire avec des espaces
                salaire_formatte = f"{salaire:,}".replace(",", " ")
                
                status = "✅ Quota atteint"
                if nombre_bonus > 0:
                    status += f" + {nombre_bonus} bonus"
            else:
                # Pas encore le quota
                salaire = 0
                salaire_formatte = "0"
                restant = 600 - crafts
                status = f"❌ Quota non atteint ({restant} crafts restants)"
            
            embed.add_field(
                name=f"👤 {data['name']}",
                value=f"🛠️ Crafts: **{crafts}**\n"
                      f"💵 Salaire: **{salaire_formatte}$**\n"
                      f"{status}",
                inline=True
            )
        
        total_formatte = f"{total_payes:,}".replace(",", " ")
        embed.set_footer(text=f"Total à payer: {total_formatte}$")
        
        await message.channel.send(embed=embed)
        return
    
    # Vérifier si c'est une réponse à une question CV
    user_id = message.author.id
    if user_id in cv_data_storage:
        data = cv_data_storage[user_id]
        
        # Vérifier que c'est dans le bon channel
        if message.channel.id != data["channel"].id:
            return
        
        question_index = data["question_index"]
        
        # Si c'est la dernière question (pièce d'identité)
        if question_index == 9:
            if len(message.attachments) == 0:
                await message.channel.send("❌ Veuillez envoyer une image de votre pièce d'identité !")
                return
            
            # Sauvegarder la pièce d'identité
            attachment = message.attachments[0]
            data["answers"].append(f"[Pièce d'identité]({attachment.url})")
            
            # Créer l'embed pour la modération
            embed = discord.Embed(
                title="📨 Nouvelle Candidature - Uwu Café",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            
            questions_labels = [
                "👤 Nom et Prénom",
                "🎂 Âge (RP)",
                "📱 Numéro de téléphone",
                "💼 Expérience",
                "✨ Motivations",
                "🏙️ Ancienneté",
                "🎮 Âge HRP",
                "⏰ Total heures",
                "🚗 Permis",
                "🆔 Pièce d'identité"
            ]
            
            for i, (label, answer) in enumerate(zip(questions_labels, data["answers"])):
                embed.add_field(name=label, value=answer, inline=False)
            
            embed.set_footer(
                text=f"Candidature de {message.author.name}",
                icon_url=message.author.display_avatar.url
            )
            embed.set_image(url=attachment.url)
            
            # Envoyer au channel de modération
            moderation_channel = bot.get_channel(MODERATION_CHANNEL)
            if moderation_channel:
                view = DecisionView(data)
                # Ping du rôle de modération
                role_mention = f"<@&1407470187221094467>"
                await moderation_channel.send(
                    f"{role_mention}\n**Nouvelle candidature de {message.author.mention}**",
                    embed=embed,
                    view=view
                )
            
            # Message de confirmation
            await message.channel.send(
                embed=discord.Embed(
                    title="✅ Candidature Envoyée !",
                    description="Votre candidature a été envoyée à l'équipe de modération.\n"
                               "Vous recevrez une réponse prochainement !",
                    color=discord.Color.green()
                )
            )
            
            # Fermer le ticket après 10 secondes
            await message.channel.send("Ce ticket va se fermer dans 10 secondes...")
            await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=10))
            await message.channel.delete()
            
            # Nettoyer les données
            del cv_data_storage[user_id]
        
        else:
            # Sauvegarder la réponse
            data["answers"].append(message.content)
            
            # Si c'est la première question (nom/prénom), renommer le channel ET l'utilisateur
            if data["question_index"] == 0:
                try:
                    nom_propre = message.content.lower().replace(" ", "-")
                    # Limiter à 100 caractères et enlever les caractères spéciaux
                    nom_propre = "".join(c for c in nom_propre if c.isalnum() or c == "-")[:100]
                    new_name = f"cv-{nom_propre}"
                    await message.channel.edit(name=new_name)
                    
                    # Renommer aussi le membre avec son nom/prénom
                    try:
                        await message.author.edit(nick=message.content[:32])  # Discord limite à 32 caractères
                    except Exception as e:
                        print(f"Erreur lors du renommage du membre: {e}")
                except Exception as e:
                    print(f"Erreur lors du renommage du channel: {e}")
            
            # Passer a la question suivante
            data["question_index"] += 1

            if data["question_index"] < len(CV_QUESTIONS):
                embed = discord.Embed(
                    title="📋 Candidature Uwu Café",
                    description=CV_QUESTIONS[data["question_index"]],
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
    
    await bot.process_commands(message)

@bot.tree.command(name="rc", description="Afficher le panneau de recrutement Uwu Café")
@app_commands.checks.has_permissions(administrator=True)
async def rc(interaction: discord.Interaction):
    """Commande pour afficher le panneau de recrutement"""
    
    # Embed pour le channel d'annonce (sans l'option Candidater)
    embed_announcement = discord.Embed(
        title="# Hey tout le monde ☕💖",
        description="Une nouvelle équipe, une nouvelle énergie, et toujours la même ambiance douce et réconfortante qui fait tout le charme du lieu ✨\n\n"
                   "🍰 **Au programme :**\n"
                   "– Une atmosphère chaleureuse et conviviale 🌷\n"
                   "– Des boissons et douceurs toujours aussi délicieuses 😋\n"
                   "– Des nouveautés à venir très bientôt 👀\n\n"
                   "Le UwU Café revient plus vivant que jamais, prêt à vous accueillir avec le sourire et beaucoup d'amour 💕\n\n"
                   "📍 Venez découvrir votre café préféré dès aujourd'hui et partager un moment tout doux avec nous ✨\n\n"
                   "Avec toute notre tendresse,\n"
                   "L'équipe du Uwu Café ☕💞\n\n# Recrutement on 🟢",
        color=discord.Color.pink()
    )
    
    # Envoyer dans le channel d'annonce sans boutons (juste le message)
    announcement_channel = bot.get_channel(ANNOUNCEMENT_CHANNEL)
    if announcement_channel:
        await announcement_channel.send(content="<@&1407470187212439660>", embed=embed_announcement)
    
    # Embed pour le service client avec les 3 boutons
    embed_service = discord.Embed(
        title="☕ Service Client Uwu Café",
        description="**Choisissez une option ci-dessous :**\n\n"
                   "📝 **Candidater** - Postuler pour rejoindre l'équipe\n"
                   "📄 **Contrat** - Demander un contrat\n"
                   "🛒 **Commander** - Passer une commande",
        color=discord.Color.pink()
    )
    
    # Envoyer dans le channel de CV avec les 3 boutons
    cv_channel = bot.get_channel(CV_SUBMISSION_CHANNEL)
    if cv_channel:
        view = ApplyButton()
        await cv_channel.send(content="<@&1407470187212439660>", embed=embed_service, view=view)
    
    await interaction.response.send_message(
        "✅ Panneau de recrutement publié dans les deux channels !",
        ephemeral=False
    )

# Lancer le bot
if __name__ == "__main__":
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        print("❌ Token Discord manquant! Créez un fichier .env avec BOT_TOKEN=votre_token")
    else:
        bot.run(TOKEN)
