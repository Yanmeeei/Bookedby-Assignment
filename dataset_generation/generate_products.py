import os.path

import pandas as pd

from config import PRODUCTS_PATH, DATA_PATH

# Define categories with their products
# Currently this includes 120 products.
categories = {
    "Clothing & Apparel": [
        "Men's T-Shirt", "Women's Jacket", "Jeans", "Formal Shoes", "Casual Sneakers", "Running Shorts",
        "Winter Coat", "Polo Shirt", "Swimwear", "Baseball Cap", "Athletic Socks", "Sports Bra",
        "Raincoat", "Joggers", "Summer Dress"
    ],
    "Tech & Electronics": [
        "Smartphone", "Laptop", "Tablet", "Smartwatch", "Wireless Headphones", "Bluetooth Speaker",
        "Gaming Console", "4K TV", "Streaming Stick", "Digital Camera", "E-Reader", "VR Headset",
        "Home Security Camera", "Portable Power Bank", "Desktop Computer"
    ],
    "Home & Furniture": [
        "Office Chair", "Standing Desk", "Bookshelf", "Dining Table", "Bedside Table", "Sofa",
        "Coffee Table", "Recliner Chair", "Patio Set", "Bar Stool", "Wardrobe", "Storage Ottoman",
        "Wall Shelf", "Bed Frame", "Accent Chair"
    ],
    "Kitchen & Appliances": [
        "Blender", "Microwave Oven", "Air Fryer", "Electric Kettle", "Cookware Set", "Toaster",
        "Espresso Machine", "Food Processor", "Rice Cooker", "Ice Cream Maker", "Slow Cooker",
        "Juicer", "Electric Grill", "Dish Rack", "Knife Set"
    ],
    "Fitness & Sports": [
        "Tennis Racket", "Yoga Mat", "Dumbbell Set", "Treadmill", "Resistance Bands", "Boxing Gloves",
        "Exercise Bike", "Skipping Rope", "Hiking Boots", "Fitness Tracker", "Pull-Up Bar",
        "Cycling Shorts", "Foam Roller", "Kayak", "Camping Tent"
    ],
    "Accessories & Lifestyle": [
        "Handbag", "Backpack", "Wallet", "Sunglasses", "Leather Belt", "Travel Pillow", "Key Organizer",
        "Luggage Set", "Watch", "Scarf", "Phone Case", "Umbrella", "Jewelry Box", "Perfume",
        "Smart Key Finder"
    ],
    "Books & Stationery": [
        "Novel", "Cookbook", "Science Fiction Book", "Travel Guide", "Notebook", "Sketchpad",
        "Planner", "Children's Storybook", "History Book", "Comic Book", "Poetry Book", "Self-Help Book",
        "Language Workbook", "Art Book", "Diary"
    ],
    "Toys & Games": [
        "Board Game", "Puzzle", "Building Blocks", "Remote-Control Car", "Stuffed Animal", "Action Figure",
        "LEGO Set", "Drone", "Play Kitchen Set", "Chess Set", "Card Game", "Yo-Yo", "Rubik's Cube",
        "Dollhouse", "Toy Train Set"
    ]
}

# Define price ranges for each category for realistic simulation
price_ranges = {
    "Clothing & Apparel": (15, 120),
    "Tech & Electronics": (50, 500),
    "Home & Furniture": (50, 500),
    "Kitchen & Appliances": (30, 300),
    "Fitness & Sports": (20, 300),
    "Accessories & Lifestyle": (10, 150),
    "Books & Stationery": (10, 50),
    "Toys & Games": (5, 100)
}


def generate_products(num_products: int = 80):
    """
    Generate the product file using the above defined categories.
    """
    products = []
    pid = 1

    for category, products in categories.items():
        for product in products:
            products.append({
                "ProductID": f"P{str(pid).zfill(len(str(num_products)))}",
                "ProductDescription": product,
                "ProductCategory": category
            })
            pid += 1

    df = pd.DataFrame(products)

    # Sample from the products to meet the num_products constrain
    if len(df) > num_products:
        df = df.sample(num_products, random_state=35).reset_index(drop=True)

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    df.to_csv(PRODUCTS_PATH, index=False)
    print(f"Product list with {num_products} entries saved to {PRODUCTS_PATH}")


if __name__ == '__main__':
    generate_products()