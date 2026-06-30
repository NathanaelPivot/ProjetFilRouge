import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score, roc_curve,
)

from utils import get_train_test_split, load_model

st.set_page_config(page_title="Modèle et évaluation", page_icon="🤖", layout="wide")
st.title("🤖 Modèle et évaluation")

st.markdown(
    "Cible choisie : prédire si un jeu sera **\"bien noté\"** (au moins 80% "
    "d'avis positifs), sur les jeux ayant au moins 10 avis. Pourquoi cette "
    "cible plutôt que la popularité : voir la page précédente (fuite de "
    "données sur `estimated_owners_avg`)."
)

X_train, X_test, y_train, y_test = get_train_test_split()
modele_final = load_model()

st.subheader("Préparation")
col1, col2, col3 = st.columns(3)
col1.metric("Jeux utilisés", f"{len(X_train) + len(X_test):,}".replace(",", " "))
col2.metric("Entraînement / test", f"{len(X_train):,} / {len(X_test):,}".replace(",", " "))
col3.metric("Classe \"bien noté\"", f"{y_train.mean() * 100:.1f}%")
st.caption(
    "Features : Price, Required age, DLC count, nb_genres, nb_categories, "
    "nb_tags, release_year, is_indie (numériques) + main_genre_group "
    "(catégorielle, top 10 genres + Other). Prétraitement : StandardScaler + "
    "OneHotEncoder dans un ColumnTransformer scikit-learn."
)

st.divider()
st.subheader("Du premier essai au modèle final")

# Résultats obtenus dans 05_modeling.ipynb / 06_evaluation.ipynb. Non
# recalculés ici : la recherche d'hyperparamètres prend ~2 minutes, ce qui
# casserait la fluidité d'une démonstration en direct. Le modèle final, lui,
# est rechargé tel quel et réévalué en direct ci-dessous.
historique = pd.DataFrame(
    {
        "Étape": [
            "Régression logistique (baseline)",
            "Random Forest (par défaut)",
            "Random Forest (ajusté)",
        ],
        "Accuracy train": [None, 0.968, 0.711],
        "Accuracy test": [0.627, 0.633, 0.660],
        "ROC-AUC test": [None, 0.676, 0.715],
    }
)
st.dataframe(historique, width="stretch", hide_index=True)

col_gauche, col_droite = st.columns(2)
with col_gauche:
    st.warning(
        "**Random Forest par défaut : 96,8% en train, 63,3% en test.** "
        "Le modèle a quasiment mémorisé les données d'entraînement "
        "(overfitting), parce que la profondeur des arbres n'était pas "
        "limitée."
    )
with col_droite:
    st.success(
        "**Après ajustement** (RandomizedSearchCV : profondeur max 20, "
        "min_samples_leaf 10, 300 arbres, class_weight='balanced') : l'écart "
        "train/test se réduit fortement et la performance réelle progresse "
        "(66,0% d'accuracy, ROC-AUC 0,72)."
    )

st.divider()
st.subheader("Évaluation du modèle final (calculée en direct)")

predictions = modele_final.predict(X_test)
probabilites = modele_final.predict_proba(X_test)[:, 1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Accuracy", f"{accuracy_score(y_test, predictions) * 100:.1f}%")
col2.metric("Precision", f"{precision_score(y_test, predictions) * 100:.1f}%")
col3.metric("Recall", f"{recall_score(y_test, predictions) * 100:.1f}%")
col4.metric("ROC-AUC", f"{roc_auc_score(y_test, probabilites):.3f}")

col_cm, col_roc = st.columns(2)

with col_cm:
    st.markdown("**Matrice de confusion**")
    cm = confusion_matrix(y_test, predictions)
    fig_cm = px.imshow(
        cm, text_auto=True, color_continuous_scale="Blues",
        labels={"x": "Prédit", "y": "Réel"},
        x=["Pas bien noté", "Bien noté"], y=["Pas bien noté", "Bien noté"],
    )
    fig_cm.update_layout(height=400)
    st.plotly_chart(fig_cm, width="stretch")

with col_roc:
    st.markdown("**Courbe ROC**")
    fpr, tpr, _ = roc_curve(y_test, probabilites)
    fig_roc = go.Figure()
    fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, name=f"Modèle (AUC = {roc_auc_score(y_test, probabilites):.3f})"))
    fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="Hasard", line=dict(dash="dash", color="gray")))
    fig_roc.update_layout(
        xaxis_title="Taux de faux positifs", yaxis_title="Taux de vrais positifs",
        height=400,
    )
    st.plotly_chart(fig_roc, width="stretch")

st.subheader("Quelles variables pèsent le plus ?")
noms_features = modele_final.named_steps["prep"].get_feature_names_out()
importances = pd.Series(
    modele_final.named_steps["model"].feature_importances_, index=noms_features
).sort_values(ascending=False).head(10)

fig_importance = px.bar(
    x=importances.values, y=importances.index, orientation="h",
    labels={"x": "Importance", "y": ""},
)
fig_importance.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_importance, width="stretch")
st.caption(
    "💡 release_year, Price, nb_tags et nb_categories dominent : l'année de "
    "sortie et le prix pèsent plus que le genre pris isolément. Cohérent "
    "avec la matrice de corrélation de la page précédente."
)

st.info(
    "**À retenir :** ~66% d'accuracy, c'est mieux que le hasard (53,5%) mais "
    "loin d'être un modèle parfait. C'est cohérent avec l'absence de "
    "corrélation forte trouvée en amont : la qualité perçue d'un jeu dépend "
    "surtout de facteurs que ces métadonnées ne capturent pas."
)

st.divider()
nav_gauche, nav_droite = st.columns(2)
with nav_gauche:
    st.page_link("pages/3_Correlations_et_segments.py", label="⬅️ Page précédente : Corrélations")
with nav_droite:
    st.page_link("pages/5_Prediction.py", label="Page suivante : Prédiction ➡️")
