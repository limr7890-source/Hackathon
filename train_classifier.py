import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from sklearn.neighbors import KNeighborsClassifier

import numpy as np
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import evaluate

import pickle


def load_training_data(pickle_path="final_balanced_dataset.pkl"):
    """
    Load the training dataset from the pickle file created by create_hard_negatives.py
    
    Args:
        pickle_path (str): Path to the pickle file containing the dataset
        
    Returns:
        tuple: (X, y, all_texts) where X is embeddings, y is labels, all_texts is the text data
    """
    print(f"Loading training dataset from {pickle_path}...")
    
    with open(pickle_path, "rb") as f:
        dataset = pickle.load(f)
    
    X = dataset["embeddings"]
    y = np.array(dataset["labels"])
    all_texts = dataset["texts"]
    
    num_positives = sum(y)
    num_negatives = len(y) - num_positives
    
    print(f"Dataset loaded successfully:")
    print(f"   - Total samples: {len(y)}")
    print(f"   - Positive examples: {num_positives}")
    print(f"   - Negative examples: {num_negatives}")
    print(f"   - Ratio (pos:neg): 1:{num_negatives/num_positives:.1f}")
    
    return X, y, all_texts


def prepare_train_test_split(X, y, all_texts, test_size=0.2, random_state=42):
    """
    Split the data into training and testing sets.
    
    Args:
        X: Feature embeddings
        y: Labels
        all_texts: Text data
        test_size: Proportion of test set
        random_state: Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test, train_df, test_df)
    """
    print(f"\nSplitting data into train/test (test_size={test_size})...")
    
    indices = np.arange(len(X))
    train_idx, test_idx = train_test_split(indices, test_size=test_size, random_state=random_state, stratify=y)

    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]

    train_df = pd.DataFrame({'text': [all_texts[i] for i in train_idx], 'label': y_train})
    test_df = pd.DataFrame({'text': [all_texts[i] for i in test_idx], 'label': y_test})

    print(f"Train/Test split completed:")
    print(f"   - Train size: {len(X_train)}")
    print(f"   - Test size: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test, train_df, test_df


def train_logistic_regression(X_train, X_test, y_train, y_test):
    """
    Train and evaluate Logistic Regression classifier.
    
    Args:
        X_train, X_test: Training and test embeddings
        y_train, y_test: Training and test labels
        
    Returns:
        dict: Results containing model, predictions, and metrics
    """
    print("\n" + "="*60)
    print("CLASSIFIER 1: Logistic Regression")
    print("="*60)
    
    # Training a logistic regression model on the training data
    logistic_model = LogisticRegression(max_iter=1000)
    logistic_model.fit(X_train, y_train)
    
    # Predictions
    test_predictions = logistic_model.predict(X_test)
    probabilities = logistic_model.predict_proba(X_test)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, test_predictions)
    precision = precision_score(y_test, test_predictions, average='binary')
    recall = recall_score(y_test, test_predictions, average='binary')
    f1 = f1_score(y_test, test_predictions, average='binary')
    
    print("\nEvaluation Results:")
    print(classification_report(y_test, test_predictions))
    
    return {
        "model": logistic_model,
        "predictions": test_predictions,
        "probabilities": probabilities,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def train_knn(X_train, X_test, y_train, y_test, n_neighbors=5):
    """
    Train and evaluate KNN classifier with cosine distance.
    
    Args:
        X_train, X_test: Training and test embeddings
        y_train, y_test: Training and test labels
        n_neighbors: Number of neighbors to use
        
    Returns:
        dict: Results containing model, predictions, and metrics
    """
    print("\n" + "="*60)
    print("CLASSIFIER 2: KNN with Cosine Distance")
    print("="*60)
    
    # Setting n_neighbors=5 (looks at the 5 closest posts)
    # Using 'cosine' metric for high-dimensional text embeddings
    knn_model = KNeighborsClassifier(n_neighbors=n_neighbors, metric='cosine')
    knn_model.fit(X_train, y_train)
    
    # Predict classes for the test set
    test_predictions = knn_model.predict(X_test)
    
    # Predict probabilities
    # For KNN, probability is calculated as the fraction of neighbors with the same label
    probabilities = knn_model.predict_proba(X_test)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, test_predictions)
    precision = precision_score(y_test, test_predictions, average='binary')
    recall = recall_score(y_test, test_predictions, average='binary')
    f1 = f1_score(y_test, test_predictions, average='binary')
    
    print("\nEvaluation Results:")
    print(classification_report(y_test, test_predictions))
    
    return {
        "model": knn_model,
        "predictions": test_predictions,
        "probabilities": probabilities,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def train_bert(train_df, test_df, y_test, model_name="distilbert-base-uncased", num_epochs=3):
    """
    Train and evaluate BERT (DistilBERT) classifier.
    
    Args:
        train_df: Training dataframe with 'text' and 'label' columns
        test_df: Test dataframe with 'text' and 'label' columns
        y_test: Test labels
        model_name: Pretrained model name
        num_epochs: Number of training epochs
        
    Returns:
        dict: Results containing trainer, predictions, and metrics
    """
    print("\n" + "="*60)
    print("CLASSIFIER 3: BERT Fine-tuning (DistilBERT)")
    print("="*60)
    
    # 1. Convert our Pandas DataFrames into Hugging Face Datasets
    train_dataset = Dataset.from_pandas(train_df[['text', 'label']].reset_index(drop=True))
    test_dataset = Dataset.from_pandas(test_df[['text', 'label']].reset_index(drop=True))
    
    # 2. Load the Tokenizer for DistilBERT
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # 3. Define tokenization function
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=256)
    
    # 4. Tokenize the datasets
    print("Tokenizing text datasets...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_test = test_dataset.map(tokenize_function, batched=True)
    
    # 5. Load the base DistilBERT model configured for binary classification (num_labels=2)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    # 6. Define the evaluation metric (Accuracy)
    metric = evaluate.load("accuracy")
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        acc = metric.compute(predictions=predictions, references=labels)
        f1 = f1_score(labels, predictions, average='binary')
        return {"accuracy": acc["accuracy"], "f1": f1}
    
    # 7. Define Training Arguments
    # We keep epochs low (3) and batch size small for local machine safety
    training_args = TrainingArguments(
        output_dir="./results",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=num_epochs,
        weight_decay=0.01,
        eval_strategy="epoch",  # Changed from evaluation_strategy
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=10
    )
    
    # 8. Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        compute_metrics=compute_metrics,
    )
    
    # 9. Launch the Training process!
    print("\nTraining BERT... This might take a few minutes.")
    trainer.train()
    
    # 10. Final Evaluation
    print("\nFinal Evaluation Results:")
    eval_results = trainer.evaluate()
    print(eval_results)
    
    predictions_output = trainer.predict(tokenized_test)
    bert_predictions = np.argmax(predictions_output.predictions, axis=-1)
    print(classification_report(y_test, bert_predictions))
    
    # Metrics
    accuracy = accuracy_score(y_test, bert_predictions)
    precision = precision_score(y_test, bert_predictions, average='binary')
    recall = recall_score(y_test, bert_predictions, average='binary')
    f1 = f1_score(y_test, bert_predictions, average='binary')
    
    return {
        "trainer": trainer,
        "predictions": bert_predictions,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "eval_results": eval_results
    }


