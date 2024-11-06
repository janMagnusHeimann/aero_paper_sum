import torch
import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

# Load dataset and model
df = pd.read_csv('data/cleaned_processed_papers.csv')
tokenizer = BertTokenizer.from_pretrained('bert_classification_model')
model = BertModel.from_pretrained('bert_classification_model')
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# Helper function to get embeddings
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True,
                       padding='max_length', max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
    return embedding


# Generate embeddings for all documents
print("Generating embeddings for category clustering...")
embeddings = np.vstack([get_embedding(text) for text in df['full_text']])

# Number of clusters based on unique labels
num_clusters = df['labels'].nunique()

# Check if we have more than one cluster
if num_clusters > 1:
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(embeddings)

    # Check for unique clusters in the result
    unique_clusters = len(set(clusters))
    if unique_clusters > 1:
        # Calculate silhouette score
        silhouette_avg = silhouette_score(embeddings, clusters)
        print(f"Silhouette Score [Category Clustering]: {silhouette_avg:.4f}")
    else:
        print("Silhouette Score cannot be computed") + (
            "because only one unique cluster was found.")
else:
    print("Clustering evaluation skipped due to") + (
        "insufficient unique labels in the dataset.")