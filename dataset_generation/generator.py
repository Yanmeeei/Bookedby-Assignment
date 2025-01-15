import os

import pandas as pd
import random
from faker import Faker
from datetime import date

from config import DATASET_PATH, PRODUCTS_PATH, DATA_PATH
from dataset_generation.generate_products import price_ranges


def generate(
        product_path=PRODUCTS_PATH,
        num_customers= 500,
        num_entries=7000,  # for generating > 5000 entries
        high_spender_ratio=0.1,
        occasional_ratio=0.3,
        lost_ratio=0.1
):
    """
    Generates synthetic data for this project with high-spenders, occasional customers, and lost customers.
    """
    # Generate customer and product IDs
    cid_list = [f"C{str(i).zfill(len(str(num_customers)))}" for i in range(1, num_customers + 1)]
    high_spenders = random.sample(cid_list, int(num_customers * high_spender_ratio))
    occasional_customers = random.sample(
        [cid for cid in cid_list if cid not in high_spenders],
        int(num_customers * occasional_ratio)
    )
    lost_customers = random.sample(cid_list, int(num_customers * lost_ratio))

    products_df = pd.read_csv(product_path)
    pid_list = products_df["ProductID"].tolist()
    pid_to_category = dict(zip(products_df["ProductID"], products_df["ProductCategory"]))
    pid_to_description = dict(zip(products_df["ProductID"], products_df["ProductDescription"]))

    # Purchase records
    data = []
    fake = Faker()
    for purchase_id in range(1, num_entries + 1):
        cid = random.choice(cid_list)
        pid = random.choice(pid_list)
        description = pid_to_description[pid]
        category = pid_to_category[pid]
        # Adjust behavior based on customer type
        if cid in high_spenders:
            purchase_amount = round(random.uniform(*price_ranges[category]) * 2, 2)  # Higher spending
        elif cid in occasional_customers:
            purchase_amount = round(random.uniform(*price_ranges[category]), 2)
            if random.random() > 0.2:
                continue  # Skip adding this purchase for occasional customers
        else:
            purchase_amount = round(random.uniform(*price_ranges[category]), 2)

        # Assign purchase date
        if random.random() < 0.30:  # Holiday peak
            purchase_date = fake.date_between(start_date=date(2024, 11, 1), end_date=date(2024, 12, 31))
        else:
            purchase_date = fake.date_between(start_date=date(2024, 1, 1), end_date=date(2024, 10, 31))

        if cid in lost_customers:
            purchase_date = fake.date_between(start_date=date(2024, 1, 1), end_date=date(2024, 10, 31))

        data.append({
            "PurchaseID": f"PU{str(purchase_id).zfill(5)}",
            "CustomerID": cid,
            "ProductID": pid,
            "ProductDescription": description,
            "ProductCategory": category,
            "PurchaseAmount": purchase_amount,
            "PurchaseDate": purchase_date
        })

    # Save dataset
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    df = pd.DataFrame(data)
    df.to_csv(DATASET_PATH, index=False)
    print(f"Dataset with {df.shape[0]} entries saved to {DATASET_PATH}")


if __name__ == "__main__":
    generate()