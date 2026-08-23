import pandas as pd
import joblib

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer


# ============================================================
# SCAMSHIELD AI - TF-IDF FEATURE EXTRACTION
# ============================================================

print("=" * 80)
print("SCAMSHIELD AI - TF-IDF FEATURE EXTRACTION")
print("=" * 80)


# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_FILE = BASE_DIR / "datasets" / "processed" / "train.csv"
TEST_FILE = BASE_DIR / "datasets" / "processed" / "test.csv"

FEATURE_DIR = BASE_DIR / "datasets" / "features"

VECTORIZER_FILE = FEATURE_DIR / "tfidf_vectorizer.joblib"


# ------------------------------------------------------------
# 2. CREATE FEATURE DIRECTORY
# ------------------------------------------------------------

FEATURE_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 3. LOAD TRAINING AND TESTING DATA
# ------------------------------------------------------------

print("\n1. LOADING DATASETS")

train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

print(f"Training emails : {len(train_df)}")
print(f"Testing emails  : {len(test_df)}")


# ------------------------------------------------------------
# 4. SEPARATE TEXT AND LABEL
# ------------------------------------------------------------

X_train_text = train_df["text"].fillna("")
y_train = train_df["label"]

X_test_text = test_df["text"].fillna("")
y_test = test_df["label"]


# ------------------------------------------------------------
# 5. CREATE TF-IDF VECTORIZER
# ------------------------------------------------------------

print("\n2. CREATING TF-IDF VECTORIZER")

vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    max_features=50000,
    sublinear_tf=True
)


# ------------------------------------------------------------
# 6. FIT ONLY ON TRAINING DATA
# ------------------------------------------------------------

print("\n3. FITTING TF-IDF ON TRAINING DATA")

X_train = vectorizer.fit_transform(X_train_text)

print(f"Training matrix shape: {X_train.shape}")


# ------------------------------------------------------------
# 7. TRANSFORM TEST DATA
# ------------------------------------------------------------

print("\n4. TRANSFORMING TEST DATA")

X_test = vectorizer.transform(X_test_text)

print(f"Testing matrix shape : {X_test.shape}")


# ------------------------------------------------------------
# 8. DISPLAY VOCABULARY SIZE
# ------------------------------------------------------------

print("\n5. TF-IDF INFORMATION")

print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")

print(f"Number of training samples: {X_train.shape[0]}")
print(f"Number of testing samples : {X_test.shape[0]}")
print(f"Number of features        : {X_train.shape[1]}")


# ------------------------------------------------------------
# 9. SAVE FEATURES
# ------------------------------------------------------------

print("\n6. SAVING FEATURES")

joblib.dump(X_train, FEATURE_DIR / "X_train_tfidf.joblib")
joblib.dump(X_test, FEATURE_DIR / "X_test_tfidf.joblib")

joblib.dump(y_train.to_numpy(), FEATURE_DIR / "y_train.joblib")
joblib.dump(y_test.to_numpy(), FEATURE_DIR / "y_test.joblib")

joblib.dump(vectorizer, VECTORIZER_FILE)

print(f"Saved: {FEATURE_DIR / 'X_train_tfidf.joblib'}")
print(f"Saved: {FEATURE_DIR / 'X_test_tfidf.joblib'}")
print(f"Saved: {FEATURE_DIR / 'y_train.joblib'}")
print(f"Saved: {FEATURE_DIR / 'y_test.joblib'}")
print(f"Saved: {VECTORIZER_FILE}")


# ------------------------------------------------------------
# 10. SAMPLE FEATURES
# ------------------------------------------------------------

print("\n7. SAMPLE VOCABULARY")

feature_names = vectorizer.get_feature_names_out()

print("First 20 features:")

for feature in feature_names[:20]:
    print(f"  {feature}")


# ------------------------------------------------------------
# 11. COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TF-IDF FEATURE EXTRACTION COMPLETE")
print("=" * 80)