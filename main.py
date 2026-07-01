import tkinter as tk
from tkinter import ttk, messagebox
import requests
import configparser
import os
import webbrowser
from datetime import datetime

# --- Configuration ---
CONFIG_FILE = "config.ini"
RIOT_API_BASE = "https://{region}.api.riotgames.com"

# --- Charger la clé API depuis config.ini ---
def load_api_key():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config["RIOT"] = {"api_key": "TA_CLE_API_RIOT"}
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
        return None
    config.read(CONFIG_FILE)
    return config["RIOT"].get("api_key")

# --- Sauvegarder la clé API ---
def save_api_key(api_key):
    config = configparser.ConfigParser()
    config["RIOT"] = {"api_key": api_key}
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

# --- Récupérer les infos d'un match ---
def get_match_info(match_id, api_key, region="euw1"):
    url = f"{RIOT_API_BASE.format(region=region)}/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": api_key}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Impossible de récupérer le match : {e}")
        return None

# --- Récupérer le nom du joueur depuis son PUUID ---
def get_summoner_name(puuid, api_key, region="euw1"):
    url = f"{RIOT_API_BASE.format(region=region)}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": api_key}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("name", "Inconnu")
    except:
        return "Inconnu"

# --- Analyser le match et extraire les stats ---
def analyze_match(match_data, api_key, region="euw1"):
    if not match_data:
        return []

    match_info = match_data.get("info", {})
    participants = match_info.get("participants", [])

    stats = []
    for participant in participants:
        puuid = participant.get("puuid")
        summoner_name = get_summoner_name(puuid, api_key, region)

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
        })

    return stats

# --- Interface Graphique ---
class TeamAnalyserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Team Analyser v2 - League of Legends")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

        # Variables
        self.api_key = tk.StringVar()
        self.match_id = tk.StringVar()
        self.region = tk.StringVar(value="euw1")
        self.stats = []

        # Charger la clé API
        saved_key = load_api_key()
        if saved_key:
            self.api_key.set(saved_key)

        # --- UI ---
        self.create_widgets()

    def create_widgets(self):
        # Frame pour la configuration
        config_frame = ttk.LabelFrame(self.root, text="⚙️ Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # Clé API
        ttk.Label(config_frame, text="Clé API Riot :").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(config_frame, textvariable=self.api_key, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(config_frame, text="Sauvegarder", command=self.save_api_key).grid(row=0, column=2, padx=5)

        # Région
        ttk.Label(config_frame, text="Région :").grid(row=1, column=0, sticky=tk.W)
        regions = ["euw1", "eun1", "na1", "br1", "la1", "la2", "oc1", "jp1", "kr", "ru"]
        ttk.Combobox(config_frame, textvariable=self.region, values=regions, width=10).grid(row=1, column=1, padx=5, sticky=tk.W)

        # Frame pour la recherche
        search_frame = ttk.LabelFrame(self.root, text="🔍 Rechercher un match", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="ID du match :").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(search_frame, textvariable=self.match_id, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Analyser", command=self.fetch_match).grid(row=0, column=2, padx=5)

        # Frame pour les résultats
        self.results_frame = ttk.LabelFrame(self.root, text="📊 Résultats", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tableau des stats
        self.tree = ttk.Treeview(self.results_frame, columns=(
            "Joueur", "Champion", "K", "D", "A", "KDA", "Gold", "CS", "Vision", "Victoire"
        ), show="headings")

        # Configurer les colonnes
        self.tree.heading("Joueur", text="Joueur")
        self.tree.heading("Champion", text="Champion")
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

        # Lien pour obtenir une clé API
        ttk.Label(
            self.root,
            text="🔑 Pas de clé API ? Obtenez-en une ici : ",
            cursor="hand2",
            foreground="blue"
        ).pack(pady=5)
        ttk.Label(
            self.root,
            text="https://developer.riotgames.com/",
            cursor="hand2",
            foreground="blue"
        ).pack()
        ttk.Label(
            self.root,
            text="(Cliquez sur le lien pour vous inscrire)",
            font=("Arial", 8),
            foreground="gray"
        ).pack()

        # Bind le clic sur le lien
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Label) and "riotgames.com" in widget.cget("text"):
                widget.bind("<Button-1>", lambda e: webbrowser.open("https://developer.riotgames.com/"))

    def save_api_key(self):
        save_api_key(self.api_key.get())
        messagebox.showinfo("Succès", "Clé API sauvegardée !")

    def fetch_match(self):
        match_id = self.match_id.get().strip()
        api_key = self.api_key.get().strip()
        region = self.region.get().strip()

        if not match_id:
            messagebox.showerror("Erreur", "Veuillez entrer un ID de match.")
            return
        if not api_key:
            messagebox.showerror("Erreur", "Veuillez entrer une clé API Riot.")
            return

        # Effacer les anciens résultats
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Récupérer les données du match
        self.root.config(cursor="wait")
        match_data = get_match_info(match_id, api_key, region)
        if match_data:
            stats = analyze_match(match_data, api_key, region)
            self.display_stats(stats)
        self.root.config(cursor="")

    def display_stats(self, stats):
        for player in stats:
            self.tree.insert("", tk.END, values=(
                player["summonerName"],
                player["championName"],
                player["kills"],
                player["deaths"],
                player["assists"],
                player["kda"],
                player["goldEarned"],
                player["creepScore"],
                player["visionScore"],
                "✅ Oui" if player["win"] else "❌ Non"
            ))

# --- Lancer l'application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TeamAnalyserApp(root)
    root.mainloop()
