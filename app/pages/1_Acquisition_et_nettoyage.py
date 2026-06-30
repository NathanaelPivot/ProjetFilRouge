import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import load_data

st.set_page_config(page_title="Acquisition et nettoyage", page_icon="📥", layout="wide")
st.title("📥 Acquisition et nettoyage des données")

st.markdown(
    "Avant toute analyse, il faut des données fiables. Cette page retrace "
    "d'où viennent les données, un bug trouvé dans le fichier source, et le "
    "nettoyage appliqué avant de pouvoir les exploiter."
)

# Chiffres calculés une fois sur le fichier brut (01_exploration.ipynb et
# 02_cleaning.ipynb) : on ne relit pas le fichier brut de 383 Mo à chaque
# lancement de l'application, seulement le fichier déjà nettoyé.
LIGNES_BRUTES = 125_855
COLONNES_BRUTES = 40
DOUBLONS_SUPPRIMES = 0
LIGNES_SUPPRIMEES_NOM_DATE = 1

df = load_data()

st.subheader("Source des données")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Source", "Steam Games Dataset")
col2.metric("Lignes brutes", f"{LIGNES_BRUTES:,}".replace(",", " "))
col3.metric("Colonnes brutes", COLONNES_BRUTES)
col4.metric("Format", "CSV (383 Mo)")
st.caption(
    "Dataset FronkonGames, disponible sur Kaggle et en miroir sur Hugging Face "
    "(liens dans le README). Téléchargé manuellement, pas d'API : Kaggle "
    "demande une authentification qui ne s'automatise pas facilement pour ce "
    "genre de volume."
)

st.divider()
st.subheader("Un bug caché dans la source")

st.markdown(
    "L'en-tête du fichier contient 39 noms de colonnes pour 40 colonnes de "
    "données réelles : `Discount` et `DLC count` sont collées en un seul nom "
    "(`DiscountDLC count`). Sans correction, `pandas` traite la première "
    "colonne comme un index et décale silencieusement toutes les colonnes "
    "suivantes d'un cran à partir de `Price`."
)

col_avant, col_apres = st.columns(2)

exemple_avant = pd.DataFrame(
    {
        "AppID": [2539430, 496350, 1034400],
        "Name": ["Black Dragon Mage Playtest", "Supipara - Chapter 1...", "Mystery Solitaire..."],
        "Release date": ["0 - 0", "0 - 20000", "0 - 20000"],
        "Estimated owners": [0, 0, 0],
    }
)
exemple_apres = pd.DataFrame(
    {
        "AppID": [2539430, 496350, 1034400],
        "Name": ["Black Dragon Mage Playtest", "Supipara - Chapter 1...", "Mystery Solitaire..."],
        "Release date": ["Aug 1, 2023", "Jul 29, 2016", "May 6, 2019"],
        "Estimated owners": ["0 - 0", "0 - 20000", "0 - 20000"],
    }
)

with col_avant:
    st.markdown("**❌ Chargement par défaut**")
    st.dataframe(exemple_avant, width="stretch", hide_index=True)
    st.caption("`Release date` contient en réalité les valeurs de `Estimated owners`.")

with col_apres:
    st.markdown("**✅ Après correction**")
    st.dataframe(exemple_apres, width="stretch", hide_index=True)
    st.caption("En-tête corrigé manuellement (`skiprows=1, names=...`) au chargement.")

st.info(
    "💡 **Comment ça a été détecté :** après le premier chargement, la "
    "conversion de `Release date` en date échouait sur 124 645 lignes sur "
    "125 855. Ce taux d'échec anormalement élevé a mis le bug en évidence."
)

st.divider()
st.subheader("Nettoyage appliqué")

col1, col2, col3 = st.columns(3)
col1.metric("Doublons supprimés", DOUBLONS_SUPPRIMES)
col2.metric("Lignes supprimées (nom/date manquant)", LIGNES_SUPPRIMEES_NOM_DATE)
col3.metric("Lignes finales", f"{len(df):,}".replace(",", " "))

st.markdown(
    """
- Colonnes inexploitables supprimées (descriptions longues, URLs d'images/site/support, notes libres)
- `Developers` et `Publishers` manquants (~7% des lignes chacun) remplacés par `"Unknown"` plutôt que de perdre la ligne
- `Release date` convertie en vraie date, `Estimated owners` (fourchette texte) convertie en valeur numérique
- Les jeux gratuits et les jeux sans aucun avis sont repérés mais conservés à ce stade : ils restent pertinents pour l'analyse exploratoire
"""
)

st.subheader("Features créées pour l'analyse")
features_creees = pd.DataFrame(
    {
        "Feature": [
            "total_reviews", "positive_ratio", "game_age_years",
            "nb_genres / nb_categories / nb_tags", "main_genre", "is_indie",
        ],
        "Calcul": [
            "Positive + Negative",
            "Positive / total_reviews",
            "Année la plus récente − année de sortie",
            "Nombre d'éléments dans Genres / Categories / Tags",
            "Premier genre listé",
            "'Indie' présent dans la liste complète des genres",
        ],
        "Utilité": [
            "Filtrer les jeux avec assez d'avis pour être fiables",
            "Mesure de la qualité perçue, future cible du modèle",
            "Étudier l'effet de l'ancienneté d'un jeu",
            "Mesurer la richesse du tagging d'une fiche de jeu",
            "Comparer les jeux par catégorie dominante",
            "Comparer indé et non-indé",
        ],
    }
)
st.dataframe(features_creees, width="stretch", hide_index=True)

st.page_link("pages/2_Exploration.py", label="Page suivante : Exploration ➡️")
