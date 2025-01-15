import argparse
import logging
import shutil
import os

from config import DATASET_PATH, PRODUCTS_PATH, DEFAULT_NUM_PRODUCTS, DEFAULT_NUM_CUSTOMERS, \
    DEFAULT_NUM_CLUSTERS, DEFAULT_NUM_CATEGORY, DEFAULT_NUM_PRODUCT

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_data(product_path, num_products, num_customers):
    logging.info("Starting data generation...")
    from dataset_generation.generate_products import generate_products
    from dataset_generation.generator import generate

    if not os.path.isfile(product_path):
        logging.info("Product file not found. Generating products...")
        generate_products(num_products)

    generate(product_path=product_path, num_customers=num_customers)
    logging.info("Data generation completed.")


def perform_data_analysis():
    logging.info("Starting data analysis...")
    from data_analysis import analysis
    analysis()
    logging.info("Data analysis completed.")


def prepare_clustering_data():
    logging.info("Starting data preparation for clustering...")
    from clustering.data_preparation import run as clst_data_preparation
    clst_data_preparation()
    logging.info("Data preparation for clustering completed.")


def perform_elbow_check():
    logging.info("Starting elbow check for clustering...")
    from clustering.elbow_check import run as elbow_check
    elbow_check()
    logging.info("Elbow check completed.")


def perform_k_means_clustering(num_clusters):
    logging.info(f"Starting k-means clustering...")
    from clustering.k_means_cluster import run as k_means_cluster
    k_means_cluster(num_clusters)
    logging.info("K-means clustering completed.")


def perform_density_check():
    logging.info("Checking density of the interaction matrix...")
    from recommendation.density_check import run as density_check
    density_check()
    logging.info("Density check completed.")


def prepare_recommendation_data(method):
    logging.info(f"Preparing recommendation data using method '{method}'...")
    from recommendation.data_preprocess import run as rec_data_preprocessing
    rec_data_preprocessing(method)
    logging.info("Recommendation data preparation completed.")


def perform_content_based_recommendation(cid, num_category, num_product):
    logging.info(f"Getting recommendation for customer {cid}...")
    from recommendation.content_based_filtering import run as content_filtering
    content_filtering(customer_id=cid, top_categories=num_category, top_n=num_product)
    logging.info("Recommendation completed.")


def perform_content_based_recommendation_all():
    logging.info(f"Getting recommendation for all customers...")
    from recommendation.content_based_filtering import run_all as content_filtering_all
    content_filtering_all()
    logging.info("Recommendation completed.")


def clear_all():
    """
    Clear all data, results and intermediate data.
    """
    logging.info("Clearing all data & intermediate results...")
    from config import DATA_PATH, OUTPUT_PATH, RECOMMENDATION_TEMP_PATH, CLUSTER_TEMP_PATH
    paths_to_clear = [
        DATA_PATH,
        OUTPUT_PATH,
        RECOMMENDATION_TEMP_PATH,
        CLUSTER_TEMP_PATH,
    ]

    for path in paths_to_clear:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                path.mkdir(parents=True, exist_ok=True)
                logging.info(f"Cleared: {path}")
            elif path.is_file():
                path.unlink()
        else:
            logging.warning(f"Path does not exist: {path}")


def run_all(overwrite_data):
    """
    Run data generation, clustering, elbow check, k-means clustering, density check and recommendation
    using default config.
    """
    try:
        if not os.path.exists(DATASET_PATH) or not overwrite_data:
            generate_data(PRODUCTS_PATH, DEFAULT_NUM_PRODUCTS, DEFAULT_NUM_CUSTOMERS)
        perform_data_analysis()
        prepare_clustering_data()
        perform_elbow_check()
        perform_k_means_clustering(DEFAULT_NUM_CLUSTERS)
        perform_density_check()
        prepare_recommendation_data("nlp")
        perform_content_based_recommendation("C001", DEFAULT_NUM_CATEGORY, DEFAULT_NUM_PRODUCT)
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)


