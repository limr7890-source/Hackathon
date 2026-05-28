
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



df = pd.read_csv("pu_learning_dataset.csv")

print("Dataset loaded successfully!")
print(f"Total dataset size: {len(df)}")
print(df["label"].value_counts())


#devide the data into training and testing sets
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])


# loading a pre-trained sentence transformer model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

#encoding the text data into embeddings for training and testing sets
X_train = embedder.encode(train_df["text"].tolist(), show_progress_bar=True)
X_test = embedder.encode(test_df["text"].tolist(), show_progress_bar=True)

# extracting the labels for training and testing sets
y_train = train_df["label"].values
y_test = test_df["label"].values





####################### first model; logistic regression #######################
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