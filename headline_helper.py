"""
Headline helper using a tiny local model.
Generates headline suggestions based on a topic and ranks them.
"""

from sentence_transformers import SentenceTransformer, util

# Small, fast (~90MB) model suitable for CPU
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = SentenceTransformer(MODEL_NAME)

TEMPLATES = [
    "How to {topic} in 5 Minutes",
    "The Ultimate Guide to {topic}",
    "Top 5 Tips for {topic}",
    "Avoid These 5 Mistakes in {topic}",
    "{topic}: What You Must Know Now",
    "Boost Your {topic} Results Today",
    "{topic} Checklist for Fast Wins",
    "Secrets to Winning at {topic}",
]


def suggest_headlines(topic: str, n: int = 5):
    topic_clean = (topic or "").strip() or "your SEO"
    candidates = [t.format(topic=topic_clean) for t in TEMPLATES]

    topic_emb = _model.encode(topic_clean, convert_to_tensor=True)
    cand_embs = _model.encode(candidates, convert_to_tensor=True)
    sims = util.cos_sim(topic_emb, cand_embs).tolist()[0]
    ranked = sorted(zip(candidates, sims), key=lambda x: x[1], reverse=True)
    return [h for h, _ in ranked[:n]]


if __name__ == "__main__":
    for h in suggest_headlines("WebGL performance optimization", n=5):
        print(h)
