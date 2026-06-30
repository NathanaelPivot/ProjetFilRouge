"""Fonctions partagées par les pages de l'application.

Centralise le chargement des données et du modèle pour que chaque page
n'ait pas à dupliquer cette logique, et pour profiter du cache de Streamlit
(les fichiers ne sont relus qu'une fois par session, pas à chaque interaction).
"""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# Racine du projet = dossier parent de app/, peu importe d'où streamlit est lancé
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "games_clean.csv"
MODEL_PATH = BASE_DIR / "models" / "modele_bien_note.joblib"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Charge le dataset nettoyé produit par 02_cleaning.ipynb."""
    df = pd.read_csv(DATA_PATH, parse_dates=["Release date"])
    df["is_indie"] = df["Genres"].fillna("").str.contains("Indie").astype(int)
    return df


@st.cache_resource
def load_model():
    """Charge le pipeline scikit-learn (prétraitement + modèle) produit par 06_evaluation.ipynb."""
    return joblib.load(MODEL_PATH)


@st.cache_data
def get_train_test_split():
    """Reconstruit exactement le même split train/test que dans
    05_modeling.ipynb / 06_evaluation.ipynb, pour pouvoir évaluer le modèle
    sauvegardé sans avoir à le réentraîner dans l'application."""
    from sklearn.model_selection import train_test_split

    df = load_data()
    sub = df[df["total_reviews"] >= 10].copy()
    sub["bien_note"] = (sub["positive_ratio"] >= 0.8).astype(int)

    top_genres = sub["main_genre"].value_counts().head(10).index
    sub["main_genre_group"] = sub["main_genre"].where(sub["main_genre"].isin(top_genres), "Other")

    features_numeriques = [
        "Price", "Required age", "DLC count", "nb_genres",
        "nb_categories", "nb_tags", "release_year", "is_indie",
    ]
    features_categorielles = ["main_genre_group"]

    X = sub[features_numeriques + features_categorielles]
    y = sub["bien_note"]

    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
