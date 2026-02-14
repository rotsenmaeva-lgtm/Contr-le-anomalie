import streamlit as st
import pandas as pd
import csv
from io import TextIOWrapper

st.set_page_config(page_title="Contrôle Anomalies", layout="wide")
st.title("🔍 Contrôle des anomalies fournisseurs")

uploaded_file = st.file_uploader("Importer Export_Balance (CSV)", type="csv")
# Read the CSV file, handling potential errors
try:
    df = pd.read_csv(uploaded_file, encoding="UTF-16", on_bad_lines='skip')  # Skip bad lines
    # Or you can use 'error' to raise an error on bad lines
    # df = pd.read_csv(uploaded_file, on_bad_lines='error')
except pd.errors.ParserError as e:
    print(f"Error reading CSV: {e}")
    # You can further inspect the error or the problematic line here
    # For example, print the line number and the line content
    line_number = int(str(e).split("line ")[1].split(",")[0])
    with open(uploaded_file, 'r', encoding="UTF-16") as f:
        for i, line in enumerate(f):
            if i == line_number - 1:
                print(f"Problematic line {line_number}: {line}")
                break

print(df.columns)
print(f"Nombre de colonnes détectées : {df.shape[1]}")
