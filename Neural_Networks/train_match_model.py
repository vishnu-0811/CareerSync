"""Train and save the job-fit ANN + TF-IDF vectorizer (run once if artifacts are missing)."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from utils import comma_tokenizer  # noqa: E402

DATASET = _ROOT / "datasets" / "job_skills_dataset_corrected.csv"
MODEL_PATH = Path(__file__).resolve().parent / "match_score_model.h5"
VECTORIZER_PATH = Path(__file__).resolve().parent / "match_vectorizer.pkl"


def _normalize_skills(text: str) -> str:
    return text.lower().strip()


def _jaccard(a: str, b: str) -> float:
    sa = {s.strip() for s in a.split(",") if s.strip()}
    sb = {s.strip() for s in b.split(",") if s.strip()}
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _build_samples(df: pd.DataFrame, vectorizer: TfidfVectorizer, n_per_row: int = 3):
    samples: list[np.ndarray] = []
    labels: list[float] = []
    rng = random.Random(42)

    role_map: dict[str, list[str]] = {}
    for _, row in df.iterrows():
        title = row["Job Title"].strip().lower()
        skills = _normalize_skills(row["Skills Required"])
        role_map.setdefault(title, []).append(skills)

    rows = df.to_dict("records")
    for row in rows:
        role_skills = _normalize_skills(row["Skills Required"])
        role_key = row["Job Title"].strip().lower()
        skill_tokens = [s.strip() for s in role_skills.split(",") if s.strip()]

        for _ in range(n_per_row):
            if len(skill_tokens) >= 2:
                keep = rng.randint(max(1, len(skill_tokens) // 2), len(skill_tokens))
                resume_skills = ", ".join(rng.sample(skill_tokens, keep))
            else:
                resume_skills = role_skills

            if rng.random() < 0.7:
                jd_skills = role_skills
            else:
                other = rng.choice(rows)
                jd_skills = _normalize_skills(other["Skills Required"])

            alt_role = rng.choice(list(role_map[role_key]))
            exp_weight = rng.uniform(0.0, 1.0)

            vec_resume = vectorizer.transform([resume_skills]).toarray()[0]
            vec_jd = vectorizer.transform([jd_skills]).toarray()[0]
            vec_role = vectorizer.transform([alt_role]).toarray()[0]
            samples.append(np.concatenate([vec_resume, vec_jd, vec_role, [exp_weight]]))

            overlap_jd = _jaccard(resume_skills, jd_skills)
            overlap_role = _jaccard(resume_skills, alt_role)
            labels.append(0.45 * overlap_jd + 0.45 * overlap_role + 0.10 * exp_weight)

    return samples, labels


def main() -> None:
    df = pd.read_csv(DATASET)
    x_raw = df["Skills Required"].str.lower().str.replace(r"[^\w\s,]", "", regex=True)

    vectorizer = TfidfVectorizer(tokenizer=comma_tokenizer)
    vectorizer.fit(x_raw)

    samples, labels = _build_samples(df, vectorizer)
    x_train, _, y_train, _ = train_test_split(samples, labels, test_size=0.2, random_state=42)

    model = Sequential(
        [
            Dense(256, activation="relu", input_shape=(len(samples[0]),)),
            Dropout(0.3),
            Dense(128, activation="relu"),
            Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.fit(np.array(x_train), np.array(y_train), epochs=15, batch_size=32, validation_split=0.1, verbose=1)

    model.save(MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved vectorizer -> {VECTORIZER_PATH}")


if __name__ == "__main__":
    main()
