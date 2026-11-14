import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parents[2] / "data" / "rd_database.db"
con = sqlite3.connect(BASE)

st.title("Base des essais R&D")

page = st.sidebar.radio("Menu", ["Recherche", "Fiche essai", "Qualité des données"])

if page == "Recherche":
    st.header("Recherche")

    composants = pd.read_sql(
        "SELECT DISTINCT composant_norm FROM formulation WHERE composant_norm IS NOT NULL", con)
    choix = st.selectbox("Composant", composants["composant_norm"].sort_values())
    visco_max = st.slider("Viscosité 1h maximale (mPa.s)", 0, 20000, 20000)

    requete = """
        SELECT e.code_essai, et.titre, f.quantite_phr, m.valeur_norm AS viscosite_1h
        FROM essai e
        JOIN etude et      ON et.code_etude = e.code_etude
        JOIN formulation f ON f.code_essai  = e.code_essai
        JOIN mesure m      ON m.code_essai  = e.code_essai AND m.propriete_norm = 'viscosite_1h'
        WHERE f.composant_norm = ? AND m.valeur_norm <= ?
        ORDER BY m.valeur_norm
    """
    resultats = pd.read_sql(requete, con, params=(choix, visco_max))

    st.write(len(resultats), "essai(s) trouvé(s)")
    st.dataframe(resultats)
    if not resultats.empty:
        st.scatter_chart(resultats, x="quantite_phr", y="viscosite_1h")

elif page == "Fiche essai":
    st.header("Fiche essai")

    essais = pd.read_sql("SELECT code_essai FROM essai ORDER BY code_essai", con)
    code = st.selectbox("Essai", essais["code_essai"])

    st.subheader("Formulation")
    formulation = pd.read_sql("""
        SELECT composant_norm, quantite_phr, composant AS nom_origine, source
        FROM formulation
        WHERE code_essai = ?
    """, con, params=(code,))
    st.dataframe(formulation)

    st.subheader("Mesures")
    mesures = pd.read_sql("""
        SELECT propriete_norm, valeur_norm, unite_norm,
               valeur_origine, unite_origine, source
        FROM mesure
        WHERE code_essai = ?
    """, con, params=(code,))
    st.dataframe(mesures)

else:
    st.header("Qualité des données")
    anomalies = pd.read_sql("SELECT * FROM anomalie", con)
    st.write(len(anomalies), "anomalie(s) à vérifier")
    st.dataframe(anomalies)