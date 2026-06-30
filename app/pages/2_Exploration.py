import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import ast

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import load_data

st.set_page_config(page_title="Exploration", page_icon="🔎", layout="wide")
st.title("🔎 Exploration du catalogue et histoire de la plateforme")

df = load_data()

# =====================================================================
# Histoire de la plateforme (vue d'ensemble, pas affectée par les filtres)
# =====================================================================
st.subheader("Croissance du catalogue Steam")
st.markdown(
    "Steam n'a pas toujours été ouvert à tous les développeurs. Le graphique "
    "ci-dessous montre la taille cumulée du catalogue, avec les moments où "
    "Valve a changé les règles de publication."
)

sorties_par_an = df[df["release_year"] >= 2003]["release_year"].value_counts().sort_index()
cumul = sorties_par_an.cumsum()

fig_cumul = px.area(
    x=cumul.index, y=cumul.values,
    labels={"x": "Année", "y": "Jeux cumulés sur Steam"},
)
jalons = [
    (2003, "Lancement de Steam"),
    (2012, "Steam Greenlight\n(la communauté vote)"),
    (2017, "Steam Direct\n(publication ouverte, $100)"),
]
for annee, texte in jalons:
    fig_cumul.add_vline(x=annee, line_dash="dash", line_color="gray")
    fig_cumul.add_annotation(
        x=annee, y=cumul.max(), text=texte, showarrow=False,
        yshift=10, textangle=0, font=dict(size=11),
    )
st.plotly_chart(fig_cumul, width="stretch")
st.caption(
    "💡 Chaque ouverture de la plateforme (Greenlight en 2012, puis Direct en "
    "2017, qui remplace Greenlight et ne demande plus qu'un forfait de 100$) "
    "précède une accélération nette de la croissance du catalogue."
)

st.divider()

# =====================================================================
# Filtres (le reste de la page répond à ces filtres)
# =====================================================================
st.sidebar.header("Filtres")

genres_disponibles = sorted(df["main_genre"].dropna().unique())
genres_choisis = st.sidebar.multiselect("Genre principal", genres_disponibles, default=[])

annee_min, annee_max = int(df["release_year"].min()), int(df["release_year"].max())
plage_annees = st.sidebar.slider("Année de sortie", annee_min, annee_max, (annee_min, annee_max))

prix_max_dispo = float(df["Price"].max())
plage_prix = st.sidebar.slider("Prix (USD)", 0.0, prix_max_dispo, (0.0, prix_max_dispo))

uniquement_indie = st.sidebar.checkbox("Jeux indé uniquement", value=False)

filtre = df["release_year"].between(*plage_annees) & df["Price"].between(*plage_prix)
if genres_choisis:
    filtre &= df["main_genre"].isin(genres_choisis)
if uniquement_indie:
    filtre &= df["is_indie"] == 1

df_filtre = df[filtre]

if df_filtre.empty:
    st.warning("Aucun jeu ne correspond à ces filtres, essaie de les élargir.")
    st.stop()

st.subheader("Profil du catalogue sélectionné")
col1, col2, col3 = st.columns(3)
col1.metric("Jeux sélectionnés", f"{len(df_filtre):,}".replace(",", " "))
col2.metric("Prix moyen", f"{df_filtre['Price'].mean():.2f} $")
ratio_moyen = df_filtre["positive_ratio"].mean()
col3.metric(
    "Ratio d'avis positifs moyen",
    f"{ratio_moyen * 100:.0f}%" if pd.notna(ratio_moyen) else "n/a",
)

st.subheader("Évolution du nombre de sorties (sélection filtrée)")
evolution = df_filtre["release_year"].value_counts().sort_index()
fig_evolution = px.bar(
    x=evolution.index, y=evolution.values,
    labels={"x": "Année", "y": "Nombre de jeux"},
)
st.plotly_chart(fig_evolution, width="stretch")

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.subheader("Genres les plus représentés")
    top_genres = df_filtre["main_genre"].value_counts().head(10)
    fig_genres = px.bar(
        x=top_genres.values, y=top_genres.index, orientation="h",
        labels={"x": "Nombre de jeux", "y": ""},
    )
    st.plotly_chart(fig_genres, width="stretch")

with col_droite:
    st.subheader("Langues les plus supportées")

    def parser_langues(valeur):
        if pd.isna(valeur):
            return []
        try:
            parsed = ast.literal_eval(str(valeur))
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass
        return []

    toutes_langues = df_filtre["Supported languages"].apply(parser_langues).explode().dropna()
    if toutes_langues.empty:
        st.info("Aucune langue renseignée dans cette sélection.")
    else:
        top_langues = toutes_langues.value_counts().head(10)
        fig_langues = px.bar(
            x=top_langues.values, y=top_langues.index, orientation="h",
            labels={"x": "Nombre de jeux", "y": ""},
        )
        st.plotly_chart(fig_langues, width="stretch")
        st.caption("💡 L'anglais est quasi systématique ; le reste varie beaucoup selon le genre/budget du jeu.")

col_gauche2, col_droite2 = st.columns(2)

with col_gauche2:
    st.subheader("Distribution du prix")
    jeux_payants = df_filtre[df_filtre["Price"] > 0]
    if jeux_payants.empty:
        st.info("Aucun jeu payant dans cette sélection.")
    else:
        fig_prix = px.histogram(
            jeux_payants, x="Price", nbins=50, log_x=True,
            labels={"Price": "Prix (USD)"},
        )
        st.plotly_chart(fig_prix, width="stretch")

with col_droite2:
    st.subheader("Gratuit vs payant")
    repartition = df_filtre["Price"].apply(lambda p: "Gratuit" if p == 0 else "Payant").value_counts()
    fig_f2p = px.pie(values=repartition.values, names=repartition.index, hole=0.4)
    st.plotly_chart(fig_f2p, width="stretch")

st.subheader("Prix vs ratio d'avis positifs")
avec_avis = df_filtre.dropna(subset=["positive_ratio"])
if avec_avis.empty:
    st.info("Aucun jeu avec des avis dans cette sélection.")
else:
    echantillon = avec_avis.sample(min(3000, len(avec_avis)), random_state=42)
    fig_scatter = px.scatter(
        echantillon, x="Price", y="positive_ratio",
        color=echantillon["is_indie"].map({1: "Indé", 0: "Non-indé"}),
        opacity=0.4,
        labels={"Price": "Prix (USD)", "positive_ratio": "Ratio d'avis positifs", "color": "Statut"},
    )
    st.plotly_chart(fig_scatter, width="stretch")
    st.caption(
        "💡 Pas de lien net entre prix et qualité perçue — confirmé plus "
        "précisément page suivante avec la matrice de corrélation."
    )

st.subheader("Détail des jeux sélectionnés")
st.dataframe(
    df_filtre[["Name", "main_genre", "Price", "release_year", "positive_ratio", "estimated_owners_avg"]]
    .sort_values("estimated_owners_avg", ascending=False)
    .head(50),
    width="stretch",
)

st.divider()
nav_gauche, nav_droite = st.columns(2)
with nav_gauche:
    st.page_link("pages/1_Acquisition_et_nettoyage.py", label="⬅️ Page précédente : Acquisition")
with nav_droite:
    st.page_link("pages/3_Correlations_et_segments.py", label="Page suivante : Corrélations ➡️")
