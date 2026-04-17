import pandas as pd
import os

url = "https://raw.githubusercontent.com/gc521/DATA-607-Data-Acquisition-Mangement/main/spam_ham_dataset.csv"
print("Downloading Enron Spam Dataset (~5000 rows)...")
df_new = pd.read_csv(url)

# Keep only text and label_num, rename label_num to label
df_new = df_new[['text', 'label_num']].rename(columns={'label_num': 'label'})

# Load the existing custom hand-picked 80 rows
existing_path = r"d:\scam-detector\backend\dataset\scam_data.csv"
print("Loading existing custom dataset...")
df_existing = pd.read_csv(existing_path)

# Combine them
df_combined = pd.concat([df_existing, df_new], ignore_index=True)

# Drop any empty rows or duplicates
df_combined.dropna(subset=['text', 'label'], inplace=True)
df_combined.drop_duplicates(subset=['text'], inplace=True)

print(f"Total rows after combining: {len(df_combined)}")

# Save back to CSV
print("Saving merged dataset...")
df_combined.to_csv(existing_path, index=False)

print("Fetch complete! Ready to train.")
