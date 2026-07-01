import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser

# --- Configuration ---
# ⚠️ CLÉ API RIOT POUR USAGE PERSONNEL UNIQUEMENT
# ⚠️ RÉGION FIXÉE SUR EUW1 (Europe de l'Ouest)
# NE PAS PARTAGER CE FICHIER OU LE .EXE GÉNÉRÉ !
RIOT_API_KEY = "RGAPI-cc19da24-8034-4cc4-b3fb-d3c215d905e6"
RIOT_REGION = "euw1"  # Région fixée sur EUW1
RIOT_API_BASE = f"https://{RIOT_REGION}.api.riotgames.com"

# Cache pour éviter de refaire des requêtes pour les mêmes PUUIDs
summoner_name_cache = {}

# --- Récupérer les infos d'un match ---
def get_match_info(match_id):
    url = f"{RIOT_API_BASE}/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
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

# --- Interface Graphique ---
class TeamAnalyserApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🎮 Team Analyser v2 - League of Legends (EUW1)")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)

        # Variables
        self.match_id = tk.StringVar()
        self.stats = []

        # --- UI ---
        self.create_widgets()

    def create_widgets(self):
        # Frame pour la recherche
        search_frame = ttk.LabelFrame(self.root, text="🔍 Rechercher un match (Région: EUW1)", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="ID du match :").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(search_frame, textvariable=self.match_id, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Analyser", command=self.fetch_match).grid(row=0, column=2, padx=5)

        # Avertissement
        warning_frame = ttk.Frame(self.root)
        warning_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(
            warning_frame,
            text="⚠️ Ce logiciel utilise une clé API personnelle (Région: EUW1). NE PAS PARTAGER le .exe ou le code !",
            foreground="red",
            font=("Arial", 9, "bold")
        ).pack()

        # Frame pour les résultats
        self.results_frame = ttk.LabelFrame(self.root, text="📊 Résultats", padding=10)
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

    def fetch_match(self):
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
