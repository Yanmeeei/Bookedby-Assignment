import os

import pandas as pd
from config import DATASET_PATH, ANALYSIS_OUTPUT_PATH, OUTPUT_PATH


def analysis():
    print('Loading data...')
    df = pd.read_csv(DATASET_PATH)

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    print('Starting analysis...')
    with open(ANALYSIS_OUTPUT_PATH, 'w') as f:

        # Top-selling products by sell amount
        top_products_amt = df.groupby('ProductDescription')['PurchaseAmount'].sum().sort_values(ascending=False)
        f.write("Top 5 Selling Products by Sell Amount:\n")
        f.write(top_products_amt.head(5).to_string())
        f.write("\n\n")

        # Top-selling products by sell count
        top_products_cnt = df.groupby('ProductDescription')['PurchaseID'].count().sort_values(ascending=False)
        f.write("Top 5 Selling Products by Sell Count:\n")
        f.write(top_products_cnt.head(5).to_string())
        f.write("\n\n")

        # Top-selling categories
        top_categories = df.groupby('ProductCategory')['PurchaseAmount'].sum().sort_values(ascending=False)
        f.write("Top 5 Selling Categories:\n")
        f.write(top_categories.head(5).to_string())
        f.write("\n\n")

        # Average spending per customer
        customer_spending = df.groupby('CustomerID')['PurchaseAmount'].sum()
        avg_spending = customer_spending.mean()
        f.write("Average Spending Per Customer: ${:.2f}\n".format(avg_spending))
    print("Analysis complete!")


if __name__ == '__main__':
    analysis()
