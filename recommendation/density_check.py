import pandas as pd
import numpy as np

from config import DATASET_PATH


def calculate_matrix_density(data):
    """
    Calculate the density of interaction matrix to determine the proper method for recommendation.
    """
    # CustomerID x ProductID
    interaction_matrix = data.pivot_table(
        index='CustomerID',
        columns='ProductID',
        values='PurchaseAmount',
        fill_value=0
    )

    # Matrix density = #nonzero-entries / #all-entries
    cnt_all = interaction_matrix.size
    cnt_nonzero = np.count_nonzero(interaction_matrix)
    density = cnt_nonzero / cnt_all

    # print(f"Matrix Shape: {interaction_matrix.shape}")
    print(f"Matrix Density: {density:.4f}")
    return density


def run():
    data = pd.read_csv(DATASET_PATH)
    density = calculate_matrix_density(data)
    if density > 0.5:
        print("The interaction matrix is dense.")
    elif density < 0.1:
        print("The interaction matrix is sparse.")
    else:
        print("The interaction matrix is moderately dense.")


if __name__ == '__main__':
    run()