def compare_models(results_dict):
    """
    Create a comparison table of all models.
    
    Args:
        results_dict: Dictionary with model names as keys and results as values
    """
    print("\n" + "="*60)
    print("MODEL COMPARISON")
    print("="*60)
    
    # Create comparison dataframe
    comparison_data = []
    for model_name, results in results_dict.items():
        comparison_data.append({
            "Model": model_name,
            "Accuracy": f"{results['accuracy']:.4f}",
            "Precision": f"{results['precision']:.4f}",
            "Recall": f"{results['recall']:.4f}",
            "F1-Score": f"{results['f1']:.4f}"
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print("\n", comparison_df.to_string(index=False))
    
    # Find best model for each metric
    print("\n" + "-"*60)
    print("BEST PERFORMERS:")
    print("-"*60)
    
    best_accuracy = max(results_dict.items(), key=lambda x: x[1]['accuracy'])
    best_precision = max(results_dict.items(), key=lambda x: x[1]['precision'])
    best_recall = max(results_dict.items(), key=lambda x: x[1]['recall'])
    best_f1 = max(results_dict.items(), key=lambda x: x[1]['f1'])
    
    print(f"Best Accuracy:  {best_accuracy[0]} ({best_accuracy[1]['accuracy']:.4f})")
    print(f"Best Precision: {best_precision[0]} ({best_precision[1]['precision']:.4f})")
    print(f"Best Recall:    {best_recall[0]} ({best_recall[1]['recall']:.4f})")
    print(f"Best F1-Score:  {best_f1[0]} ({best_f1[1]['f1']:.4f})")
    
    return comparison_df


def train_classifiers(pickle_path="final_balanced_dataset.pkl"):
    """
    Main function to train all three classifiers from the pickle dataset.
    
    Args:
        pickle_path (str): Path to the pickle file containing the dataset
    """
    print("\n" + "="*60)
    print("STARTING CLASSIFIER TRAINING PIPELINE")
    print("="*60)
    
    # Load the dataset from pickle
    X, y, all_texts = load_training_data(pickle_path)
    
    # Prepare train/test split
    X_train, X_test, y_train, y_test, train_df, test_df = prepare_train_test_split(X, y, all_texts)
    
    # Train all models
    results = {}
    
    # 1. Logistic Regression
    results["Logistic Regression"] = train_logistic_regression(X_train, X_test, y_train, y_test)
    
    # 2. KNN
    results["KNN (k=5, cosine)"] = train_knn(X_train, X_test, y_train, y_test, n_neighbors=5)
    
    # 3. BERT
    results["BERT (DistilBERT)"] = train_bert(train_df, test_df, y_test, num_epochs=3)
    
    # Compare all models
    comparison_df = compare_models(results)
    
    print("\n" + "="*60)
    print("🎉 TRAINING COMPLETE!")
    print("="*60)
    
    return results, comparison_df


# Main execution
if __name__ == "__main__":
    results, comparison = train_classifiers("final_balanced_dataset.pkl")
