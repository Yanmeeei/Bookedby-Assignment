import os

import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
import matplotlib.pyplot as plt
import numpy as np

from config import CLUSTER_OUTPUT_PATH, CLUSTER_TEMP_PATH


def kmeans(prepared_data, n_clusters: int = 5):
    """
    Perform k-means clustering on the given dataset.
    Calculate the silhouette score, creates a silhouette plot and an interactive 3D scatter plot.
    """

    features = ['TotalSpending', 'PurchaseFrequency', 'Recency']  # Use RFM features
    data = prepared_data[features]

    # Apply k-means cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    prepared_data['Cluster'] = kmeans.fit_predict(data)
    centroids = pd.DataFrame(kmeans.cluster_centers_, columns=features)

    with open(CLUSTER_OUTPUT_PATH / 'cluster_centroids.csv', 'w') as f:
        f.write(str(centroids))
    print(">>> Cluster centroids saved at " + str(CLUSTER_OUTPUT_PATH / 'cluster_centroids.csv'))
    visualization_3d(prepared_data, features, centroids)

    # Compute silhouette score for validation
    score = silhouette_score(data, prepared_data['Cluster'])
    plot_silhouette(data.values, prepared_data['Cluster'].values, n_clusters)

    return prepared_data, score


def visualization_3d(data, features, centroids=None):
    """
    Create an interactive 3D scatter plot for cluster visualization.
    """

    fig = px.scatter_3d(
        data,
        x=features[0],  # TotalSpending
        y=features[1],  # PurchaseFrequency
        z=features[2],  # Recency
        color='Cluster',
        title="Interactive 3D Cluster Visualization",
        labels={
            features[0]: features[0],
            features[1]: features[1],
            features[2]: features[2]
        },
        opacity=0.7
    )

    if centroids is not None:
        fig.add_scatter3d(
            x=centroids[features[0]],  # TotalSpending
            y=centroids[features[1]],  # PurchaseFrequency
            z=centroids[features[2]],  # Recency
            mode='markers',
            marker=dict(size=5, color='red', symbol='x'),
            name='Centroid',
            customdata=centroids,
            hovertemplate=(
                f"{features[0]}: %{{x}}<br>"
                f"{features[1]}: %{{y}}<br>"
                f"{features[2]}: %{{z}}<br>"
                "<extra></extra>"
            )
        )

    output_file = CLUSTER_OUTPUT_PATH / 'k_means_visualization.html'
    fig.write_html(output_file)
    print(">>> Interactive 3D scatter plot saved at " + str(output_file))


def plot_silhouette(prepared_data, labels, n_clusters):
    """
    Plot silhouette scores to evaluate cluster quality.
    Higher scores indicate better clusters.
    """

    silhouette_values = silhouette_samples(prepared_data, labels)

    plt.figure(figsize=(10, 6))
    y_lower = 10
    for i in range(n_clusters):
        ith_cluster_values = silhouette_values[labels == i]
        ith_cluster_values.sort()
        size_cluster_i = len(ith_cluster_values)
        y_upper = y_lower + size_cluster_i

        plt.fill_betweenx(
            np.arange(y_lower, y_upper),
            0, ith_cluster_values,
            alpha=0.7, label=f'Cluster {i}'
        )

        # A gap between clusters
        y_lower = y_upper + 10

    plt.axvline(x=np.mean(silhouette_values), color="red", linestyle="--", label="Average Silhouette Score")
    plt.title("Silhouette Plot")
    plt.xlabel("Silhouette Coefficient")
    plt.ylabel("Cluster Samples")
    plt.legend()
    plt.savefig(CLUSTER_OUTPUT_PATH / 'silhouette_score.png')
    print(">>> Silhouette plot saved at " + str(CLUSTER_OUTPUT_PATH / 'silhouette_score.png'))


def run(n_clusters=5):
    try:
        prepared_data = pd.read_csv(CLUSTER_TEMP_PATH / 'scaled_features.csv')
    except FileNotFoundError:
        print("Error: 'scaled_features.csv' not found. Please complete data preparation.")
        return
    print("Successfully loaded data. Beginning k-means clustering.")

    if not os.path.exists(CLUSTER_OUTPUT_PATH):
        os.makedirs(CLUSTER_OUTPUT_PATH)

    # Apply k-means clustering
    clustered_data, score = kmeans(prepared_data, n_clusters=n_clusters)
    clustered_data.to_csv(CLUSTER_OUTPUT_PATH / "clustered_data.csv", index=False)
    print(f">>> Clustered data saved at {CLUSTER_OUTPUT_PATH}/clustered_data.csv")

    print("K-means clustering finished.")
    print(f"Silhouette Score for {n_clusters} clusters: {score:.4f}")


if __name__ == '__main__':
    run()
