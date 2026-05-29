import numpy as np
import pickle
import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def load_positive_posts_from_csv(csv_path):
    """
    Load positive posts from a CSV file.
    
    Args:
        csv_path (str): Path to the CSV file containing positive posts
        
    Returns:
        list: List of positive post texts extracted from the 'content' column
    """
    print(f"1. Loading positive posts from CSV: {csv_path}...")
    df = pd.read_csv(csv_path)
    
    if 'content' not in df.columns:
        raise ValueError(f"CSV file must contain a 'content' column. Found columns: {df.columns.tolist()}")
    
    # Extract content and filter out empty/null values
    positive_texts = df['content'].dropna().astype(str).str.strip().tolist()
    positive_texts = [text for text in positive_texts if len(text.split()) >= 3]
    
    print(f"   - Loaded {len(positive_texts)} positive posts")
    return positive_texts


def compute_embeddings(texts, model_name="all-MiniLM-L6-v2"):
    """
    Compute embeddings for a list of texts.
    
    Args:
        texts (list): List of text strings
        model_name (str): Name of the SentenceTransformer model
        
    Returns:
        tuple: (embedder model, embeddings array)
    """
    print(f"2. Computing embeddings using {model_name}...")
    embedder = SentenceTransformer(model_name)
    embeddings = embedder.encode(texts)
    print(f"   - Computed {len(embeddings)} embeddings")
    return embedder, embeddings


def fetch_negative_candidates(max_samples=20000):
    """
    Fetch negative candidate posts from Instagram dataset.
    
    Args:
        max_samples (int): Maximum number of samples to fetch
        
    Returns:
        list: List of negative candidate texts
    """
    print(f"3. Pulling negative candidates from Instagram (Hugging Face)...")
    dataset = load_dataset(
        "kkcosmos/instagram-images-with-captions", 
        split="train", 
        streaming=True,
        columns=["item_id", "caption"]
    )

    negative_candidates = []
    for i, example in enumerate(dataset):
        if i >= max_samples:
            break
        if 'caption' in example and example['caption']:
            text = str(example['caption']).strip()
            if len(text.split()) >= 3:
                negative_candidates.append(text)
    
    print(f"   - Fetched {len(negative_candidates)} negative candidates")
    return negative_candidates


def filter_negatives_by_similarity(candidate_embeddings, campaign_center, negative_candidates, 
                                   easy_threshold=0.2, hard_threshold=0.45):
    """
    Filter negative candidates into easy and hard negatives based on similarity.
    
    Args:
        candidate_embeddings: Embeddings of negative candidates
        campaign_center: Center vector of positive campaign posts
        negative_candidates: List of negative candidate texts
        easy_threshold (float): Similarity threshold for easy negatives
        hard_threshold (float): Similarity threshold for hard negatives
        
    Returns:
        tuple: (easy_neg_indices, hard_neg_indices)
    """
    print("5. Computing semantic distances and filtering into hard and easy...")
    similarities = cosine_similarity(candidate_embeddings, campaign_center).flatten()

    easy_neg_indices = []
    hard_neg_indices = []

    for idx, sim in enumerate(similarities):
        if sim < easy_threshold:
            easy_neg_indices.append(idx)
        elif easy_threshold <= sim < hard_threshold:
            hard_neg_indices.append(idx)
    
    print(f"   - Found {len(easy_neg_indices)} easy negatives (similarity < {easy_threshold})")
    print(f"   - Found {len(hard_neg_indices)} hard negatives ({easy_threshold} <= similarity < {hard_threshold})")
    
    return easy_neg_indices, hard_neg_indices


