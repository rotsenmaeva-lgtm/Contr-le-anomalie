import streamlit as st
import pandas as pd

st.set_page_config(page_title="Contrôle Anomalies", layout="wide")
st.title("🔍 Contrôle des anomalies fournisseurs")

uploaded_file = st.file_uploader("Importer Export_Balance (CSV)", type="csv")

if uploaded_file:

    # ------------------ Lecture CSV robuste ------------------
    try:
        # Tentative UTF-8
        balance = pd.read_csv(uploaded_file, sep=";")
    except Exception as e_utf8:
        try:
            uploaded_file.seek(0)  # Revenir au début du fichier
            balance = pd.read_csv(uploaded_file, sep=";", encoding="latin-1")
        except Exception as e_latin1:
            st.error(f"⚠️ Impossible de lire le CSV :\nUTF-8 : {e_utf8}\nLatin-1 : {e_latin1}")
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

    # ------------------ Détection des anomalies ------------------
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

    # Doublons de facture
    doublons_facture = balance[balance.duplicated(subset=["Compte", "N° facture"], keep=False)]
    if not doublons_facture.empty:
        append_anomaly(doublons_facture, "Doublon de facture", "Facture en double")

    df_anomalies = pd.DataFrame(anomalies)

    # ------------------ Calcul KPI ------------------
    total_pieces = len(balance)
    total_anomalies = len(df_anomalies)
    taux_anomalie = round((total_anomalies / total_pieces) * 100, 2) if total_pieces > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Pièces analysées", total_pieces)
    col2.metric("⚠️ Anomalies détectées", total_anomalies)
    col3.metric("📊 Taux d'anomalie", f"{taux_anomalie} %")

    # ------------------ Affichage anomalies ------------------
    st.subheader("📋 Liste des anomalies")
    st.dataframe(df_anomalies)

    # ------------------ Export CSV ------------------
    st.download_button(
        "📥 Télécharger les anomalies",
        df_anomalies.to_csv(index=False).encode("utf-8"),
        "anomalies_structurées.csv",
        "text/csv"
    )
