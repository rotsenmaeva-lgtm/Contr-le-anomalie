import streamlit as st
import pandas as pd
# Read the CSV file, handling potential errors
try:
    df = pd.read_csv(file_path, encoding="UTF-16", on_bad_lines='skip')  # Skip bad lines
    # Or you can use 'error' to raise an error on bad lines
    # df = pd.read_csv(file_path, on_bad_lines='error')
except pd.errors.ParserError as e:
    print(f"Error reading CSV: {e}")
    # You can further inspect the error or the problematic line here
    # For example, print the line number and the line content
    line_number = int(str(e).split("line ")[1].split(",")[0])
    with open(file_path, 'r', encoding="UTF-16") as f:
        for i, line in enumerate(f):
            if i == line_number - 1:
                print(f"Problematic line {line_number}: {line}")
                break

print(df.columns)
print(f"Nombre de colonnes détectées : {df.shape[1]}")
