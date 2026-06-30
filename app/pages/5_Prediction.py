import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from utils import load_data, load_model

st.set_page_config(page_title="Prédiction", page_icon="🎯", layout="centered")
st.title("🎯 Le jeu sera-t-il bien noté ?")

st.markdown(
    """
Renseigne les caractéristiques d'un jeu (réel ou imaginaire) et le modèle
estime s'il a des chances d'être "bien noté" sur Steam, c'est-à-dire d'avoir
au moins 80% d'avis positifs (parmi les jeux ayant au moins 10 avis).

Pour rappel (page précédente), le modèle atteint environ 66% d'accuracy sur
les données de test : c'est mieux que le hasard mais loin d'être parfait, à
prendre comme une tendance plutôt qu'une certitude.
"""
)

modele = load_model()
df = load_data()

with st.expander("💡 Ce que dit l'analyse sur le statut indé"):
    st.markdown(
        "Dans les données, les jeux indés ont en moyenne un meilleur ratio "
        "d'avis positifs (76,5%) que les non-indés (74,1%), mais touchent "
        "beaucoup moins de joueurs (≈56 500 propriétaires estimés en moyenne "
        "contre ≈135 700). Coche ou décoche la case ci-dessous pour voir "
        "comment ça influence la prédiction."
    )

# Les catégories de genre sont récupérées directement depuis l'encodeur du
# modèle, pour rester toujours cohérent avec ce qui a été utilisé à l'entraînement.
encodeur_genre = modele.named_steps["prep"].named_transformers_["cat"]
genres_disponibles = list(encodeur_genre.categories_[0])

with st.form("formulaire_prediction"):
    col1, col2 = st.columns(2)

    with col1:
        prix = st.number_input("Prix (USD)", min_value=0.0, max_value=200.0, value=9.99, step=1.0)
        age_requis = st.number_input("Âge requis", min_value=0, max_value=21, value=0, step=1)
        nb_dlc = st.number_input("Nombre de DLC", min_value=0, max_value=50, value=0, step=1)
        annee_sortie = st.number_input(
            "Année de sortie",
            min_value=int(df["release_year"].min()),
            max_value=int(df["release_year"].max()) + 1,
            value=int(df["release_year"].max()),
            step=1,
        )

    with col2:
        nb_genres = st.slider("Nombre de genres", 1, 8, 2)
        nb_categories = st.slider("Nombre de catégories Steam", 1, 15, 4)
        nb_tags = st.slider("Nombre de tags", 0, 30, 8)
        genre_principal = st.selectbox("Genre principal", genres_disponibles)
        est_indie = st.checkbox("Jeu indépendant", value=True)

    valider = st.form_submit_button("Prédire")

if valider:
    nouveau_jeu = pd.DataFrame(
        [
            {
                "Price": prix,
                "Required age": age_requis,
                "DLC count": nb_dlc,
                "nb_genres": nb_genres,
                "nb_categories": nb_categories,
                "nb_tags": nb_tags,
                "release_year": annee_sortie,
                "is_indie": int(est_indie),
                "main_genre_group": genre_principal,
            }
        ]
    )

    prediction = modele.predict(nouveau_jeu)[0]
    probabilite = modele.predict_proba(nouveau_jeu)[0][1]

    st.markdown("---")
    if prediction == 1:
        st.success(f"✅ Plutôt bien noté — probabilité estimée : {probabilite * 100:.0f}%")
    else:
        st.error(f"❌ Plutôt pas bien noté — probabilité d'être bien noté : {probabilite * 100:.0f}%")

        recommandations = []
        if nb_tags < 10:
            recommandations.append("ajouter plus de tags pertinents sur la fiche Steam")
        if nb_categories < 5:
            recommandations.append("renseigner davantage de catégories Steam")
        if not est_indie:
            recommandations.append(
                "s'inspirer des pratiques indé : dans les données, les jeux indés ont un "
                "ratio d'avis positifs en moyenne supérieur"
            )
        if recommandations:
            st.markdown(
                "**💡 Recommandation (d'après l'importance des variables du modèle) :** "
                + " ; ".join(recommandations) + "."
            )

    st.progress(min(max(probabilite, 0.0), 1.0))

    st.caption(
        "Rappel : ce modèle se base uniquement sur des métadonnées (prix, genre, "
        "tags...), pas sur la qualité réelle du gameplay. Une prédiction "
        "défavorable ne condamne pas un bon jeu, et inversement."
    )

st.divider()
st.page_link("pages/4_Modele_et_evaluation.py", label="⬅️ Page précédente : Modèle et évaluation")