def create_balanced_dataset(positive_texts, positive_embeddings, negative_candidates, 
                           candidate_embeddings, easy_neg_indices, hard_neg_indices):
    """
    Create a balanced dataset with positives and negatives (max 2x negatives).
    
    Args:
        positive_texts: List of positive post texts
        positive_embeddings: Embeddings of positive posts
        negative_candidates: List of negative candidate texts
        candidate_embeddings: Embeddings of negative candidates
        easy_neg_indices: Indices of easy negatives
        hard_neg_indices: Indices of hard negatives
        
    Returns:
        dict: Dictionary containing texts, embeddings, and labels
    """
    print("6. Performing balanced sampling (max 2x negatives relative to positives)...")
    num_positives = len(positive_texts)
    max_negatives_per_type = num_positives  # Equal amount of hard and easy ones

    selected_hard_idx = hard_neg_indices[:max_negatives_per_type]
    selected_easy_idx = easy_neg_indices[:max_negatives_per_type]
    final_neg_indices = selected_hard_idx + selected_easy_idx

    sampled_negative_texts = [negative_candidates[i] for i in final_neg_indices]
    sampled_negative_embeddings = candidate_embeddings[final_neg_indices]

    print("7. Packing all relevant samples with embeddings, text, and labels...")
    
    # Combine all texts
    all_texts = positive_texts + sampled_negative_texts

    # Combine all embeddings
    all_embeddings = np.vstack([positive_embeddings, sampled_negative_embeddings])

    # Create labels: 1 for positives, 0 for negatives
    all_labels = [1] * len(positive_texts) + [0] * len(sampled_negative_texts)

    # Create the final dataset structure
    final_dataset = {
        "texts": all_texts,
        "embeddings": all_embeddings,
        "labels": all_labels
    }
    
    return final_dataset


def save_dataset_to_pickle(dataset, output_path="final_balanced_dataset.pkl"):
    """
    Save the dataset to a pickle file.
    
    Args:
        dataset (dict): Dataset dictionary with texts, embeddings, and labels
        output_path (str): Path to save the pickle file
    """
    with open(output_path, "wb") as f:
        pickle.dump(dataset, f)
    
    print(f" The final dataset file is ready! ({output_path})")
    print(f"   - Total samples: {len(dataset['texts'])}")
    print(f"   - Positives (label=1): {sum(dataset['labels'])}")
    print(f"   - Negatives (label=0): {len(dataset['labels']) - sum(dataset['labels'])}")
    print(f"   - Embeddings shape: {dataset['embeddings'].shape}")


def create_hard_negatives_pipeline(csv_path, output_path="final_balanced_dataset.pkl", 
                                   max_negative_samples=20000, model_name="all-MiniLM-L6-v2"):
    """
    Main pipeline function to create hard negatives dataset from a CSV file.
    
    Args:
        csv_path (str): Path to CSV file containing positive posts (must have 'content' column)
        output_path (str): Path to save the output pickle file
        max_negative_samples (int): Maximum number of negative samples to fetch
        model_name (str): Name of the SentenceTransformer model to use
        
    Returns:
        dict: The final dataset dictionary
    """
    # Step 1: Load positive posts from CSV
    positive_texts = load_positive_posts_from_csv(csv_path)
    
    # Step 2: Compute embeddings for positive posts
    embedder, positive_embeddings = compute_embeddings(positive_texts, model_name)
    
    # Compute campaign center
    campaign_center = np.mean(positive_embeddings, axis=0).reshape(1, -1)
    
    # Step 3: Fetch negative candidates
    negative_candidates = fetch_negative_candidates(max_negative_samples)
    
    # Step 4: Compute embeddings for negative candidates
    print(f"4. Computing embeddings for {len(negative_candidates)} negative candidates...")
    candidate_embeddings = embedder.encode(negative_candidates)
    
    # Step 5: Filter negatives by similarity
    easy_neg_indices, hard_neg_indices = filter_negatives_by_similarity(
        candidate_embeddings, campaign_center, negative_candidates
    )
    
    # Step 6: Create balanced dataset
    final_dataset = create_balanced_dataset(
        positive_texts, positive_embeddings, negative_candidates,
        candidate_embeddings, easy_neg_indices, hard_neg_indices
    )
    
    # Step 7: Save to pickle
    save_dataset_to_pickle(final_dataset, output_path)
    
    return final_dataset


# Main execution
if __name__ == "__main__":
    # Example usage
    csv_path = "seed_posts.csv"
    output_path = "final_balanced_dataset.pkl"
    
    dataset = create_hard_negatives_pipeline(
        csv_path=csv_path,
        output_path=output_path,
        max_negative_samples=20000
    )
