import joblib
import pandas as pd

from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# SCAMSHIELD AI - MODEL TRAINING
# ============================================================

print("=" * 80)
print("SCAMSHIELD AI - MODEL TRAINING")
print("=" * 80)


# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURE_DIR = BASE_DIR / "datasets" / "features"

MODEL_DIR = BASE_DIR / "models"

RESULT_DIR = BASE_DIR / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. LOAD TF-IDF FEATURES
# ------------------------------------------------------------

print("\n1. LOADING TF-IDF FEATURES")

X_train = joblib.load(
    FEATURE_DIR / "X_train_tfidf.joblib"
)

X_test = joblib.load(
    FEATURE_DIR / "X_test_tfidf.joblib"
)

y_train = joblib.load(
    FEATURE_DIR / "y_train.joblib"
)

y_test = joblib.load(
    FEATURE_DIR / "y_test.joblib"
)

print(f"Training features: {X_train.shape}")
print(f"Testing features : {X_test.shape}")


# ------------------------------------------------------------
# 3. DEFINE MODELS
# ------------------------------------------------------------

print("\n2. INITIALIZING MODELS")

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Multinomial Naive Bayes": MultinomialNB(),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ),

    "MLP Neural Network": MLPClassifier(
        hidden_layer_sizes=(128,),
        activation="relu",
        solver="adam",
        max_iter=30,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=5
    )
}


# ------------------------------------------------------------
# 4. TRAIN AND EVALUATE MODELS
# ------------------------------------------------------------

results = []

trained_models = {}


for model_name, model in models.items():

    print("\n" + "-" * 80)
    print(f"TRAINING: {model_name}")
    print("-" * 80)

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    print("Training model...")

    model.fit(X_train, y_train)

    trained_models[model_name] = model

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    print("Generating predictions...")

    y_pred = model.predict(X_test)

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    # --------------------------------------------------------
    # STORE RESULTS
    # --------------------------------------------------------

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    # --------------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------------

    print("\nPerformance:")

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    # --------------------------------------------------------
    # CLASSIFICATION REPORT
    # --------------------------------------------------------

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Normal",
                "Phishing"
            ],
            zero_division=0
        )
    )

    # --------------------------------------------------------
    # CONFUSION MATRIX
    # --------------------------------------------------------

    cm = confusion_matrix(y_test, y_pred)

    print("Confusion Matrix:")

    print(cm)


# ------------------------------------------------------------
# 5. CREATE RESULTS DATAFRAME
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("MODEL COMPARISON")
print("=" * 80)

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="F1 Score",
    ascending=False
).reset_index(drop=True)


print("\n")

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ------------------------------------------------------------
# 6. SAVE RESULTS
# ------------------------------------------------------------

results_file = RESULT_DIR / "model_comparison.csv"

results_df.to_csv(
    results_file,
    index=False
)

print(
    f"\nResults saved to: {results_file}"
)


# ------------------------------------------------------------
# 7. IDENTIFY BEST BASELINE MODEL
# ------------------------------------------------------------

best_model_name = results_df.iloc[0]["Model"]

print("\n" + "=" * 80)
print("BEST BASELINE MODEL")
print("=" * 80)

print(f"Model: {best_model_name}")

print(
    f"F1 Score: "
    f"{results_df.iloc[0]['F1 Score']:.4f}"
)


# ------------------------------------------------------------
# 8. SAVE ALL TRAINED MODELS
# ------------------------------------------------------------

print("\nSAVING TRAINED MODELS")

for model_name, model in trained_models.items():

    filename = (
        model_name
        .lower()
        .replace(" ", "_")
        .replace("-", "")
        + ".joblib"
    )

    model_path = MODEL_DIR / filename

    joblib.dump(
        model,
        model_path
    )

    print(f"Saved: {model_path}")


# ------------------------------------------------------------
# 9. COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("MODEL TRAINING COMPLETE")
print("=" * 80)