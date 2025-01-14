import os

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans

from config import CLUSTER_OUTPUT_PATH, CLUSTER_TEMP_PATH


def elbow_method(data):
    """
    Compute and visualize teh distortion at different num_clusters.
    """
    # Calculate the distortion for 1-9 clusters
    distortions = []
    for k in range(1, 10):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(data[['TotalSpending', 'PurchaseFrequency', 'Recency']])  # RFM features
        distortions.append(kmeans.inertia_)

    # Plot the results
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, 10), distortions, marker='o')
    plt.title('Distortions for different numbers of clusters')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Distortion (Inertia)')
    plt.savefig(CLUSTER_OUTPUT_PATH / 'elbow_plot_kmeans.png')


def run():
    try:
        data = pd.read_csv(CLUSTER_TEMP_PATH / 'scaled_features.csv')
    except FileNotFoundError:
        print('Please complete data preparation for clustering.')
        return

    if not os.path.exists(CLUSTER_OUTPUT_PATH):
        os.makedirs(CLUSTER_OUTPUT_PATH)

    elbow_method(data)
    print('>>> Elbow plot saved at ' + str(CLUSTER_OUTPUT_PATH / 'elbow_plot_kmeans.png'))


if __name__ == '__main__':
    run()
