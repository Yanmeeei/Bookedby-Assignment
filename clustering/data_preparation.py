import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

from config import DATASET_PATH, CLUSTER_TEMP_PATH


def feature_scaling(df):
    """
    Prepare and aggregate customer data for clustering by extracting relevant features.
    """

    # Generate features per customer (simple RFM features)
    df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'])
    customer_data = df.groupby('CustomerID').agg(
        TotalSpending=('PurchaseAmount', 'sum'),
        PurchaseFrequency=('PurchaseID', 'count'),
        LastPurchase=('PurchaseDate', 'max')
    ).reset_index()

    # Calculate recency.
    # Baseline is the latest datetime in the PurchaseDate records
    customer_data['Recency'] = (df['PurchaseDate'].max() - customer_data['LastPurchase']).dt.days

    # Feature scaling to numerical columns using StandardScaler
    numerical_columns = ['TotalSpending', 'PurchaseFrequency', 'Recency']  # RFM features
    scaler = StandardScaler()
    customer_data[numerical_columns] = scaler.fit_transform(customer_data[numerical_columns])

    return customer_data


def run():
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Dataset file not found at {DATASET_PATH}.") from e

    if not os.path.exists(CLUSTER_TEMP_PATH):
        os.makedirs(CLUSTER_TEMP_PATH)

    prepared_data = feature_scaling(df)
    prepared_data.to_csv(CLUSTER_TEMP_PATH / "scaled_features.csv", index=False)

    print("Data preparation done!")


if __name__ == '__main__':
    run()
