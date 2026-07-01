# 🎮 Team Analyser v2 - League of Legends

Un logiciel pour analyser les matchs de League of Legends en entrant un ID de match.

## 📥 Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/Epimurdor/team-analyser-v2.git
   cd team-analyser-v2
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Obtenir une clé API Riot** :
   - Allez sur [https://developer.riotgames.com/](https://developer.riotgames.com/)
   - Créez un compte et générez une clé API.
   - Copiez-la dans le champ "Clé API Riot" dans l'application.

4. **Lancer l'application** :
   ```bash
   python main.py
   ```

## 🚀 Générer le .exe

1. **Exécuter le script** :
   - Double-cliquez sur `build_exe.bat` (Windows).
   - Ou exécutez manuellement :
     ```bash
     pyinstaller --onefile --windowed --name "TeamAnalyser_v2" main.py
     ```

2. **Récupérer le .exe** :
   - Le fichier `TeamAnalyser_v2.exe` sera généré dans le dossier `dist/`.

## 🎯 Utilisation

1. **Entrer votre clé API Riot** (une seule fois, elle est sauvegardée).
2. **Sélectionner la région** (ex: `euw1` pour l'Europe de l'Ouest).
3. **Entrer l'ID du match** (ex: `EUW1_1234567890_1234567890`).
4. **Cliquer sur "Analyser"** pour afficher les stats.

## 📊 Fonctionnalités

- ✅ Affichage des joueurs et de leurs champions.
- ✅ Stats complètes (K/D/A, KDA, Gold, CS, Vision).
- ✅ Indication de la victoire/défaite.
- ✅ Sauvegarde de la clé API.

## 🔧 Technologies

- **Langage** : Python 3.10+
- **Interface** : Tkinter
- **API** : [Riot Games API](https://developer.riotgames.com/)
- **Compilation** : PyInstaller

## ⚠️ Notes

- La clé API Riot est **gratuite** mais limitée en requêtes (100 requêtes/2 minutes en développement).
- Pour les matchs récents, utilisez l'ID complet (ex: `EUW1_1234567890_1234567890`).
- Les IDs de match peuvent être trouvés dans l'historique des matchs sur [op.gg](https://op.gg/) ou [u.gg](https://u.gg/).

## 📌 Où trouver l'ID d'un match ?

1. Allez sur [op.gg](https://op.gg/) ou [u.gg](https://u.gg/).
2. Cherchez un joueur (ex: `Faker`).
3. Allez dans l'onglet **"Match History"**.
4. Cliquez sur un match.
5. L'URL contiendra l'ID du match, par exemple :
   - `https://www.op.gg/summoner/matches/EUW1_1234567890_1234567890`
   - **ID du match** = `EUW1_1234567890_1234567890`

## 🐛 Problèmes courants

| Problème | Solution |
|----------|----------|
| **Erreur "Invalid API Key"** | Vérifiez que votre clé API est correcte et active. |
| **Erreur "Match not found"** | L'ID du match est incorrect ou trop ancien (les matchs sont disponibles **1 semaine** après leur fin). |
| **L'application plante au lancement** | Installez les dépendances : `pip install -r requirements.txt`. |
| **Le .exe ne s'ouvre pas** | Assurez-vous que Python est installé sur la machine cible ou utilisez `--onefile` avec PyInstaller. |
| **Limite de requêtes dépassée** | Attendez 2 minutes (limite : 100 requêtes/2 min en développement). |

## 🎁 Fonctionnalités supplémentaires (à venir)

- Export des stats en CSV/Excel.
- Graphiques (KDA, Gold/Minute, etc.).
- Comparaison entre 2 matchs.
- Recherche par nom de joueur.
- Thème sombre pour l'interface.

## 📜 Licence

Ce projet est sous licence **MIT**. Vous êtes libre de l'utiliser, le modifier et le distribuer.
