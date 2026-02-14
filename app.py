import streamlit as st
import pandas as pd

st.set_page_config(page_title="Contrôle Anomalies", layout="wide")

st.title("🔍 Contrôle des anomalies fournisseurs")

uploaded_file = st.file_uploader("Export_Balance_UTF8 (CSV)", type="csv")

if uploaded_file:
    balance = pd.read_csv(uploaded_file, encoding="latin-1", sep=";")

    # Nettoyage noms de colonnes
balance.columns = [col.strip() for col in balance.columns]
balance.columns = [col.replace("\ufeff", "") for col in balance.columns]
    
    # Nettoyage
balance = balance.dropna(subset=["N° facture", "Crédit"], how="all")
balance = balance[balance["Crédit"] != 0]
balance = balance[balance["N° facture"].astype(str).str.strip() != ""]

anomalies = []

    def append_anomaly(anomaly_df, type_anomalie, commentaire):
        for _, row in anomaly_df.iterrows():
            anomalies.append({
                "Type d'anomalie": type_anomalie,
                "Compte": row["Compte"],
                "N° facture": row["N° facture"],
                "Date": row["Date"],
                "Montant": row["Crédit"],
                "Commentaire": commentaire
            })

    # Doublons facture
doublons_facture = balance[balance.duplicated(subset=["Compte", "N° facture"], keep=False)]

    if not doublons_facture.empty:
        append_anomaly(doublons_facture, "Doublon de facture", "Facture en double")

    df_anomalies = pd.DataFrame(anomalies)

    total_pieces = len(balance)
    total_anomalies = len(df_anomalies)
    taux_anomalie = round((total_anomalies / total_pieces) * 100, 2) if total_pieces > 0 else 0

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Pièces analysées", total_pieces)
    col2.metric("⚠️ Anomalies détectées", total_anomalies)
    col3.metric("📊 Taux d'anomalie", f"{taux_anomalie} %")

    st.subheader("📋 Liste des anomalies")
    st.dataframe(df_anomalies)

    st.download_button(
        "📥 Télécharger les anomalies",
        df_anomalies.to_csv(index=False).encode("utf-8"),
        "anomalies_structurées.csv",
        "text/csv"
    )
