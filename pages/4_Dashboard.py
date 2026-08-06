import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from sidebar_ui import init_app_layout, render_app_footer

st.set_page_config(page_title="CareerSync - Dashboard", layout="wide")
init_app_layout("dashboard")

import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
)

from utils import comma_tokenizer  # noqa: F401 — required for TF-IDF unpickle

_model_dir = _ROOT / "Supervised"
vectorizer = joblib.load(_model_dir / "tfidf_vectorizer.pkl")
label_encoder = joblib.load(_model_dir / "label_encoder.pkl")
X_test = joblib.load(_model_dir / "X_test.pkl")
y_test = joblib.load(_model_dir / "y_test.pkl")

lr_model = joblib.load(_model_dir / "logistic_regression_model.pkl")
rf_model = joblib.load(_model_dir / "random_forest_model.pkl")
svm_model = joblib.load(_model_dir / "svm_model.pkl")

models = {
    "Logistic Regression": lr_model,
    "Random Forest": rf_model,
    "SVM": svm_model,
}


def plot_confusion_matrix(y_true, y_pred, classes, title):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes,
        ax=ax,
    )
    ax.set_title(f"Confusion Matrix: {title}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    st.pyplot(fig)
    plt.close(fig)


def plot_precision_recall_curve(y_true, y_score, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    for i in range(len(label_encoder.classes_)):
        precision, recall, _ = precision_recall_curve(
            (y_true == i).astype(int), y_score[:, i]
        )
        ax.plot(recall, precision, label=f"Class {label_encoder.classes_[i]}")
    ax.set_title(f"Precision-Recall Curve: {title}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend()
    ax.grid()
    st.pyplot(fig)
    plt.close(fig)


st.title("Model Performance Dashboard")

model_name = st.selectbox("Select Model", list(models.keys()))
model = models[model_name]

y_pred = model.predict(X_test)
y_score = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

st.subheader("Confusion Matrix")
plot_confusion_matrix(y_test, y_pred, label_encoder.classes_, model_name)

st.subheader("Classification Report")
report = classification_report(
    y_test, y_pred, target_names=label_encoder.classes_, output_dict=True
)
st.dataframe(report)

st.subheader("Accuracy")
st.write(f"{model_name} Accuracy: {accuracy_score(y_test, y_pred):.4f}")

if y_score is not None:
    st.subheader("Precision-Recall Curve")
    plot_precision_recall_curve(y_test, y_score, model_name)

render_app_footer()
