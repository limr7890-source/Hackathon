from scraper.pipeline import run_pipeline
from create_hard_negatives import create_hard_negatives_pipeline
from train_classifier import train_classifiers

api_key = "c755ca2c-f0c7-478d-bcb0-750606dda714"


def main():
    """
    Main execution function that:
    1. Runs the scraper pipeline to get seed posts
    2. Creates hard negatives dataset from the seed posts
    3. Trains and compares multiple classifiers
    """
    # Define file paths
    seed_csv_path = "seed_posts.csv"
    dataset_pickle_path = "final_balanced_dataset.pkl"
    
    # Step 1: Run the scraper pipeline
    print("=" * 60)
    print("STEP 1: Running scraper pipeline...")
    print("=" * 60)
    
    pipeline_result = run_pipeline(
        input_csv_path="campaign_input.csv",
        output_csv_path="campaign_output.csv",
        api_key=api_key,
        seed_csv_path=seed_csv_path
    )
    
    print(f"\n✅ Pipeline completed!")
    print(f"   - Seed CSV: {pipeline_result['seed_path']}")
    print(f"   - Total posts: {pipeline_result['total_posts']}")
    print(f"   - Output: {pipeline_result['output_path']}")
    
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
    print(f"   - Training dataset: {dataset_pickle_path}")
    print(f"   - Model results: ./results/")
    print(f"\n📊 Trained Models:")
    print(f"   - Logistic Regression")
    print(f"   - KNN (k=5, cosine)")
    print(f"   - BERT (DistilBERT)")
    
    return {
        "pipeline_result": pipeline_result,
        "dataset": dataset,
        "model_results": results,
        "comparison": comparison_df
    }


if __name__ == "__main__":
    main()
