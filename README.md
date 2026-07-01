# 🎮 Team Analyser v2 - League of Legends (Usage Personnel)

Un logiciel **pour usage personnel uniquement** pour analyser les matchs de League of Legends en entrant un ID de match.

> ⚠️ **ATTENTION** : Ce logiciel utilise une **clé API Riot personnelle**. **NE PAS PARTAGER** le code, le dépôt ou le `.exe` généré avec d'autres personnes, sous peine de voir la clé désactivée par Riot Games.

---

## 📥 Installation

1. **Cloner le dépôt** (ou télécharger les fichiers) :
   ```bash
   git clone https://github.com/Epimurdor/team-analyser-v2.git
   cd team-analyser-v2
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application** :
   ```bash
   python main.py
   ```

---

## 🚀 Générer le .exe (Windows)

1. **Exécuter le script** :
   - Double-cliquez sur `build_exe.bat`.
   - Ou exécutez manuellement :
     ```bash
     pyinstaller --onefile --windowed --name "TeamAnalyser_v2" main.py
     ```

2. **Récupérer le .exe** :
   - Le fichier `TeamAnalyser_v2.exe` sera généré dans le dossier `dist/`.
   - **⚠️ NE PAS PARTAGER CE FICHIER !** (Il contient ta clé API.)

---

## 🎯 Utilisation

1. **Entrer l'ID du match** (ex: `EUW1_1234567890_1234567890`).
2. **Sélectionner la région** (ex: `euw1` pour l'Europe de l'Ouest).
3. **Cliquer sur "Analyser"** pour afficher les stats.

### Où trouver l'ID d'un match ?
- Sur **[op.gg](https://op.gg/)** ou **[u.gg](https://u.gg/)** :
  1. Cherchez un joueur (ex: `Faker`).
  2. Allez dans l'onglet **"Match History"**. 
  3. Cliquez sur un match.
  4. L'URL contiendra l'ID du match, par exemple :
     - `https://www.op.gg/summoner/matches/EUW1_1234567890_1234567890`
     - **ID du match** = `EUW1_1234567890_1234567890`

---

## 📊 Fonctionnalités

- ✅ **Recherche par ID de match** : Entre l'ID et récupère toutes les stats.
- ✅ **Affichage des joueurs** : Noms, champions, niveau, K/D/A, KDA, Gold, CS, Vision.
- ✅ **Indication victoire/défaite** : ✅ Oui / ❌ Non.
- ✅ **Détails du match** : Durée, équipes, etc.
- ✅ **Cache des noms de joueurs** : Évite les requêtes inutiles à l'API.
- ✅ **Clé API intégrée** : Pas besoin de la saisir à chaque fois.

---

## 🔧 Technologies

- **Langage** : Python 3.10+
- **Interface** : Tkinter (intégré à Python)
- **API** : [Riot Games API](https://developer.riotgames.com/)
- **Compilation** : PyInstaller

---

## ⚠️ Avertissements Importants

1. **Ne pas partager le code ou le `.exe`** : 
   - Ta clé API est **hardcodée** dans `main.py`. Si tu partages le fichier ou le `.exe`, d'autres pourront l'utiliser, et Riot **désactivera ta clé**.

2. **Limites de l'API Riot** :
   - **100 requêtes / 2 minutes** en développement.
   - Les matchs sont disponibles **1 semaine** après leur fin.

3. **Si ta clé est désactivée** :
   - Va sur [https://developer.riotgames.com/](https://developer.riotgames.com/) pour en générer une nouvelle.
   - Remplace la valeur de `RIOT_API_KEY` dans `main.py`.

---

## 🐛 Problèmes Courants

| Problème | Solution |
|----------|----------|
| **`Invalid API Key`** | Ta clé a été désactivée (partagée ou abusée). Génère-en une nouvelle sur le site de Riot. |
| **`Match not found`** | L'ID du match est incorrect ou le match a plus de **1 semaine**. |
| **`403 Forbidden`** | Limite de requêtes dépassée (100/2 min). Attends 2 minutes. |
| **Le `.exe` ne s'ouvre pas** | Assure-toi que Python est installé sur ta machine ou utilise `--onefile` avec PyInstaller. |
| **L'application est lente** | C'est normal : l'API Riot a un délai de réponse (1-2 secondes par requête). |

---

## 📜 Licence

Ce projet est **pour usage personnel uniquement**. Tu es libre de l'utiliser et de le modifier, mais **ne le partage pas** avec ta clé API intégrée.

---

## 🔒 Comment Mettre à Jour la Clé API ?

Si ta clé est désactivée ou si tu veux en changer :

1. Va sur [https://developer.riotgames.com/](https://developer.riotgames.com/).
2. Génère une nouvelle clé API.
3. Ouvre `main.py` et remplace la ligne :
   ```python
   RIOT_API_KEY = "TA_NOUVELLE_CLE_API"
   ```
4. Sauvegarde le fichier et relance l'application.

---

## 🎁 Fonctionnalités Supplémentaires (Optionnelles)

Si tu veux que j'ajoute une de ces fonctionnalités, dis-le-moi !

- 📥 **Export en CSV/Excel** : Exporter les stats pour analyse avancée.
- 📈 **Graphiques** : Courbes de Gold/Minute, KDA, etc.
- 🔍 **Recherche par nom de joueur** : Trouver les matchs récents d'un joueur.
- 🌙 **Thème sombre** : Interface plus moderne.
- 🔄 **Comparaison de matchs** : Comparer 2 matchs côte à côte.
