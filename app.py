import streamlit as st
import pandas as pd

st.set_page_config(page_title="Contrôle Anomalies", layout="wide")

st.title("🔍 Contrôle des anomalies fournisseurs")

uploaded_file = st.file_uploader("Importer Export_Balance (CSV)", type="csv")

if uploaded_file:

    # ------------------ Lecture CSV robuste ------------------
    try:
        balance = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
    except Exception as e1:
        try:
            balance = pd.read_csv(uploaded_file, sep=",", encoding="utf-8")
        except Exception as e2:
            try:
                balance = pd.read_csv(uploaded_file, sep=",", encoding="utf-16")
            except Exception as e3:
                st.error(f"⚠️ Impossible de lire le fichier CSV.\n"
                         f"Tentative 1 : {e1}\n"
                         f"Tentative 2 : {e2}\n"
                         f"Tentative 3 : {e3}")
                st.stop()

    # ------------------ Normalisation des colonnes ------------------
    balance.columns = [str(col).strip() for col in balance.columns]
    balance.columns = [col.replace("\ufeff", "") for col in balance.columns]
    st.write("✅ Colonnes détectées :", balance.columns.tolist())

    # ------------------ Nettoyage et conversion ------------------
    # Débit et Crédit
    for col in ["Débit", "Crédit"]:
        if col in balance.columns:
            balance[col] = balance[col].fillna(0)
            balance[col] = balance[col].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)
    # N° facture
    if "N° facture" in balance.columns:
        balance["N° facture"] = balance["N° facture"].fillna("").astype(str).str.strip()

    # Vérifie colonnes essentielles
    if "N° facture" not in balance.columns or "Crédit" not in balance.columns:
        st.error("⚠️ Colonnes 'N° facture' ou 'Crédit' manquantes !")
        st.stop()

    # Nettoyage final
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

    # ------------------ Création DataFrame anomalies ------------------
    df_anomalies = pd.DataFrame(anomalies)

    # ------------------ Calcul KPI ------------------
    total_pieces = len(balance)
    total_anomalies = len(df_anomalies)
    taux_anomalie = round((total_anomalies / total_pieces) * 100, 2) if total_pieces > 0 else 0

    # ------------------ Affichage KPI ------------------
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
