import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import plotly.express as px
import streamlit as st

from utils import load_data

st.set_page_config(page_title="Steam Game Success", page_icon="🎮", layout="wide")

st.title("🎮 Steam Game Success — Data Storytelling")
st.markdown(
    "Le marché des jeux vidéo sur Steam exploré de bout en bout : son évolution, "
    "ce qui semble lié (ou pas) à la qualité perçue d'un jeu, et un simulateur "
    "pour tester tes propres hypothèses."
)

df = load_data()

col1, col2, col3 = st.columns(3)
col1.metric("Jeux dans le catalogue", f"{len(df):,}".replace(",", " "))
col2.metric(
    "Période couverte",
    f"{int(df['release_year'].min())} – {int(df['release_year'].max())}",
)
col3.metric("Part de jeux indé", f"{df['is_indie'].mean() * 100:.0f}%")

st.markdown("---")
st.subheader("Ce que les données racontent")

col_texte, col_graphique = st.columns([2, 1])

with col_texte:
    st.markdown(
        """
**Une explosion de sorties, mais pas seulement portée par l'indé.**
Le nombre de jeux sortis sur Steam est passé de quelques centaines par an
avant 2014 à près de 25 000 en 2025. La part des jeux indés dans ces sorties
a culminé à 77% en 2018, puis s'est stabilisée autour de 60-65% : le
catalogue grossit dans toutes les catégories, pas seulement côté indé.

**La popularité s'explique surtout par la visibilité, pas par la qualité.**
Le nombre de propriétaires estimé est fortement lié au nombre d'avis et au
pic de joueurs connectés, alors que le ratio d'avis positifs n'est corrélé
fortement à aucune métadonnée disponible (prix, genre, tags...). Un modèle
entraîné à prédire si un jeu sera "bien noté" plafonne autour de 66%
d'accuracy : il y a un signal, mais modeste.

**Les jeux indés sont mieux notés en moyenne, mais touchent moins de monde.**
76,5% d'avis positifs en moyenne contre 74,1% pour les non-indés, pour
environ 56 500 propriétaires estimés contre 135 700. Être bien noté
n'implique pas d'être largement diffusé, et inversement.
"""
    )

with col_graphique:
    evolution = df["release_year"].value_counts().sort_index()
    evolution = evolution[evolution.index >= 2004]
    fig = px.bar(
        x=evolution.index, y=evolution.values,
        labels={"x": "", "y": "Jeux sortis"},
    )
    fig.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width="stretch")
    st.caption("Nombre de jeux sortis sur Steam par année (2004–2026)")

st.markdown("---")
st.markdown(
    "Pour aller plus loin, utilise le menu à gauche : **Exploration** pour "
    "filtrer le catalogue par genre, année et prix, et **Prédiction** pour "
    "simuler les chances de succès d'un jeu selon ses caractéristiques."
)

st.page_link("pages/1_Acquisition_et_nettoyage.py", label="Commencer : Acquisition et nettoyage ➡️")

st.caption("Source des données : Steam Games Dataset (FronkonGames), via Kaggle.")
