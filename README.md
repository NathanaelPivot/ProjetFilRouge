# Steam Game Success — Data Storytelling

Projet réalisé dans le cadre de l'UF "Spécialité IA & Data" (Ynov, Bachelor 3).

## Contexte

Analyse du marché des jeux vidéo sur Steam : qu'est-ce qui caractérise un jeu qui
rencontre son public (genre, prix, modèle économique, langues supportées, etc.) ?
Le projet va de l'acquisition des données jusqu'à une application interactive de
data storytelling permettant d'explorer le marché et de simuler les chances de
succès d'un jeu selon ses caractéristiques.

## Résultats clés

- Le nombre de jeux sortis sur Steam a explosé depuis le milieu des années 2010
  (quelques centaines par an avant 2014, près de 25 000 en 2025), mais la part
  des jeux indés dans ces sorties a culminé en 2018 (77%) puis s'est stabilisée
  autour de 60-65% : le marché non-indé croît encore plus vite récemment.
- La popularité d'un jeu (nombre de propriétaires estimé) s'explique en grande
  partie par sa visibilité (nombre d'avis, pic de joueurs connectés), alors que
  la qualité perçue (ratio d'avis positifs) n'est fortement corrélée à aucune
  métadonnée disponible.
- Un modèle entraîné pour prédire si un jeu sera "bien noté" plafonne autour de
  66% d'accuracy (ROC-AUC ≈ 0,72) : un signal réel mais modeste, cohérent avec
  l'absence de corrélation forte trouvée en amont.
- Les jeux indés sont en moyenne un peu mieux notés que les non-indés (76,5%
  d'avis positifs contre 74,1%), mais touchent beaucoup moins de joueurs.

Le détail de la démarche et l'interprétation de chaque résultat sont dans les
notebooks (`notebooks/`) et dans `docs/documentation_technique.md`.

## Données

Dataset : "Steam Games Dataset" (FronkonGames), +120 000 jeux avec prix, genres, tags,
avis positifs/négatifs, score Metacritic, nombre de joueurs estimé, date de sortie, etc.

- Kaggle : https://www.kaggle.com/datasets/fronkongames/steam-games-dataset
- Miroir Hugging Face : https://huggingface.co/datasets/FronkonGames/steam-games-dataset

Le fichier n'est pas inclus dans le repo (trop volumineux). À faire :
1. Télécharger `games.csv` depuis l'un des deux liens ci-dessus
2. Le placer dans `data/raw/games.csv`

**Point d'attention :** le fichier `games.csv` source contient un bug dans son
en-tête (`Discount` et `DLC count` sont collés en un seul nom de colonne), ce
qui décale toutes les colonnes suivantes si on le charge sans précaution. Les
notebooks `01_exploration.ipynb` et `02_cleaning.ipynb` corrigent ce problème
automatiquement au chargement (détail dans `docs/documentation_technique.md`).

## Installation

```bash
# Cloner le repo
git clone <url-de-ton-repo>
cd steam-game-success

# Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate   # sous Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Structure du projet

```
steam-game-success/
├── data/
│   ├── raw/            # données brutes (games.csv à déposer ici)
│   └── processed/      # données nettoyées générées par 02_cleaning.ipynb
├── notebooks/
│   ├── 01_exploration.ipynb   # acquisition et premier tour d'horizon
│   ├── 02_cleaning.ipynb      # nettoyage, typage, création de features
│   ├── 03_exploration.ipynb   # EDA : distributions, genres, langues, évolution
│   ├── 04_correlations.ipynb  # EDA : corrélations, indé vs gros studios
│   ├── 05_modeling.ipynb      # cible, features, régression logistique vs Random Forest
│   └── 06_evaluation.ipynb    # métriques fines, ajustement, sauvegarde du modèle final
├── models/
│   └── modele_bien_note.joblib   # pipeline complet (prétraitement + modèle)
├── app/
│   ├── Accueil.py                          # page d'accueil et synthèse des résultats
│   ├── utils.py                            # chargement partagé des données, du modèle et du split train/test
│   └── pages/
│       ├── 1_Acquisition_et_nettoyage.py   # source, bug du CSV, nettoyage, features créées
│       ├── 2_Exploration.py                # histoire de la plateforme + filtres genre/année/prix
│       ├── 3_Correlations_et_segments.py   # matrice de corrélation, indé vs non-indé
│       ├── 4_Modele_et_evaluation.py       # cible, comparaison de modèles, métriques, feature importance
│       └── 5_Prediction.py                 # formulaire de simulation + prédiction et recommandation
├── docs/
│   ├── documentation_technique.md   # démarche, choix techniques, résultats, limites
│   └── manuel_utilisateur.md        # guide d'installation et d'utilisation détaillé
├── requirements.txt
└── README.md
```

## Utilisation

Reproduire la démarche complète, dans l'ordre :

```bash
jupyter notebook notebooks/01_exploration.ipynb
```

Lancer l'application une fois les notebooks 01, 02 et 06 exécutés (ils
génèrent les données nettoyées et le modèle dont l'application a besoin) :

```bash
streamlit run app/Accueil.py
```

Voir `docs/manuel_utilisateur.md` pour le détail page par page de l'application.

## Documentation

- `docs/documentation_technique.md` : démarche complète, choix techniques
  (cible, features, modèles, hyperparamètres), résultats et limites
- `docs/manuel_utilisateur.md` : installation détaillée et guide d'utilisation
  de l'application

## Avancement

- [x] Acquisition et premier tour d'horizon des données
- [x] Nettoyage et préparation
- [x] Analyse exploratoire
- [x] Modélisation
- [x] Application interactive
- [x] Documentation finale
