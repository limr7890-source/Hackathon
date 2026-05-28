import numpy as np
import pickle
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("1. Loading the Instagram dataset from Hugging Face (text-only in advance)...")
# Smart loading of only the caption column to avoid touching images
dataset = load_dataset(
    "kkcosmos/instagram-images-with-captions", 
    split="train", 
    streaming=True,
    columns=["item_id", "caption"]
)

# Extracting posts as negative candidates
negative_candidates = []
for i, example in enumerate(dataset):
    if i >= 20000:  # Number of general posts wanted to process
        break
    
    if 'caption' in example and example['caption']:
        text = str(example['caption']).strip()
        # Filtering posts that are too short (less than 3 words)
        if len(text.split()) >= 3:
            negative_candidates.append(text)

print(f"✅ Success! Collected {len(negative_candidates)} posts in seconds.")

print("\n2. Loading Embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# The current positive examples for your campaign
positive_posts = [
    "Check out our new running shoes! Lightweight and durable #JustDoIt",
    "Run faster, push harder. The new collection is live now #JustDoIt"
]

positive_embeddings = model.encode(positive_posts)
campaign_center = np.mean(positive_embeddings, axis=0).reshape(1, -1)

print("\n3. Computing Embeddings for negative posts (heavy step - will only run this time)...")
candidate_embeddings = model.encode(negative_candidates)

# --- 🔥 Here is where the magic happens: saving everything to Pickle for the future ---
print("\n4. Saving all raw data and vectors to a Pickle file...")
cache_data = {
    "texts": negative_candidates,
    "embeddings": candidate_embeddings
}

with open("instagram_negatives_cache.pkl", "wb") as f:
    pickle.dump(cache_data, f)
print("✅ Cache file saved: instagram_negatives_cache.pkl")

print("\n5. Computing semantic distances and filtering by Thresholds for the current campaign...")
similarities = cosine_similarity(candidate_embeddings, campaign_center).flatten()

easy_negatives = []
hard_negatives = []

for text, sim in zip(negative_candidates, similarities):
    if sim < 0.2:
        easy_negatives.append(text)
    elif 0.2 <= sim < 0.45:
        hard_negatives.append(text)

# Saving the plain text files for your team members
with open("easy_negatives.txt", "w", encoding="utf-8") as f:
    for post in easy_negatives:
        f.write(post.replace("\n", " ") + "\n")

with open("hard_negatives.txt", "w", encoding="utf-8") as f:
    for post in hard_negatives:
        f.write(post.replace("\n", " ") + "\n")

print(f"\n🎉 Everything is ready and secured!")
print(f"✅ Created {len(easy_negatives)} Easy Negatives examples")
print(f"✅ Created {len(hard_negatives)} Hard Negatives examples")