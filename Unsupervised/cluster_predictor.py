import joblib
import numpy as np
from pathlib import Path
from utils import comma_tokenizer
from sklearn.metrics.pairwise import cosine_similarity
from resume_parser import parse_pdf_for_skills

_ROOT = Path(__file__).resolve().parents[1]

# Load models
vectorizer = joblib.load(_ROOT / "Unsupervised" / "skill_vectorizer.pkl")
kmeans = joblib.load(_ROOT / "Unsupervised" / "skill_kmeans_model.pkl")
cluster_labels = joblib.load(_ROOT / "Unsupervised" / "cluster_labels.pkl")

# Predict top 3 matching clusters from resume PDF
def predict_resume_clusters(pdf_path, skill_list_file="unique_skills.txt"):
    # Extract skills
    extracted_skills = parse_pdf_for_skills(pdf_path, skill_list_file)
    if not extracted_skills:
        return []

    # Vectorize skills
    vec = vectorizer.transform([extracted_skills])

    # Compare with cluster centers
    similarities = cosine_similarity(vec, kmeans.cluster_centers_)[0]
    top_indices = np.argsort(similarities)[::-1][:3]

    results = []
    for idx in top_indices:
        label = cluster_labels.get(idx, f"Cluster {idx}")
        score = similarities[idx]
        results.append((idx, label, score))

    return results

