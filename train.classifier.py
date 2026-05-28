import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# =========================================================================
# 1. Loading the negative dataset from Cache in a fraction of a second (without Embedding model!)
# =========================================================================
print("Loading the pre-computed negative dataset from the Pickle file...")
with open("instagram_negatives_cache.pkl", "rb") as f:
    cache_data = pickle.load(f)

negative_texts = cache_data["texts"]
negative_embeddings = cache_data["embeddings"]
print(f"Successfully loaded {len(negative_texts)} vector-mapped negative posts.")

# =========================================================================
# 2. Connecting the final positive data (what your team collected from the official advertiser)
# =========================================================================
# Let's assume team members finished and brought you a list of real positive posts from the campaign:
final_positive_posts = [
    "Check out our new running shoes! Lightweight and durable #JustDoIt",
    "Run faster, push harder. The new collection is live now #JustDoIt",
    "Unboxing the new gym gear. Absolutely loving the design and comfort! #JustDoIt"
    # ... here you can insert the full expanded list
]

print("\nComputing Embeddings only for the positive posts (small amount, will take half a second)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
positive_embeddings = model.encode(final_positive_posts)

# Updating the campaign center based on the full and final data
campaign_center = np.mean(positive_embeddings, axis=0).reshape(1, -1)

# =========================================================================
# 3. Fast semantic filtering against the existing Cache
# =========================================================================
print("\nPerforming fast semantic filtering against the Cache (runs in milliseconds)...")
similarities = cosine_similarity(negative_embeddings, campaign_center).flatten()

easy_negatives = []
hard_negatives = []

for text, sim in zip(negative_texts, similarities):
    if sim < 0.2:
        easy_negatives.append(text)
    elif 0.2 <= sim < 0.45:
        hard_negatives.append(text)

print(f"✅ Updated distribution for the campaign: {len(easy_negatives)} easy, {len(hard_negatives)} hard.")

# =========================================================================
# 4. Preparing the final dataset for model training (X and y)
# =========================================================================
# Gold tip: To prevent Class Imbalance, we will take a proportional amount of negatives to positives.
# If we have, for example, 50 positive posts, we will take roughly 75 hard and 75 easy.
num_positives = len(final_positive_posts)
num_needed_negatives = min(num_positives * 2, len(hard_negatives))

# Sampling from the negatives
selected_hard = hard_negatives[:num_needed_negatives]
selected_easy = easy_negatives[:num_needed_negatives]

# Creating the unified Dataset
X_text = final_positive_posts + selected_hard + selected_easy
y = [1] * len(final_positive_posts) + [0] * (len(selected_hard) + len(selected_easy))

print(f"\n🎉 The final dataset for training the model is ready!")
print(f"Total positive examples (label 1): {y.count(1)}")
print(f"Total negative examples (label 0): {y.count(0)}")

# Now you can take X_text (or their Embeddings) and run a simple classifier on them!

