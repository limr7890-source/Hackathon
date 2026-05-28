import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier



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
logistic_model.fit(X_train, y_train)

probabilities = logistic_model.predict_proba(X_test)[:, 1]
## m = 300


test_predictions = logistic_model.predict(X_test)

print("\nEvaluation Results for Classifier 1 (Logistic Regression):")
print(classification_report(y_test, test_predictions))





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
