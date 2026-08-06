import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from utils import comma_tokenizer
import joblib
import warnings
warnings.filterwarnings("ignore")


# Load your dataset
df = pd.read_csv('../datasets/job_skills_dataset_corrected.csv')
df = df.dropna(subset=["Skills Required", "Job Category"])
df["Skills Required"] = df["Skills Required"].str.lower().str.replace(r"[^\w\s,]", "", regex=True)

# Vectorize using TF-IDF
vectorizer = TfidfVectorizer(tokenizer=comma_tokenizer)
X = vectorizer.fit_transform(df["Skills Required"])

# Determine best k using silhouette score
best_k = 0
best_score = -1

for k in range(2, 16):
    model = KMeans(n_clusters=k, random_state=42)
    labels = model.fit_predict(X)
    score = silhouette_score(X, labels)
    if score > best_score:
        best_score = score
        best_k = k

print(f"✅ Best k: {best_k} with silhouette score: {best_score:.4f}")

# Fit final model with best_k
kmeans = KMeans(n_clusters=best_k, random_state=42)
df["Cluster"] = kmeans.fit_predict(X)

# Label each cluster using most common Job Category
cluster_labels = {}
for cid in range(best_k):
    top_label = df[df["Cluster"] == cid]["Job Category"].mode()[0]
    cluster_labels[cid] = top_label
    print(f"Cluster {cid} → {top_label}")

# Save model and components
joblib.dump(vectorizer, "skill_vectorizer.pkl")
joblib.dump(kmeans, "skill_kmeans_model.pkl")
joblib.dump(cluster_labels, "cluster_labels.pkl")

print("✅ Model, vectorizer, and cluster labels saved successfully.")
