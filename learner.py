
import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier

import torch
import numpy as np
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import evaluate

from sklearn.metrics import f1_score

import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# =========================================================================
# 1. Loading your real positive posts (what the team collected)
# =========================================================================
print("Loading and computing vectors for the positive posts from the campaign...")
positive_texts = [
    "Check out our new running shoes! Lightweight and durable #JustDoIt",
    "Run faster, push harder. The new collection is live now #JustDoIt",
    "Unboxing the new gym gear. Absolutely loving the design and comfort! #JustDoIt"
    # ... paste the full list brought by the team here
]

embedder = SentenceTransformer("all-MiniLM-L6-v2")
positive_embeddings = embedder.encode(positive_texts) # Fast computation for a small amount
num_positives = len(positive_texts)

# Computing the final campaign center
campaign_center = np.mean(positive_embeddings, axis=0).reshape(1, -1)

# =========================================================================
# 2. Loading the huge negative dataset from the Pickle file
# =========================================================================
print("Loading the negative dataset from the Pickle file...")
with open("instagram_negatives_cache.pkl", "rb") as f:
    cache_data = pickle.load(f)

all_negative_texts = cache_data["texts"]
all_negative_embeddings = cache_data["embeddings"]

# =========================================================================
# 3. Live, fast semantic filtering to find hard and easy negatives for the specific campaign
# =========================================================================
print("Computing distances and separating into hard and easy...")
similarities = cosine_similarity(all_negative_embeddings, campaign_center).flatten()

easy_neg_indices = []
hard_neg_indices = []

for idx, sim in enumerate(similarities):
    if sim < 0.2:
        easy_neg_indices.append(idx)
    elif 0.2 <= sim < 0.45:
        hard_neg_indices.append(idx)

# =========================================================================
# 4. The Magic: Smart and balanced sampling (max 2x negatives relative to positives)
# =========================================================================
# Let's assume we want a 1:2 ratio. That means the total amount of negatives will be exactly double the positives.
# We will split it half-and-half: part hard negatives (to challenge the model) and part easy ones (for background noise).
max_negatives_per_type = num_positives  # Taking an equal amount of hard and easy ones

# Actual sampling from the indices (taking the first ones, or randomly)
selected_hard_idx = hard_neg_indices[:max_negatives_per_type]
selected_easy_idx = easy_neg_indices[:max_negatives_per_type]
final_neg_indices = selected_hard_idx + selected_easy_idx

# Extracting the filtered and balanced texts and vectors
sampled_negative_texts = [all_negative_texts[i] for i in final_neg_indices]
sampled_negative_embeddings = all_negative_embeddings[final_neg_indices]

print(f"Class balancing completed successfully:")
print(f"   - Good examples (positives): {num_positives}")
print(f"   - Bad examples (hard negatives): {len(selected_hard_idx)}")
print(f"   - Bad examples (easy negatives): {len(selected_easy_idx)}")
print(f"   - Total negative examples: {len(sampled_negative_texts)} (ratio of 1:{len(sampled_negative_texts)/num_positives:.1f})")

# =========================================================================
# 5. Merging arrays and splitting into Train/Test (exactly as your models expect)
# =========================================================================
X = np.vstack([positive_embeddings, sampled_negative_embeddings])
y = np.array([1] * num_positives + [0] * len(sampled_negative_texts))
all_texts = positive_texts + sampled_negative_texts

indices = np.arange(len(X))
train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42, stratify=y)

X_train = X[train_idx]
X_test = X[test_idx]
y_train = y[train_idx]
y_test = y[test_idx]

train_df = pd.DataFrame({'text': [all_texts[i] for i in train_idx], 'label': y_train})
test_df = pd.DataFrame({'text': [all_texts[i] for i in test_idx], 'label': y_test})

print(f"\nTraining arrays are ready for your models! Train size: {len(X_train)}, Test size: {len(X_test)}")



# =========================================================================
# Logistic Regression 
# =========================================================================
# training a logistic regression model on the training data
logistic_model = LogisticRegression(max_iter=1000)
result = logistic_model.fit(X_train, y_train)

probabilities = logistic_model.predict_proba(X_test)[:, 1]
## m = 300


test_predictions = logistic_model.predict(X_test)

print("\nEvaluation Results for Classifier 1 (Logistic Regression):")
print(classification_report(y_test, test_predictions))

#print("Intercept:", logistic_model.intercept_)
#print("Coefficients:", logistic_model.coef_)




# ==========================================
# Train and Evaluate Classifier 2 (KNN)
# ==========================================
print("\nTraining Classifier 2 (KNN with Cosine Distance)...")

# Setting n_neighbors=5 (looks at the 5 closest posts)
# Using 'cosine' metric for high-dimensional text embeddings
classifier2 = KNeighborsClassifier(n_neighbors=5, metric='cosine')
classifier2.fit(X_train, y_train)

# Predict classes for the test set
test_predictions_knn = classifier2.predict(X_test)

# Predict probabilities
# For KNN, probability is calculated as the fraction of neighbors with the same label
test_probabilities_knn = classifier2.predict_proba(X_test)[:, 1]

print("\nEvaluation Results for Classifier 2 (KNN):")
print(classification_report(y_test, test_predictions_knn))




# ==========================================
# BERT Fine-Tuning Setup
# ==========================================

print("\nStarting Classifier 3 (BERT Fine-tuning) setup...")

# 1. Convert our Pandas DataFrames into Hugging Face Datasets
train_dataset = Dataset.from_pandas(train_df[['text', 'label']].reset_index(drop=True))
test_dataset = Dataset.from_pandas(test_df[['text', 'label']].reset_index(drop=True))


# 2. Load the Tokenizer for DistilBERT
model_name = "distilbert-base-uncased"
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
    num_train_epochs=3,
    weight_decay=0.01,
    evaluation_strategy="epoch",
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
print("\nTraining Classifier 3 (BERT)... This might take a few minutes.")
trainer.train()

# 10. Final Evaluation
print("\nFinal Evaluation Results for Classifier 3 (BERT):")
eval_results = trainer.evaluate()
print(eval_results)

predictions_output = trainer.predict(tokenized_test)
bert_predictions = np.argmax(predictions_output.predictions, axis=-1)
print(classification_report(y_test, bert_predictions))


