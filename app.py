import streamlit as st
import pandas as pd
import csv
from io import TextIOWrapper

st.set_page_config(page_title="Contrôle Anomalies", layout="wide")
st.title("🔍 Contrôle des anomalies fournisseurs")

uploaded_file = st.file_uploader("Importer Export_Balance (CSV)", type="csv")

if uploaded_file:

    # ------------------ Lecture CSV avec détection automatique ------------------
    try:
        # Pour UTF-16 Excel, on utilise TextIOWrapper
        wrapper = TextIOWrapper(uploaded_file, encoding="utf-16")
        sample = wrapper.read(1024)
        wrapper.seek(0)

        # Détecter séparateur automatiquement
        dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        sep_detected = dialect.delimiter

        balance = pd.read_csv(wrapper, sep=sep_detected)
    except Exception as e:
        st.error(f"⚠️ Impossible de lire le fichier CSV : {e}")
        st.stop()

    # ------------------ Nettoyage noms de colonnes ------------------
    balance.columns = [str(col).strip().replace("\ufeff", "") for col in balance.columns]
    st.write("✅ Colonnes détectées :", balance.columns.tolist())

    # ------------------ Vérification colonnes essentielles ------------------
    if "N° facture" not in balance.columns or "Crédit" not in balance.columns:
        st.error("⚠️ Colonnes 'N° facture' ou 'Crédit' manquantes !")
        st.stop()

    # ------------------ Nettoyage et conversion des colonnes ------------------
    for col in ["Débit", "Crédit"]:
        if col in balance.columns:
            balance[col] = balance[col].fillna(0)
            balance[col] = balance[col].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)

    balance["N° facture"] = balance["N° facture"].fillna("").astype(str).str.strip()

    balance = balance.dropna(subset=["N° facture", "Crédit"], how="all")
    balance = balance[balance["Crédit"] != 0]
    balance = balance[balance["N° facture"].astype(str).str.strip() != ""]

    # ------------------ Détection anomalies ------------------
    anomalies = []

    def append_anomaly(anomaly_df, type_anomalie, commentaire):
        for _, row in anomaly_df.iterrows():
            anomalies.append({
                "Type d'anomalie": type_anomalie,
                "Compte": row.get("Compte", ""),
                "N° facture": row.get("N° facture", ""),
                "Date": row.get("Date", ""),
                "Montant": row.get("Crédit", 0),
                "Commentaire": commentaire
            })

    # Doublons facture
    doublons_facture = balance[balance.duplicated(subset=["Compte", "N° facture"], keep=False)]
    if not doublons_facture.empty:
        append_anomaly(doublons_facture, "Doublon de facture", "Facture en double")

    df_anomalies = pd_
