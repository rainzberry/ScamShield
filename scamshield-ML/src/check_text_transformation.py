import pandas as pd
import re
import os


folder = "datasets/raw"

source_files = [
    "CEAS_08.csv",
    "Enron.csv",
    "Ling.csv",
    "Nazario.csv",
    "Nigerian_Fraud.csv",
    "SpamAssasin.csv"
]


def normalize_text(text):
    """
    Basic normalization similar to common
    text preprocessing pipelines.
    """

    if pd.isna(text):
        text = ""

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Replace URLs with space
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Keep only letters and numbers
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


print("=" * 80)
print("SCAMSHIELD AI - TEXT TRANSFORMATION CHECK")
print("=" * 80)


for file in source_files:

    path = os.path.join(folder, file)

    df = pd.read_csv(path)

    print("\n" + "-" * 80)
    print(file)
    print("-" * 80)

    # Create subject + body
    subject = df["subject"].fillna("")
    body = df["body"].fillna("")

    combined_text = subject + " " + body

    normalized = combined_text.apply(normalize_text)

    print("Rows:", len(df))

    print("Example original:")
    print(combined_text.iloc[0][:300])

    print("\nExample normalized:")
    print(normalized.iloc[0][:300])


print("\n" + "=" * 80)
print("TEXT TRANSFORMATION CHECK COMPLETE")
print("=" * 80)