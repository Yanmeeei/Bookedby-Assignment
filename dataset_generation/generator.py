import os

import pandas as pd
import random
from faker import Faker
from datetime import date

from config import DATASET_PATH, PRODUCTS_PATH, DATA_PATH
from dataset_generation.generate_products import price_ranges


def generate(product_path=PRODUCTS_PATH, num_customers: int = 500, num_entries: int = 5000):
    """
    Generates synthetic data for this project.
    """
    # Generate customer and product IDs
    cid_list = [f"C{str(i).zfill(len(str(num_customers)))}" for i in range(1, num_customers + 1)]
    products_df = pd.read_csv(product_path)
    pid_list = products_df["ProductID"].tolist()
    pid_to_category = dict(zip(products_df["ProductID"], products_df["ProductCategory"]))
    pid_to_description = dict(zip(products_df["ProductID"], products_df["ProductDescription"]))

    # Generate purchase records
    data = []
    fake = Faker()  # for generating datetime
    for purchase_id in range(1, num_entries + 1):
        cid = random.choice(cid_list)
        pid = random.choice(pid_list)
        description = pid_to_description[pid]
        category = pid_to_category[pid]

        purchase_amount = round(random.uniform(*price_ranges[category]), 2)
        if random.random() < 0.3:  # 30% chance for holiday shopping peak
            purchase_date = fake.date_between(start_date=date(2024, 11, 1), end_date=date(2024, 12, 31))
        else:
            purchase_date = fake.date_between(start_date=date.today().replace(year=date.today().year - 1),
                                              end_date=date.today())
        if random.random() < 0.01:
            purchase_amount *= 5  # 1% chance for big buyers

        data.append({
            "PurchaseID": f"PU{str(purchase_id).zfill(5)}",
            "CustomerID": cid,
            "ProductID": pid,
            "ProductDescription": description,
            "ProductCategory": category,
            "PurchaseAmount": purchase_amount,
            "PurchaseDate": purchase_date
        })

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    df = pd.DataFrame(data)
    df.to_csv(DATASET_PATH, index=False)
    print(f"Dataset with {num_entries} entries saved to {DATASET_PATH}")


if __name__ == "__main__":
    generate()