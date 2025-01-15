import os.path

import pandas as pd
import pickle
from collections import Counter
from config import DATASET_PATH, PRODUCTS_PATH, RECOMMENDATION_TEMP_PATH, REC_OUTPUT_PATH


def recommend(data, similarity_matrix, pid_to_sm_row, product_metadata, cid, top_c=2, top_n=2):
    """
    Get product recommendations for a specific customer using a similarity matrix.
    """
    # Get the customer's purchase history
    customer_data = data[data['CustomerID'] == cid]
    purchased_products = customer_data['ProductID'].unique()
    purchased_categories = customer_data['ProductCategory']

    # Get the top {top_categories} categories purchased most by the customer
    category_purchase_cnt = Counter(purchased_categories)
    top_categories = [cat for cat, _ in category_purchase_cnt.most_common(top_c)]

    # For each of the top categories, find recommendations and their similarity score.
    recommendations = {}
    for c in top_categories:
        for pid in purchased_products:
            for idx, score in sorted(enumerate(similarity_matrix[pid_to_sm_row[pid]]), key=lambda x: x[1], reverse=True):
                similar_product = product_metadata.iloc[idx]['ProductID']
                similar_category = product_metadata.iloc[idx]['ProductCategory']
                if (
                    # The recommendations should not be purchased before
                    similar_product not in purchased_products and
                    similar_category == c
                ):
                    recommendations[similar_product] = recommendations.get(similar_product, 0) + score

    # Sort recommendations by score and select top_n per category
    pid_to_category = dict(zip(product_metadata["ProductID"], product_metadata["ProductCategory"]))
    familiar_recommendations = []
    for c in top_categories:
        category_recommendations = []
        for pid, score in recommendations.items():
            if pid_to_category[pid] == c:
                category_recommendations.append((pid, score))
        top_category_recommendations = sorted(category_recommendations, key=lambda x: x[1], reverse=True)[:top_n]
        familiar_recommendations.extend([rec[0] for rec in top_category_recommendations])

    # Add one product from the most unfamiliar category (unvisited or least bought)
    # That is the most similar to previously purchased products
    unfamiliar_categories = set(product_metadata['ProductCategory']) - set(purchased_categories)
    if not unfamiliar_categories:
        unfamiliar_categories = set(sorted(category_purchase_cnt, key=category_purchase_cnt.get)[:3])
    potential_novel_products = product_metadata[
        product_metadata['ProductCategory'].isin(unfamiliar_categories)
    ]
    best_match = None
    best_score = -1
    for pid in purchased_products:
        for idx, score in sorted(enumerate(similarity_matrix[pid_to_sm_row[pid]]), key=lambda x: x[1], reverse=True):
            similar_product = product_metadata.iloc[idx]['ProductID']
            # If the similar product is eligible for recommendation, compare with current best match.
            if (
                    similar_product not in purchased_products and
                    similar_product in potential_novel_products['ProductID'].values
            ):
                if score > best_score:
                    best_match = similar_product
                    best_score = score

    return purchased_products, familiar_recommendations, best_match


def print_products(products, pid_to_description, pid_to_category, num_products=None, title=None):
    """
    Prints products grouped by their categories to the console.
    """
    if title:
        print(f"\n{title}")

    prod_dict = {}
    for pid in products:
        cat = pid_to_category[pid]
        if cat not in prod_dict:
            prod_dict[cat] = []
        prod_dict[cat].append(pid)

    for cat, pids in prod_dict.items():
        print(f"\t{cat}")
        for pid in pids[:num_products] if num_products else pids:
            print(f"\t\t{pid_to_description[pid]}")


def load_files():
    """
    Loads necessary files.
    """
    if (
            not os.path.exists(RECOMMENDATION_TEMP_PATH / "similarity_matrix.pkl") or
            not os.path.exists(RECOMMENDATION_TEMP_PATH / "pid_to_smid.pkl")
    ):
        raise FileNotFoundError("Cannot find preprocessed data")
    with open(RECOMMENDATION_TEMP_PATH / "similarity_matrix.pkl", "rb") as f:
        similarity_matrix = pickle.load(f)
    with open(RECOMMENDATION_TEMP_PATH / "pid_to_smid.pkl", "rb") as f:
        pid_to_smid = pickle.load(f)
    product_metadata = pd.read_csv(RECOMMENDATION_TEMP_PATH / "product_metadata.csv")

    try:
        products_df = pd.read_csv(PRODUCTS_PATH)
    except FileNotFoundError:
        print("Cannot find product data")
        return

    return similarity_matrix, pid_to_smid, product_metadata, products_df


