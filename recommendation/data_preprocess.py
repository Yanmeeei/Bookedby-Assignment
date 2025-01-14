import os

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pandas as pd
import pickle

from config import RECOMMENDATION_TEMP_PATH, PRODUCTS_PATH


def data_process_nlp(data: pd.DataFrame):
    """
    Computes cosine similarity using pretrained models in Sentence Transformers.
    """

    # Combine ProductCategory and ProductDescription for better similarity analysis
    data['CombinedMetadata'] = (
            data['ProductCategory'].str.strip().str.lower() + " " +
            data['ProductDescription'].fillna("").str.strip().str.lower()
    )

    model = SentenceTransformer('all-MiniLM-L6-v2')  # Load a lightweight model since dataset is small

    print("Generating embeddings for product metadata...")
    embeddings = model.encode(data['CombinedMetadata'].tolist(), show_progress_bar=True)

    print("Computing similarity matrix...")
    similarity_matrix = cosine_similarity(embeddings)

    # Map ProductID to index in the similarity matrix
    pid_to_smid = pd.Series(data.index, index=data['ProductID'])

    return similarity_matrix, pid_to_smid, data


def data_process_pairwise(data: pd.DataFrame):
    """
    Please use the NLP version data processing instead, for better recommendation performance.

    Precomputes cosine similarity using pairwise distances.
    """
    # Combine ProductCategory and ProductDescription for better similarity analysis
    data['CombinedMetadata'] = (
            data['ProductCategory'].str.strip().str.lower() + " " +
            data['ProductDescription'].fillna("").str.strip().str.lower()
    )

    # Compute cosine similarity between products
    vectorizer = CountVectorizer(max_features=1000)
    metadata_matrix = vectorizer.fit_transform(data['CombinedMetadata'])
    similarity_matrix = cosine_similarity(metadata_matrix, metadata_matrix)

    # Map pid to index in the similarity matrix
    pid_to_smid = pd.Series(data.index, index=data['ProductID'])
    return similarity_matrix, pid_to_smid, data


def run(method='nlp'):

    if method not in ['nlp', 'pairwise']:
        print("Invalid data processing method argument. Valid methods are 'nlp' and 'pairwise'")
        return

    if not os.path.exists(RECOMMENDATION_TEMP_PATH):
        os.makedirs(RECOMMENDATION_TEMP_PATH)

    # Data preprocessing
    data = pd.read_csv(PRODUCTS_PATH)
    if method == 'nlp':
        similarity_matrix, pid_to_smid, product_data = data_process_nlp(data)
    else:
        similarity_matrix, pid_to_smid, product_data = data_process_pairwise(data)

    # Save results
    print("Saving results...")
    with open(RECOMMENDATION_TEMP_PATH / "similarity_matrix.pkl", "wb") as f:
        pickle.dump(similarity_matrix, f)
    with open(RECOMMENDATION_TEMP_PATH / "pid_to_smid.pkl", "wb") as f:
        pickle.dump(pid_to_smid, f)
    product_data.to_csv(RECOMMENDATION_TEMP_PATH / "product_metadata.csv", index=False)

    # print(f"Product metadata shape: {product_data.shape}")
    # print(f"Similarity matrix shape: {similarity_matrix.shape}")
    print("Precomputed similarity matrix, pid to smid dict, and product metadata saved.")


if __name__ == "__main__":
    run()
