# Steam Game Success — Data Storytelling

Projet réalisé dans le cadre de l'UF "Spécialité IA & Data" (Ynov, Bachelor 3).

## Contexte

Analyse du marché des jeux vidéo sur Steam : qu'est-ce qui caractérise un jeu qui rencontre
son public (genre, prix, modèle économique, langues supportées, etc.) ? Le projet va de
l'acquisition des données jusqu'à une application interactive de data storytelling permettant
d'explorer le marché et de simuler les chances de succès d'un jeu selon ses caractéristiques.

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
automatiquement au chargement.

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
│   └── processed/      # données nettoyées générées par le notebook
├── notebooks/
│   ├── 01_exploration.ipynb   # acquisition et premier tour d'horizon
│   └── 02_cleaning.ipynb      # nettoyage, typage, création de features
├── app/                # application Streamlit (à venir)
├── docs/                # documentation technique
├── requirements.txt
└── README.md
```

## Utilisation

```bash
jupyter notebook notebooks/01_exploration.ipynb
```

## Statut

- [x] Acquisition et premier tour d'horizon des données
- [x] Nettoyage et préparation
- [ ] Analyse exploratoire
- [ ] Modélisation
- [ ] Application interactive
- [ ] Documentation finale