def main():
    """
    The entry point for this CLI.
    """
    parser = argparse.ArgumentParser(description="Yanmei's Recommendation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    run_all_parser = subparsers.add_parser("run-all",
                                           help="Run data generation, data analysis, k means clustering and recommendation using default configuration")
    run_all_parser.add_argument("-d", "--overwrite-data", help="Overwrite existing data", action="store_false")
    clear_all_parser = subparsers.add_parser("clear-all", help="Clear all data & results")

    # Subcommand: generate_data
    generate_parser = subparsers.add_parser("generate", help="Generate synthetic data")
    generate_parser.add_argument("-p", "--product_path", type=str, default=PRODUCTS_PATH,
                                 help=f"Path to the products list CSV (default={PRODUCTS_PATH})")
    generate_parser.add_argument("-np", "--num_products", type=int, default=DEFAULT_NUM_PRODUCTS,
                                 help=f"Number of products to generate (default={DEFAULT_NUM_PRODUCTS})")
    generate_parser.add_argument("-nc", "--num_customers", type=int, default=DEFAULT_NUM_CUSTOMERS,
                                 help=f"Number of customers to generate (default={DEFAULT_NUM_CUSTOMERS})")

    # Subcommand: data_analysis
    generate_parser = subparsers.add_parser("analyze", help="Perform data analysis")

    # Subcommand: clustering
    clustering_parser = subparsers.add_parser("clustering", help="Clustering-related commands")
    clustering_subparsers = clustering_parser.add_subparsers(dest="clustering_command", help="Clustering subcommands")
    prepare_data_parser = clustering_subparsers.add_parser("prepare", help="Prepare data for clustering")
    elbow_check_parser = clustering_subparsers.add_parser("elbow-method",
                                                          help="Perform Elbow check for suitable number of clusters")
    k_means_cluster_parser = clustering_subparsers.add_parser("kmeans", help="Perform K-means clustering")
    k_means_cluster_parser.add_argument("-c", "--num_clusters", type=int, default=DEFAULT_NUM_CLUSTERS,
                                        help=f"Number of clusters (default={DEFAULT_NUM_CLUSTERS})")

    # Subcommand: Recommendation
    recommendation_parser = subparsers.add_parser("recommendation", help="Recommendation-related commands")
    recommendation_subparser = recommendation_parser.add_subparsers(dest="recommendation_command",
                                                                    description="Recommendation subcommands")
    density_check_parser = recommendation_subparser.add_parser("check-density",
                                                               help="Perform density check for the interaction matrix")
    prepare_data_parser = recommendation_subparser.add_parser("prepare", help="Prepare data for recommendation")
    prepare_data_parser.add_argument(
        "-m", "--method", type=str, choices=["nlp", "pairwise"], required=True,
        help="Choose the data preparation method: 'nlp' (recommended for more relavent results) or 'pairwise'."
    )
    content_based_filtering_parser = recommendation_subparser.add_parser("content-filter",
                                                                         help="Get recommendations using content based filtering")
    content_based_filtering_parser.add_argument("-cid", "--customer_id", required=True, type=str,
                                                help="Customer ID (format: C001~C500 (or max number of customers) for existing customers, C000 for new customers)")
    content_based_filtering_parser.add_argument("-nc", "--num_category", type=int, default=DEFAULT_NUM_CATEGORY,
                                                help=f"number of categories to recommend (default={DEFAULT_NUM_CATEGORY})")
    content_based_filtering_parser.add_argument("-np", "--num_product", type=int, default=DEFAULT_NUM_PRODUCT,
                                                help=f"Number of recommended products in each category (default={DEFAULT_NUM_PRODUCT})")

    content_based_filtering_all_parser = recommendation_subparser.add_parser("content-filter-all", help="Get recommendations for all customers")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    elif args.command == "run-all":
        run_all(args.overwrite_data)
    elif args.command == "clear-all":
        clear_all()
    elif args.command == "generate":
        generate_data(args.product_path, args.num_products, args.num_customers)
    elif args.command == "analyze":
        perform_data_analysis()
    elif args.command == "clustering":
        if args.clustering_command == "prepare":
            prepare_clustering_data()
        elif args.clustering_command == "elbow-method":
            perform_elbow_check()
        elif args.clustering_command == "kmeans":
            perform_k_means_clustering(args.num_clusters)
        else:
            clustering_parser.print_help()
    elif args.command == "recommendation":
        if args.recommendation_command == "check-density":
            perform_density_check()
        elif args.recommendation_command == "prepare":
            prepare_recommendation_data(args.method)
        elif args.recommendation_command == "content-filter":
            perform_content_based_recommendation(args.customer_id, args.num_category, args.num_product)
        elif args.recommendation_command == "content-filter-all":
            perform_content_based_recommendation_all()
        else:
            recommendation_parser.print_help()


if __name__ == "__main__":
    main()
