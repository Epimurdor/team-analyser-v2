import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser
from datetime import datetime, timedelta

# --- Configuration ---
# ⚠️ CLÉ API RIOT POUR USAGE PERSONNEL UNIQUEMENT
# ⚠️ RÉGION FIXÉE SUR EUW1 (Europe de l'Ouest)
# NE PAS PARTAGER CE FICHIER OU LE .EXE GÉNÉRÉ !
RIOT_API_KEY = "RGAPI-cc19da24-8034-4cc4-b3fb-d3c215d905e6"
RIOT_REGION = "euw1"  # Région fixée sur EUW1
RIOT_API_BASE = f"https://{RIOT_REGION}.api.riotgames.com"

# Cache pour éviter de refaire des requêtes pour les mêmes PUUIDs ou matchs
summoner_name_cache = {}
match_cache = {}
puuid_cache = {}

# --- Récupérer le PUUID d'un joueur depuis son pseudo + tag ---
def get_puuid_by_name(summoner_name, tag_line):
    # Vérifier si on a déjà le PUUID en cache
    cache_key = f"{summoner_name}#{tag_line}"
    if cache_key in puuid_cache:
        return puuid_cache[cache_key]
    
    # Riot a changé son API : il faut d'abord chercher l'account via le nom + tag
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        puuid = response.json().get("puuid")
        if puuid:
            puuid_cache[cache_key] = puuid
        return puuid
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de trouver le joueur {summoner_name}#{tag_line} : {e}")
        return None

# --- Récupérer le PUUID d'un joueur depuis son nom d'invocateur (ancienne méthode) ---
def get_puuid_by_summoner_name(summoner_name):
    url = f"{RIOT_API_BASE}/lol/summoner/v4/summoners/by-name/{summoner_name}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("puuid")
    except requests.exceptions.RequestException:
        return None

# --- Récupérer l'historique des matchs d'un joueur ---
def get_match_history(puuid, count=20):
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de récupérer l'historique des matchs : {e}")
        return []

# --- Récupérer les infos d'un match ---
def get_match_info(match_id):
    if match_id in match_cache:
        return match_cache[match_id]
    
    url = f"{RIOT_API_BASE}/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        match_data = response.json()
        match_cache[match_id] = match_data
        return match_data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de récupérer le match : {e}")
        return None

# --- Récupérer le nom du joueur depuis son PUUID (avec cache) ---
def get_summoner_name(puuid):
    if puuid in summoner_name_cache:
        return summoner_name_cache[puuid]
    
    url = f"{RIOT_API_BASE}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        name = response.json().get("name", "Inconnu")
        summoner_name_cache[puuid] = name
        return name
    except:
        return "Inconnu"

# --- Analyser le match et extraire les stats ---
def analyze_match(match_data):
    if not match_data:
        return []

    match_info = match_data.get("info", {})
    participants = match_info.get("participants", [])

    stats = []
    for participant in participants:
        puuid = participant.get("puuid")
        summoner_name = get_summoner_name(puuid)

        stats.append({
            "summonerName": summoner_name,
            "championName": participant.get("championName"),
            "kills": participant.get("kills"),
            "deaths": participant.get("deaths"),
            "assists": participant.get("assists"),
            "kda": round((participant.get("kills", 0) + participant.get("assists", 0)) / max(1, participant.get("deaths", 1)), 2),
            "goldEarned": participant.get("goldEarned"),
            "creepScore": participant.get("totalMinionsKilled"),
            "visionScore": participant.get("visionScore"),
            "win": participant.get("win"),
            "teamId": participant.get("teamId"),
            "summonerLevel": participant.get("summonerLevel"),
            "items": participant.get("items", []),
            "spells": [participant.get("summoner1Id"), participant.get("summoner2Id")],
        })

    return stats

# --- Convertir un timestamp Riot en date lisible ---
def format_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime("%d/%m/%Y %H:%M")

