# Documentation technique

Ce document explique la démarche complète du projet, les choix techniques faits
à chaque étape et pourquoi, les résultats obtenus, et les limites à connaître.
Pour le détail du code, voir les notebooks dans `notebooks/` (un par grande
étape, dans l'ordre). Pour l'installation et l'utilisation, voir
`manuel_utilisateur.md`.

## 1. Vue d'ensemble de la démarche

| Notebook | Contenu |
|---|---|
| `01_exploration.ipynb` | Chargement du fichier brut, premier diagnostic (taille, types, valeurs manquantes, doublons) |
| `02_cleaning.ipynb` | Nettoyage, reformatage des types, création des features de base |
| `03_exploration.ipynb` | Distributions (prix, genres, langues) et évolution du marché dans le temps |
| `04_correlations.ipynb` | Corrélations entre variables, comparaison indé vs non-indé |
| `05_modeling.ipynb` | Choix de la cible, préparation des features, premiers modèles |
| `06_evaluation.ipynb` | Métriques fines, diagnostic d'overfitting, ajustement, sauvegarde du modèle |

L'application (`app/`) consomme directement les sorties de `02_cleaning.ipynb`
(`data/processed/games_clean.csv`) et de `06_evaluation.ipynb`
(`models/modele_bien_note.joblib`).

## 2. Un bug dans les données sources

Le fichier `games.csv` (Steam Games Dataset, FronkonGames) a un défaut dans son
en-tête : les colonnes `Discount` et `DLC count` sont collées en un seul nom
(`DiscountDLC count`), ce qui donne 39 noms de colonnes pour 40 colonnes de
données réelles. Sans correction, `pandas.read_csv` traite la première colonne
comme un index implicite et décale silencieusement toutes les colonnes
suivantes d'un cran à partir de `Price` — par exemple `Release date` se
retrouvait à contenir les valeurs qui devaient être dans `Estimated owners`.

**Détection :** après le premier chargement, la conversion de `Release date` en
date échouait sur la quasi-totalité des lignes (124 645 sur 125 855), ce qui a
mis en évidence le problème.

**Correction :** chargement avec une liste explicite de 40 noms de colonnes
(`skiprows=1, names=COLONNES`) plutôt que de laisser pandas déduire l'en-tête.
Cette correction est appliquée dans `01_exploration.ipynb` et reprise dans tous
les notebooks suivants qui chargent le fichier brut.

## 3. Nettoyage et features (Jour 2)

- Suppression des colonnes inexploitables pour l'analyse (descriptions
  longues, URLs d'images/site/support, notes libres)
- Suppression des doublons (lignes strictement identiques, puis doublons sur
  `AppID`)
- Suppression des lignes sans nom ou sans date de sortie ; `Developers` /
  `Publishers` manquants remplacés par `'Unknown'`
- `Release date` convertie en date, `release_year` extraite
- `Estimated owners` (fourchette texte, ex. `"0 - 20000"`) convertie en valeur
  numérique en prenant le milieu de la fourchette (`estimated_owners_avg`)
- Features créées : `total_reviews`, `positive_ratio`, `game_age_years`,
  `nb_genres`, `nb_categories`, `nb_tags`, `main_genre` (premier genre listé)
- Les valeurs limites (jeux gratuits, jeux sans aucun avis) sont repérées mais
  pas supprimées à ce stade : elles restent pertinentes pour l'analyse
  exploratoire, et sont filtrées plus tard si besoin pour la modélisation

`is_indie` (le jeu a "Indie" dans sa liste de genres) est créé plus tard, au
Jour 4, à partir de la colonne `Genres` complète (pas seulement `main_genre`,
qui ne garde que le premier genre listé).

## 4. Choix de la cible pour la modélisation

Deux candidates étaient disponibles comme indicateur de "succès" :

- **`estimated_owners_avg`** (popularité) : écartée comme cible principale.
  L'analyse de corrélation (Jour 4) montre qu'elle est fortement liée à
  `total_reviews` (r ≈ 0,76) et à `Peak CCU` (r ≈ 0,64). Or ces deux variables
  sont elles-mêmes des signaux à partir desquels ce type d'estimation est
  généralement calculé (Steam ne communique pas le nombre réel de joueurs).
  Les utiliser comme variables explicatives aurait introduit une fuite de
  données (prédire la cible à partir d'elle-même).
- **`positive_ratio`** (qualité perçue) : retenue. Elle n'a pas ce problème de
  circularité, et n'est fortement corrélée à aucune métadonnée disponible —
  ce qui en fait une cible plus intéressante à modéliser, même si les
  performances attendues sont nécessairement modestes.

**Construction de la cible :** classification binaire `bien_note` = 1 si
`positive_ratio >= 0.8`, sinon 0. Le seuil 0,8 a été choisi parce qu'il est
proche du seuil "Very Positive" utilisé par Steam lui-même, et qu'il donne des
classes à peu près équilibrées (53,5% / 46,5%) sur les données filtrées.

**Filtre appliqué :** seuls les jeux avec au moins 10 avis (`total_reviews >=
10`) sont conservés pour la modélisation, soit 56 662 jeux sur 125 854. En
dessous de ce seuil, le ratio d'avis positifs est trop instable pour être un
signal fiable (1 avis sur 1 donnerait 100%, ce qui est du bruit).

## 5. Features et encodage

Features numériques : `Price`, `Required age`, `DLC count`, `nb_genres`,
`nb_categories`, `nb_tags`, `release_year`, `is_indie`.

Feature catégorielle : `main_genre_group`, qui regroupe les 10 genres
principaux les plus fréquents et met le reste dans `"Other"` (`main_genre` a
28 valeurs très inégalement réparties, un one-hot direct aurait créé des
colonnes presque vides).

Prétraitement via un `ColumnTransformer` scikit-learn (`StandardScaler` sur le
numérique, `OneHotEncoder(handle_unknown='ignore')` sur le genre), encapsulé
dans un `Pipeline` avec le modèle. Ce choix plutôt qu'un `pd.get_dummies`
manuel évite les décalages de colonnes entre train et test, et permet de
sauvegarder le prétraitement et le modèle comme un seul objet réutilisable.

## 6. Modèles et ajustement

**Modèles testés (Jour 5) :** régression logistique (`LogisticRegression`,
baseline simple) et Random Forest (`RandomForestClassifier`, pour capter des
interactions entre variables). Résultats par défaut : ~62,7% et ~63,3%
d'accuracy respectivement.

**Diagnostic (Jour 6) :** le Random Forest par défaut overfittait fortement
(96,8% d'accuracy sur le train contre 63,3% sur le test), parce que la
profondeur des arbres n'était pas limitée.

**Ajustement :** `RandomizedSearchCV` (12 tirages, validation croisée à 3
plis, critère ROC-AUC) sur `n_estimators`, `max_depth`, `min_samples_leaf` et
`class_weight`. Meilleurs paramètres trouvés : `n_estimators=300,
max_depth=20, min_samples_leaf=10, class_weight='balanced'`. Après ajustement,
l'écart train/test se réduit fortement (71,1% / 66,0%) et la performance
réelle sur le test progresse (accuracy 63,3% → 66,0%, ROC-AUC 0,68 → 0,72).

**Variables les plus importantes** (feature importance du modèle final) :
`release_year`, `Price`, `nb_tags`, `nb_categories`. Le genre pris isolément
pèse relativement peu une fois ces variables prises en compte.

## 7. Résultats et limites

Le modèle final atteint ~66% d'accuracy et ~0,72 de ROC-AUC sur les jeux ayant
au moins 10 avis. C'est mieux que le hasard (53,5% en prédisant toujours la
classe majoritaire) mais loin d'être un modèle fiable à 90%+, et c'est un
résultat assumé plutôt qu'un problème à masquer : il confirme ce que l'analyse
de corrélation indiquait déjà, à savoir que la qualité perçue d'un jeu dépend
surtout de facteurs que ces métadonnées ne capturent pas (le gameplay
lui-même, le marketing, le bouche-à-oreille...).

**Limites connues :**
- Le modèle ne s'applique qu'aux jeux ayant au moins 10 avis ; il ne dit rien
  sur les jeux très récents ou très peu visibles
- `estimated_owners_avg` est une estimation fournie par le dataset source, pas
  une mesure exacte du nombre de joueurs
- Le seuil de 0,8 pour définir "bien noté" est un choix arbitraire (bien que
  motivé) ; un autre seuil donnerait une cible et des résultats différents
- L'analyse se limite aux métadonnées disponibles dans le dataset ; aucune
  donnée sur le contenu réel du jeu, son marketing ou sa réception médiatique
  n'a été utilisée

## 8. Application

Voir `manuel_utilisateur.md` pour le guide d'utilisation. Côté architecture :
l'application est une app Streamlit multipage (`app/Accueil.py` +
`app/pages/`), avec un module `app/utils.py` qui centralise le chargement
(mis en cache) des données et du modèle pour éviter de relire les fichiers à
chaque interaction. La page de prédiction récupère la liste des genres
directement depuis l'encodeur du modèle sauvegardé plutôt que de la coder en
dur, pour rester cohérente automatiquement si le modèle est réentraîné.
