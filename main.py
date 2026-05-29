from create_hard_negatives import create_hard_negatives_pipeline
from train_classifier import train_classifiers
from sentence_transformers import SentenceTransformer
import pandas as pd
import pickle
import os


def classify_campaign_posts(model, embedder, campaign_csv_path, output_csv_path):
    """
    Classify posts in the campaign CSV using the trained model.
    
    Args:
        model: Trained classifier (e.g., Logistic Regression)
        embedder: SentenceTransformer model for encoding text
        campaign_csv_path: Path to instagram_campaign_data.csv
        output_csv_path: Path for output CSV with predictions
        
    Returns:
        DataFrame with predictions added
    """
    print("\n" + "=" * 60)
    print("STEP 4: Classifying campaign posts...")
    print("=" * 60)
    
    # Load campaign data
    print(f"Loading campaign data from {campaign_csv_path}...")
    df = pd.read_csv(campaign_csv_path)
    print(f"  Total posts to classify: {len(df)}")
    
    # Extract text content
    texts = df['content'].fillna('').astype(str).tolist()
    
    # Generate embeddings
    print("Generating embeddings for campaign posts...")
    embeddings = embedder.encode(texts, show_progress_bar=True)
    
    # Make predictions
    print("Making predictions...")
    predictions = model.predict(embeddings)
    probabilities = model.predict_proba(embeddings)[:, 1]  # Probability of being class 1 (good)
    
    # Add predictions to dataframe
    df['predicted_label'] = predictions
    df['confidence'] = probabilities
    
    # Add human-readable classification
    df['classification'] = df['predicted_label'].map({0: 'hijacked', 1: 'genuine'})
    
    # Save to new CSV
    df.to_csv(output_csv_path, index=False)
    
    # Print statistics
    num_genuine = (predictions == 1).sum()
    num_hijacked = (predictions == 0).sum()
    
    print(f"\n✅ Classification complete!")
    print(f"   Output saved to: {output_csv_path}")
    print(f"\n📊 Classification Results:")
    print(f"   - Genuine posts: {num_genuine} ({num_genuine/len(df)*100:.1f}%)")
    print(f"   - Hijacked posts: {num_hijacked} ({num_hijacked/len(df)*100:.1f}%)")
    
    # Show confidence distribution
    avg_confidence_genuine = df[df['predicted_label'] == 1]['confidence'].mean()
    avg_confidence_hijacked = df[df['predicted_label'] == 0]['confidence'].mean()
    
    print(f"\n📈 Average Confidence:")
    print(f"   - Genuine posts: {avg_confidence_genuine:.3f}")
    print(f"   - Hijacked posts: {1 - avg_confidence_hijacked:.3f}")
    
    # Show some examples
    print(f"\n🔍 Sample Classifications:")
    print("\nGenuine Posts (top 3 by confidence):")
    genuine_samples = df[df['predicted_label'] == 1].nlargest(3, 'confidence')
    for idx, row in genuine_samples.iterrows():
        print(f"  - @{row['username']}: {row['content'][:60]}... (confidence: {row['confidence']:.3f})")
    
    print("\nHijacked Posts (top 3 by confidence):")
    hijacked_samples = df[df['predicted_label'] == 0].nsmallest(3, 'confidence')
    for idx, row in hijacked_samples.iterrows():
        print(f"  - @{row['username']}: {row['content'][:60]}... (confidence: {1-row['confidence']:.3f})")
    
    return df


def main():
    """
    Main execution function that:
    1. Generates/loads mock seed posts (bypassing BrightData scraper)
    2. Uses instagram_campaign_data.csv as campaign posts
    3. Creates hard negatives dataset from the seed posts
    4. Trains and compares multiple classifiers
    5. Uses best model to classify campaign posts
    """
    # Define file paths
    seed_csv_path = "seed_posts.csv"
    campaign_data_path = "instagram_campaign_data.csv"
    dataset_pickle_path = "final_balanced_dataset.pkl"
    classified_output_path = "instagram_campaign_data_classified.csv"
    
    # Step 1: Generate seed posts if they don't exist
    print("=" * 60)
    print("STEP 1: Preparing seed posts...")
    print("=" * 60)
    
    if not os.path.exists(seed_csv_path):
        print(f"Generating {seed_csv_path}...")
        from generate_seed_posts import generate_seed_posts
        generate_seed_posts(100, seed_csv_path)
    else:
        print(f"✅ Seed posts already exist: {seed_csv_path}")
        seed_df = pd.read_csv(seed_csv_path)
        print(f"   - Total seed posts: {len(seed_df)}")
    
    # Verify campaign data exists
    if not os.path.exists(campaign_data_path):
        print(f"\n❌ Error: {campaign_data_path} not found!")
        print("   Please ensure instagram_campaign_data.csv exists.")
        return
    
    campaign_df = pd.read_csv(campaign_data_path)
    print(f"\n✅ Campaign data loaded: {campaign_data_path}")
    print(f"   - Total campaign posts: {len(campaign_df)}")
    
    # Step 2: Create hard negatives dataset from seed posts
    print("\n" + "=" * 60)
    print("STEP 2: Creating hard negatives dataset...")
    print("=" * 60)
    
    dataset = create_hard_negatives_pipeline(
        csv_path=seed_csv_path,
        output_path=dataset_pickle_path,
        max_negative_samples=20000
    )
    
    print(f"\n✅ Dataset created: {dataset_pickle_path}")
    
    # Step 3: Train and compare classifiers
    print("\n" + "=" * 60)
    print("STEP 3: Training classifiers...")
    print("=" * 60)
    
    results, comparison_df = train_classifiers(pickle_path=dataset_pickle_path)
    
    # Step 4: Use Logistic Regression to classify campaign posts
    print("\n" + "=" * 60)
    print("Using Logistic Regression model for classification...")
    print("=" * 60)
    
    # Load the embedder (same one used for training)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get the Logistic Regression model
    logistic_model = results["Logistic Regression"]["model"]
    
    # Classify campaign posts
    classified_df = classify_campaign_posts(
        model=logistic_model,
        embedder=embedder,
        campaign_csv_path=campaign_data_path,
        output_csv_path=classified_output_path
    )
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 COMPLETE PIPELINE FINISHED!")
    print("=" * 60)
    print(f"\n📁 Generated Files:")
    print(f"   - Seed posts CSV: {seed_csv_path}")
    print(f"   - Campaign data CSV: {campaign_data_path}")
    print(f"   - Classified output CSV: {classified_output_path}")
    print(f"   - Training dataset: {dataset_pickle_path}")
    print(f"   - Model results: ./results/")
    print(f"\n📊 Trained Models:")
    print(f"   - Logistic Regression (USED FOR CLASSIFICATION)")
    print(f"   - KNN (k=5, cosine)")
    print(f"   - BERT (DistilBERT)")
    print(f"\n💡 Data Flow:")
    print(f"   1. Seed posts (100 genuine campaign posts) → Positive samples")
    print(f"   2. Instagram dataset (20K posts) → Negative samples")
    print(f"   3. Balanced dataset → Train 3 classifiers")
    print(f"   4. Logistic Regression → Classify {len(classified_df)} campaign posts")
    print(f"   5. Results saved to: {classified_output_path}")
    
    return {
        "dataset": dataset,
        "model_results": results,
        "comparison": comparison_df,
        "classified_posts": classified_df
    }


if __name__ == "__main__":
    main()