def run(customer_id, top_categories=2, top_n=3):
    """
    Generate recommendations for a specified customer.
    """
    data = pd.read_csv(DATASET_PATH)

    # Get recommendations (top-seller products) for new customers
    if customer_id not in data["CustomerID"].unique():
        print("Welcome, new customer. Recommending most purchased products:")
        top_products = (data.groupby('ProductDescription')['PurchaseID']
                        .count()
                        .reset_index()  # Convert series to DataFrame
                        .rename(
            columns={'ProductDescription': 'Top Seller Product', 'PurchaseID': 'TransactionCount'}))
        top_products = top_products.sort_values(by='TransactionCount', ascending=False)
        print(top_products.head(5).to_string(index=False))
        return

    try:
        similarity_matrix, pid_to_smid, product_metadata, products_df = load_files()
    except FileNotFoundError as e:
        print(e)
        return
    pid_to_description = dict(zip(products_df["ProductID"], products_df["ProductDescription"]))

    purchased_products, familiar_recommendations, best_match = \
        recommend(data, similarity_matrix, pid_to_smid, product_metadata, customer_id, top_c=top_categories, top_n=top_n)

    # Print results to the console
    pid_to_category = dict(zip(products_df["ProductID"], products_df["ProductCategory"]))
    print_products(  # Print purchase history
        purchased_products,
        pid_to_description,
        pid_to_category,
        title=f"Customer {customer_id}'s purchase history:"
    )
    print_products(  # Print familiar recommendations
        familiar_recommendations,
        pid_to_description,
        pid_to_category,
        num_products=top_n,
        title="Recommendations (familiar):"
    )
    print_products(  # Print novel recommendation
        [best_match],
        pid_to_description,
        pid_to_category,
        num_products=top_n,
        title="Recommendations (novel):"
    )

    if not os.path.exists(REC_OUTPUT_PATH):
        os.makedirs(REC_OUTPUT_PATH)
    with open(REC_OUTPUT_PATH / f"{customer_id}.csv", "w") as f:
        f.write("CustomerID,RecID01,RecDesc01,RecID02,RecDesc02,RecID03,RecDesc03,UnfamRecID01,UnfamRecDesc01\n")
        f.write(f"{customer_id},")
        for r in familiar_recommendations:
            f.write(f"{r},{pid_to_description[r]},")
        f.write(f"{best_match},{pid_to_description[best_match]}")
    print("Recommendations done! Results are saved at ", REC_OUTPUT_PATH)


def run_all(top_categories=2, top_n=3):
    """
    Generate recommendations for all customers.
    """
    data = pd.read_csv(DATASET_PATH)
    try:
        similarity_matrix, pid_to_smid, product_metadata, products_df = load_files()
    except FileNotFoundError as e:
        print(e)
        return
    pid_to_description = dict(zip(products_df["ProductID"], products_df["ProductDescription"]))

    if not os.path.exists(REC_OUTPUT_PATH):
        os.makedirs(REC_OUTPUT_PATH)

    with (open(REC_OUTPUT_PATH / f"all.csv", "w") as f):
        # Write CSV header
        f.write("CustomerID,")
        for i in range(top_categories * top_n):
            f.write(f"RecID{i},RecDesc{i},")
        f.write("NovelRecID,NovelRecDesc\n")

        for cid in sorted(data["CustomerID"].unique()):
            purchased_products, familiar_recommendations, best_match = \
                recommend(data, similarity_matrix, pid_to_smid, product_metadata, cid, top_c=top_categories, top_n=top_n)
            f.write(f"{cid},")
            for r in familiar_recommendations:
                f.write(f"{r},{pid_to_description[r]},")
            f.write(f"{best_match},{pid_to_description[best_match]}")
            f.write("\n")

    print("Recommendations done! Results are saved at ", REC_OUTPUT_PATH)


if __name__ == "__main__":
    # run_all()
    run("C001")