# --- Interface Graphique ---
class TeamAnalyserApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🎮 Team Analyser v2 - League of Legends (EUW1)")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Variables
        self.match_id = tk.StringVar()
        self.summoner_name = tk.StringVar()
        self.summoner_tag = tk.StringVar()
        self.stats = []
        self.current_puuid = None
        self.match_history = []

        # --- UI ---
        self.create_widgets()

    def create_widgets(self):
        # Frame pour la recherche par ID de match
        match_search_frame = ttk.LabelFrame(self.root, text="🔍 Rechercher par ID de match (EUW1)", padding=10)
        match_search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(match_search_frame, text="ID du match :").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(match_search_frame, textvariable=self.match_id, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(match_search_frame, text="Analyser", command=self.fetch_match_by_id).grid(row=0, column=2, padx=5)

        # Frame pour la recherche par pseudo + tag
        summoner_search_frame = ttk.LabelFrame(self.root, text="👤 Rechercher par pseudo + tag (EUW1)", padding=10)
        summoner_search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(summoner_search_frame, text="Pseudo :").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(summoner_search_frame, textvariable=self.summoner_name, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(summoner_search_frame, text="Tag :").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(summoner_search_frame, textvariable=self.summoner_tag, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Button(summoner_search_frame, text="Rechercher l'historique", command=self.fetch_match_history).grid(row=0, column=4, padx=5)

        # Avertissement
        warning_frame = ttk.Frame(self.root)
        warning_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(
            warning_frame,
            text="⚠️ Ce logiciel utilise une clé API personnelle (Région: EUW1). NE PAS PARTAGER le .exe ou le code !",
            foreground="red",
            font=("Arial", 9, "bold")
        ).pack()

        # Frame pour l'historique des matchs
        self.history_frame = ttk.LabelFrame(self.root, text="📜 Historique des matchs", padding=10)
        self.history_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        self.history_tree = ttk.Treeview(self.history_frame, columns=(
            "ID", "Date", "Champion", "Résultat", "KDA", "Durée"
        ), show="headings", height=5)
        
        self.history_tree.heading("ID", text="ID du match")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Champion", text="Champion")
        self.history_tree.heading("Résultat", text="Résultat")
        self.history_tree.heading("KDA", text="KDA")
        self.history_tree.heading("Durée", text="Durée")
        
        self.history_tree.column("ID", width=200)
        self.history_tree.column("Date", width=120)
        self.history_tree.column("Champion", width=100)
        self.history_tree.column("Résultat", width=80)
        self.history_tree.column("KDA", width=60)
        self.history_tree.column("Durée", width=80)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar pour l'historique
        history_scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=history_scrollbar.set)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind le double-clic sur un match de l'historique pour afficher ses stats
        self.history_tree.bind("<Double-1>", self.load_match_from_history)

        # Frame pour les résultats
        self.results_frame = ttk.LabelFrame(self.root, text="📊 Résultats du match", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tableau des stats
        self.tree = ttk.Treeview(self.results_frame, columns=(
            "Joueur", "Champion", "Niveau", "K", "D", "A", "KDA", "Gold", "CS", "Vision", "Victoire"
        ), show="headings")

        # Configurer les colonnes
        self.tree.heading("Joueur", text="Joueur")
        self.tree.heading("Champion", text="Champion")
        self.tree.heading("Niveau", text="Niveau")
        self.tree.heading("K", text="Kills")
        self.tree.heading("D", text="Deaths")
        self.tree.heading("A", text="Assists")
        self.tree.heading("KDA", text="KDA")
        self.tree.heading("Gold", text="Gold")
        self.tree.heading("CS", text="CS")
        self.tree.heading("Vision", text="Vision")
        self.tree.heading("Victoire", text="Victoire")

        self.tree.column("Joueur", width=150)
        self.tree.column("Champion", width=120)
        self.tree.column("Niveau", width=60, anchor=tk.CENTER)
        self.tree.column("K", width=50, anchor=tk.CENTER)
        self.tree.column("D", width=50, anchor=tk.CENTER)
        self.tree.column("A", width=50, anchor=tk.CENTER)
        self.tree.column("KDA", width=70, anchor=tk.CENTER)
        self.tree.column("Gold", width=80, anchor=tk.CENTER)
        self.tree.column("CS", width=60, anchor=tk.CENTER)
        self.tree.column("Vision", width=80, anchor=tk.CENTER)
        self.tree.column("Victoire", width=80, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame pour les détails supplémentaires
        self.details_frame = ttk.LabelFrame(self.root, text="📋 Détails du Match", padding=10)
        self.details_frame.pack(fill=tk.X, padx=10, pady=5)
        self.details_label = ttk.Label(self.details_frame, text="Aucun match sélectionné.")
        self.details_label.pack()

        # Bind le clic sur une ligne pour afficher les détails
        self.tree.bind("<<TreeviewSelect>>", self.show_details)

        # Lien pour obtenir une nouvelle clé API si besoin
        ttk.Label(
            self.root,
            text="🔑 Besoin d'une nouvelle clé API ? ",
            cursor="hand2",
            foreground="blue"
        ).pack(pady=5)
        ttk.Label(
            self.root,
            text="https://developer.riotgames.com/",
            cursor="hand2",
            foreground="blue"
        ).pack()

        # Bind le clic sur le lien
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Label) and "riotgames.com" in widget.cget("text"):
                widget.bind("<Button-1>", lambda e: webbrowser.open("https://developer.riotgames.com/"))

    def fetch_match_by_id(self):
        match_id = self.match_id.get().strip()

        if not match_id:
            messagebox.showerror("Erreur", "Veuillez entrer un ID de match.")
            return

        # Effacer les anciens résultats
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.details_label.config(text="Chargement...")

        # Récupérer les données du match
        self.root.config(cursor="wait")
        match_data = get_match_info(match_id)
        if match_data:
            stats = analyze_match(match_data)
            self.display_stats(stats, match_data)
        self.root.config(cursor="")

    def fetch_match_history(self):
        summoner_name = self.summoner_name.get().strip()
        summoner_tag = self.summoner_tag.get().strip()

        if not summoner_name or not summoner_tag:
            messagebox.showerror("Erreur", "Veuillez entrer un pseudo et un tag.")
            return

        # Effacer l'ancien historique
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        self.details_label.config(text=f"Recherche des matchs de {summoner_name}#{summoner_tag}...")
        self.root.config(cursor="wait")

        # Récupérer le PUUID
        puuid = get_puuid_by_name(summoner_name, summoner_tag)
        if not puuid:
            # Essayer avec l'ancienne méthode (nom d'invocateur)
            puuid = get_puuid_by_summoner_name(summoner_name)
            if not puuid:
                self.root.config(cursor="")
                self.details_label.config(text="Joueur non trouvé. Vérifiez le pseudo et le tag.")
                return

        self.current_puuid = puuid

        # Récupérer l'historique des matchs
        match_ids = get_match_history(puuid, count=20)
        if not match_ids:
            self.root.config(cursor="")
            self.details_label.config(text="Aucun match trouvé pour ce joueur.")
            return

        self.match_history = match_ids

        # Récupérer les infos de chaque match pour afficher l'historique
        for match_id in match_ids:
            match_data = get_match_info(match_id)
            if match_data:
                match_info = match_data.get("info", {})
                participants = match_info.get("participants", [])
                
                # Trouver les infos du joueur dans ce match
                player_data = None
                for participant in participants:
                    if participant.get("puuid") == puuid:
                        player_data = participant
                        break
                
                if player_data:
                    champion_name = player_data.get("championName", "Inconnu")
                    win = "✅ Victoire" if player_data.get("win") else "❌ Défaite"
                    kills = player_data.get("kills", 0)
                    deaths = player_data.get("deaths", 0)
                    assists = player_data.get("assists", 0)
                    kda = round((kills + assists) / max(1, deaths), 2)
                    
                    game_duration = match_info.get("gameDuration", 0)
                    minutes = game_duration // 60
                    seconds = game_duration % 60
                    duration = f"{minutes}m {seconds}s"
                    
                    game_start_timestamp = match_info.get("gameStartTimestamp", 0)
                    date = format_timestamp(game_start_timestamp)
                    
                    self.history_tree.insert("", tk.END, values=(
                        match_id,
                        date,
                        champion_name,
                        win,
                        kda,
                        duration
                    ), iid=match_id)

        self.root.config(cursor="")
        self.details_label.config(text=f"Historique de {summoner_name}#{summoner_tag} (20 derniers matchs)")

    def load_match_from_history(self, event):
        selected_item = self.history_tree.selection()
        if not selected_item:
            return
        
        match_id = selected_item[0]
        self.match_id.set(match_id)
        self.fetch_match_by_id()

    def display_stats(self, stats, match_data):
        if not stats:
            self.details_label.config(text="Aucune donnée trouvée pour ce match.")
            return

        for player in stats:
            self.tree.insert("", tk.END, values=(
                player["summonerName"],
                player["championName"],
                player["summonerLevel"],
                player["kills"],
                player["deaths"],
                player["assists"],
                player["kda"],
                player["goldEarned"],
                player["creepScore"],
                player["visionScore"],
                "✅ Oui" if player["win"] else "❌ Non"
            ))

        # Afficher les détails du match
        match_info = match_data.get("info", {})
        game_duration = match_info.get("gameDuration", 0)
        minutes = game_duration // 60
        seconds = game_duration % 60
        
        teams = {}
        for player in stats:
            team_id = player["teamId"]
            if team_id not in teams:
                teams[team_id] = {"win": player["win"], "players": []}
            teams[team_id]["players"].append(player["summonerName"])

        team1 = teams.get(100, {"win": False, "players": []})
        team2 = teams.get(200, {"win": False, "players": []})
        
        details_text = (
            f"Durée : {minutes}m {seconds}s | "
            f"Équipe Bleue (Victoire: {'✅' if team1['win'] else '❌'}): {', '.join(team1['players'])} | "
            f"Équipe Rouge (Victoire: {'✅' if team2['win'] else '❌'}): {', '.join(team2['players'])}"
        )
        self.details_label.config(text=details_text)

    def show_details(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item = self.tree.item(selected_item)
        values = item["values"]
        if not values:
            return
        
        # Afficher les détails du joueur sélectionné
        player_name = values[0]
        champion = values[1]
        kills, deaths, assists = values[3], values[4], values[5]
        gold = values[7]
        cs = values[8]
        vision = values[9]
        
        details_text = (
            f"Détails de {player_name} ({champion}) | "
            f"KDA: {kills}/{deaths}/{assists} | "
            f"Gold: {gold} | CS: {cs} | Vision: {vision}"
        )
        self.details_label.config(text=details_text)

# --- Lancer l'application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TeamAnalyserApp(root)
    root.mainloop()
