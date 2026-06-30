import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import plotly.express as px
import streamlit as st

from utils import load_data

st.set_page_config(page_title="Corrélations", page_icon="🔗", layout="wide")
st.title("🔗 Corrélations et segments")

st.markdown(
    "Avant de construire un modèle, il faut savoir ce qui est vraiment lié à "
    "quoi. Cette page croise les variables entre elles, puis compare les "
    "jeux indés aux productions plus importantes."
)

df = load_data()

st.subheader("Matrice de corrélation")
colonnes_numeriques = [
    "Price", "Discount", "DLC count", "Required age", "nb_genres",
    "nb_categories", "nb_tags", "game_age_years", "release_year",
    "total_reviews", "positive_ratio", "estimated_owners_avg", "Peak CCU",
]
correlations = df[colonnes_numeriques].corr().round(2)

fig_corr = px.imshow(
    correlations, text_auto=True, color_continuous_scale="RdBu",
    zmin=-1, zmax=1, aspect="auto",
)
fig_corr.update_layout(height=550)
st.plotly_chart(fig_corr, width="stretch")

col_a, col_b = st.columns(2)
with col_a:
    st.warning(
        "**⚠️ estimated_owners_avg** est fortement lié à `total_reviews` "
        "(0,76) et `Peak CCU` (0,64). Logique : Steam ne donne jamais le "
        "vrai nombre de joueurs, cette estimation est elle-même calculée à "
        "partir de ces signaux. Les utiliser pour prédire cette variable "
        "reviendrait à la prédire à partir d'elle-même."
    )
with col_b:
    st.info(
        "**ℹ️ positive_ratio** (la qualité perçue) n'est fortement corrélé à "
        "rien : `nb_tags` (0,18) et `release_year` (0,15) sont les liens les "
        "plus forts, ce qui reste faible. C'est pour ça qu'on a choisi cette "
        "variable comme cible : pas de fuite de données, mais un signal à "
        "construire à partir de plusieurs variables faibles."
    )

st.divider()
st.subheader("Indé vs non-indé")

comparaison = df.groupby("is_indie").agg(
    nb_jeux=("AppID", "count"),
    prix_moyen=("Price", "mean"),
    ratio_positif_moyen=("positive_ratio", "mean"),
    owners_moyen=("estimated_owners_avg", "mean"),
)
comparaison.index = comparaison.index.map({1: "Indé", 0: "Non-indé"})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jeux indés", f"{comparaison.loc['Indé', 'nb_jeux']:,}".replace(",", " "))
col2.metric("Prix moyen (indé)", f"{comparaison.loc['Indé', 'prix_moyen']:.2f} $")
col3.metric(
    "Ratio avis positifs (indé)",
    f"{comparaison.loc['Indé', 'ratio_positif_moyen'] * 100:.1f}%",
    delta=f"{(comparaison.loc['Indé', 'ratio_positif_moyen'] - comparaison.loc['Non-indé', 'ratio_positif_moyen']) * 100:.1f} pts vs non-indé",
)
col4.metric(
    "Propriétaires estimés (indé)",
    f"{comparaison.loc['Indé', 'owners_moyen']:,.0f}".replace(",", " "),
    delta=f"{comparaison.loc['Indé', 'owners_moyen'] - comparaison.loc['Non-indé', 'owners_moyen']:,.0f}".replace(",", " "),
)

fig_comp = px.bar(
    comparaison.reset_index(),
    x="is_indie", y=["ratio_positif_moyen", "prix_moyen"],
    barmode="group",
    labels={"is_indie": "", "value": "", "variable": "Indicateur"},
)
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    fig_ratio = px.bar(
        comparaison.reset_index(), x="is_indie", y="ratio_positif_moyen",
        labels={"is_indie": "", "ratio_positif_moyen": "Ratio d'avis positifs moyen"},
        color="is_indie", color_discrete_sequence=["#DD8452", "#4C72B0"],
    )
    fig_ratio.update_layout(showlegend=False)
    st.plotly_chart(fig_ratio, width="stretch")
with col_chart2:
    fig_owners = px.bar(
        comparaison.reset_index(), x="is_indie", y="owners_moyen",
        labels={"is_indie": "", "owners_moyen": "Propriétaires estimés (moyenne)"},
        color="is_indie", color_discrete_sequence=["#DD8452", "#4C72B0"],
    )
    fig_owners.update_layout(showlegend=False)
    st.plotly_chart(fig_owners, width="stretch")

st.caption(
    "💡 Les jeux indés sont mieux notés en moyenne mais touchent beaucoup "
    "moins de joueurs : être bien noté n'implique pas d'être largement "
    "diffusé, et inversement."
)

st.subheader("Évolution de la part d'indé parmi les sorties")
part_indie = df[df["release_year"] >= 2010].groupby("release_year")["is_indie"].mean() * 100
fig_part_indie = px.line(
    x=part_indie.index, y=part_indie.values, markers=True,
    labels={"x": "Année", "y": "% de jeux indés"},
)
st.plotly_chart(fig_part_indie, width="stretch")
st.caption(
    "💡 La part d'indé a culminé à 77% en 2018 puis s'est stabilisée autour "
    "de 60-65% : le marché non-indé a augmenté encore plus vite récemment, "
    "la composition du catalogue évolue, ce n'est pas juste \"toujours plus d'indé\"."
)

st.divider()
nav_gauche, nav_droite = st.columns(2)
with nav_gauche:
    st.page_link("pages/2_Exploration.py", label="⬅️ Page précédente : Exploration")
with nav_droite:
    st.page_link("pages/4_Modele_et_evaluation.py", label="Page suivante : Modèle ➡️")
