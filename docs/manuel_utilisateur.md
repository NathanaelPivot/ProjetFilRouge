# Manuel d'installation et d'utilisation

## 1. Installation

### Prérequis
- Python 3.10 ou plus récent
- Un compte Kaggle gratuit (pour télécharger le dataset)

### Étapes

```bash
# 1. Cloner le repo
git clone <url-de-ton-repo>
cd steam-game-success

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate        # sous Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Récupérer les données

1. Télécharger `games.csv` depuis
   https://www.kaggle.com/datasets/fronkongames/steam-games-dataset
   (ou son miroir Hugging Face : https://huggingface.co/datasets/FronkonGames/steam-games-dataset)
2. Placer le fichier dans `data/raw/games.csv`

### Générer les données nettoyées et le modèle

L'application a besoin de deux fichiers qui ne sont pas inclus dans le repo
(trop volumineux et propres à chaque exécution) : le dataset nettoyé et le
modèle entraîné. Pour les générer, exécuter les notebooks dans l'ordre,
cellule par cellule :

```bash
jupyter notebook notebooks/01_exploration.ipynb
```

Au minimum, il faut exécuter entièrement :
- `02_cleaning.ipynb` → génère `data/processed/games_clean.csv`
- `06_evaluation.ipynb` → génère `models/modele_bien_note.joblib`

(Les notebooks 03, 04 et 05 ne sont pas strictement nécessaires pour faire
fonctionner l'application, mais font partie de la démarche d'analyse complète
et sont nécessaires pour comprendre les choix faits dans `06_evaluation.ipynb`.)

⚠️ La cellule de recherche d'hyperparamètres dans `06_evaluation.ipynb` prend
environ 2 minutes à s'exécuter.

## 2. Lancer l'application

```bash
streamlit run app/Accueil.py
```

Cela ouvre normalement l'application automatiquement dans le navigateur à
l'adresse `http://localhost:8501`. Si ce n'est pas le cas, ouvrir cette adresse
manuellement.

## 3. Utilisation de l'application

L'application a trois pages, accessibles depuis le menu dans la barre latérale
gauche.

### Accueil

Présente le projet, trois indicateurs globaux sur le catalogue (nombre de
jeux, période couverte, part d'indé), et une synthèse des principaux
constats de l'analyse avec un graphique d'évolution des sorties par année.
C'est le point de départ pour comprendre le contexte avant d'explorer le
détail dans les autres pages.

### Exploration

Permet de filtrer le catalogue de jeux et d'en explorer les caractéristiques :

| Filtre (barre latérale) | Effet |
|---|---|
| Genre principal | Limite l'affichage à un ou plusieurs genres |
| Année de sortie | Curseur à deux poignées pour choisir une plage d'années |
| Prix (USD) | Curseur à deux poignées pour choisir une plage de prix |
| Jeux indé uniquement | Ne garde que les jeux tagués "Indie" |

Les graphiques et indicateurs (nombre de jeux sélectionnés, prix moyen, ratio
d'avis positifs moyen) se mettent à jour automatiquement selon les filtres
choisis. Une légende 💡 sous certains graphiques résume ce qu'il faut en
retenir. Un tableau en bas de page liste le détail des 50 jeux les plus
populaires de la sélection.

### Prédiction

Permet de renseigner les caractéristiques d'un jeu (réel ou imaginaire) et
d'obtenir l'estimation du modèle sur ses chances d'être "bien noté" (au moins
80% d'avis positifs).

1. Déplier l'encart "💡 Ce que dit l'analyse sur le statut indé" pour un rappel
   de contexte (optionnel)
2. Renseigner les champs du formulaire : prix, âge requis, nombre de DLC,
   année de sortie, nombre de genres/catégories/tags, genre principal, statut
   indé
3. Cliquer sur "Prédire"

Le résultat affiche une estimation ("Plutôt bien noté" / "Plutôt pas bien
noté") avec la probabilité associée, et un rappel que le modèle se base
uniquement sur des métadonnées et atteint environ 66% d'accuracy : à prendre
comme une tendance, pas une certitude.

## 4. En cas de problème

- **`FileNotFoundError` au lancement de l'application** : le fichier
  `games_clean.csv` ou `modele_bien_note.joblib` n'existe pas encore — voir
  la section "Générer les données nettoyées et le modèle" ci-dessus.
- **Erreur de date / colonnes qui ne correspondent pas en chargeant
  `games.csv`** : voir la section 2 de `documentation_technique.md` sur le
  bug d'en-tête connu du fichier source.
- **L'application met du temps à charger** : normal au premier chargement
  (lecture du CSV et du modèle) ; les chargements suivants sont mis en cache
  par Streamlit et sont quasi instantanés.
