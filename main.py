from create_hard_negatives import create_hard_negatives_pipeline
from train_classifier import train_classifiers
import os


def main():
    """
    Main execution function that:
    1. Generates/loads mock seed posts (bypassing BrightData scraper)
    2. Uses instagram_campaign_data.csv as campaign posts
    3. Creates hard negatives dataset from the seed posts
    4. Trains and compares multiple classifiers
    """
    # Define file paths
    seed_csv_path = "seed_posts.csv"
    campaign_data_path = "instagram_campaign_data.csv"
    dataset_pickle_path = "final_balanced_dataset.pkl"
    
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
        import pandas as pd
        seed_df = pd.read_csv(seed_csv_path)
        print(f"   - Total seed posts: {len(seed_df)}")
    
    # Verify campaign data exists
    if not os.path.exists(campaign_data_path):
        print(f"\n❌ Error: {campaign_data_path} not found!")
        print("   Please ensure instagram_campaign_data.csv exists.")
        return
    
    import pandas as pd
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
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 COMPLETE PIPELINE FINISHED!")
    print("=" * 60)
    print(f"\n📁 Generated Files:")
    print(f"   - Seed posts CSV: {seed_csv_path}")
    print(f"   - Campaign data CSV: {campaign_data_path}")
    print(f"   - Training dataset: {dataset_pickle_path}")
    print(f"   - Model results: ./results/")
    print(f"\n📊 Trained Models:")
    print(f"   - Logistic Regression")
    print(f"   - KNN (k=5, cosine)")
    print(f"   - BERT (DistilBERT)")
    print(f"\n💡 Data Flow:")
    print(f"   1. Seed posts (100 genuine campaign posts) → Positive samples")
    print(f"   2. Instagram dataset (20K posts) → Negative samples")
    print(f"   3. Balanced dataset → Train 3 classifiers")
    print(f"   4. Best model → Classify campaign posts in {campaign_data_path}")
    
    return {
        "dataset": dataset,
        "model_results": results,
        "comparison": comparison_df
    }


if __name__ == "__main__":
    main()
