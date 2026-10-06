"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/data_generation/generate_data.py
Purpose: Generates a realistic, large-scale synthetic dataset reflecting the
         Bangladesh e-commerce landscape (2023-2025). Introduces controlled
         data quality issues for the data validation & cleaning pipeline.
"""

import os
import random
import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# CONSTANTS & BANGLADESH REFERENCE DATA
# ---------------------------------------------------------

DIVISIONS_CITIES = {
    "Dhaka": [("Dhaka", 0.75), ("Gazipur", 0.15), ("Narayanganj", 0.10)],
    "Chattogram": [("Chattogram", 0.80), ("Cox's Bazar", 0.20)],
    "Sylhet": [("Sylhet", 0.78), ("Moulvibazar", 0.22)],
    "Rajshahi": [("Rajshahi", 0.70), ("Bogura", 0.30)],
    "Khulna": [("Khulna", 0.72), ("Jashore", 0.28)],
    "Barishal": [("Barishal", 1.00)],
    "Rangpur": [("Rangpur", 0.68), ("Dinajpur", 0.32)],
    "Mymensingh": [("Mymensingh", 1.00)]
}

DIVISION_WEIGHTS = {
    "Dhaka": 0.54,
    "Chattogram": 0.16,
    "Sylhet": 0.07,
    "Rajshahi": 0.06,
    "Khulna": 0.06,
    "Rangpur": 0.04,
    "Barishal": 0.04,
    "Mymensingh": 0.03
}

ACQUISITION_CHANNELS = ["Facebook Ads", "Organic Search", "Google Ads", "TikTok / Instagram", "Referral", "Direct / Offline"]
ACQUISITION_WEIGHTS = [0.38, 0.22, 0.18, 0.10, 0.08, 0.04]

PAYMENT_METHODS = ["bKash", "Cash on Delivery", "Nagad", "Card", "Bank Transfer"]
PAYMENT_WEIGHTS = [0.42, 0.33, 0.15, 0.08, 0.02]

ORDER_STATUSES = ["Delivered", "Returned", "Cancelled", "Shipped", "Processing"]
ORDER_STATUS_WEIGHTS = [0.89, 0.05, 0.04, 0.01, 0.01]

PRODUCT_CATEGORIES = {
    "Electronics": {
        "subcategories": ["Smartphones", "Smartwatches", "Power Banks", "Laptops", "Earbuds", "Bluetooth Speakers"],
        "price_range": (1200, 85000),
        "margin_range": (0.14, 0.24),
        "brands": ["Walton", "Samsung", "Xiaomi", "Realme", "Baseus", "Anker", "Lenovo", "Apple", "Microlab"]
    },
    "Mobile Accessories": {
        "subcategories": ["Phone Cases", "Screen Protectors", "Fast Chargers", "Type-C Cables", "OTG Adapters", "Car Mounts"],
        "price_range": (150, 2200),
        "margin_range": (0.45, 0.65),
        "brands": ["Baseus", "Remax", "Hoco", "Joyroom", "Ugreen", "Generic"]
    },
    "Fashion": {
        "subcategories": ["Panjabi", "Sarees", "Salwar Kameez", "Denim Jeans", "Polo Shirts", "Sneakers", "Kurtis", "T-Shirts"],
        "price_range": (550, 9500),
        "margin_range": (0.35, 0.52),
        "brands": ["Aarong", "Yellow", "Cats Eye", "Sailor", "Apex", "Bata", "Richman", "Lotto", "Kay Kraft"]
    },
    "Beauty": {
        "subcategories": ["Face Serums", "Sunscreens", "Moisturizers", "Lipsticks", "Hair Oils", "Face Wash", "Shampoo"],
        "price_range": (350, 4200),
        "margin_range": (0.42, 0.60),
        "brands": ["The Ordinary", "COSRX", "Neutrogena", "Lafz", "Parachute", "Nivea", "Focallure", "Simple"]
    },
    "Home & Living": {
        "subcategories": ["Bedsheets", "Cookware Sets", "LED Lights", "Curtains", "Electric Blenders", "Storage Racks"],
        "price_range": (450, 11000),
        "margin_range": (0.28, 0.44),
        "brands": ["Kiam", "Walton", "Vision", "Regal", "Jafran", "Transcom", "Philips"]
    },
    "Grocery": {
        "subcategories": ["Miniket Rice", "Mustard Oil", "Spices Combo", "Special Ghee", "Sundarban Honey", "Sylhet Tea", "Lentils"],
        "price_range": (120, 2600),
        "margin_range": (0.10, 0.18),
        "brands": ["Pran", "Radhuni", "Teer", "Fresh", "Ispahani", "Chashi", "Square", "ACI Pure"]
    },
    "Sports": {
        "subcategories": ["Cricket Bats", "Footballs", "Gym Gloves", "Yoga Mats", "Bangladesh Cricket Jersey", "Badminton Rackets"],
        "price_range": (400, 6500),
        "margin_range": (0.30, 0.45),
        "brands": ["CA Sports", "SS Ton", "Cosco", "Yonex", "Kiprun", "Decathlon", "Nivia"]
    },
    "Books": {
        "subcategories": ["BCS Guides", "Academic & Admission", "Fiction & Novel", "Islamic Literature", "Self Development", "English Literature"],
        "price_range": (180, 1400),
        "margin_range": (0.24, 0.38),
        "brands": ["Prothoma", "Batighar", "Anupam", "Tamralipi", "Somoy", "Professor's", "Guardian"]
    }
}

START_DATE = datetime.date(2023, 1, 1)
END_DATE = datetime.date(2025, 9, 30)
TOTAL_DAYS = (END_DATE - START_DATE).days


def get_seasonal_multiplier(d: datetime.date) -> float:
    """Return seasonal sales demand multiplier for a given date in Bangladesh."""
    # Ramadan / Eid-ul-Fitr windows:
    # 2023: Ramadan ~March 23 - April 21, Eid ~April 22
    # 2024: Ramadan ~March 11 - April 9, Eid ~April 10
    # 2025: Ramadan ~March 1 - March 29, Eid ~March 30
    eid_fitr_ranges = [
        (datetime.date(2023, 3, 20), datetime.date(2023, 4, 25)),
        (datetime.date(2024, 3, 10), datetime.date(2024, 4, 15)),
        (datetime.date(2025, 3, 1), datetime.date(2025, 4, 5))
    ]
    for start_r, end_r in eid_fitr_ranges:
        if start_r <= d <= end_r:
            days_to_peak = abs((d - (start_r + datetime.timedelta(days=20))).days)
            return max(1.8, 2.7 - (days_to_peak * 0.04))

    # Eid-ul-Adha windows:
    # 2023: June 25 - July 2
    # 2024: June 13 - June 20
    # 2025: June 4 - June 11
    eid_adha_ranges = [
        (datetime.date(2023, 6, 18), datetime.date(2023, 7, 3)),
        (datetime.date(2024, 6, 8), datetime.date(2024, 6, 22)),
        (datetime.date(2025, 5, 28), datetime.date(2025, 6, 12))
    ]
    for start_r, end_r in eid_adha_ranges:
        if start_r <= d <= end_r:
            return 1.6

    # Pohela Boishakh (Bengali New Year ~ April 14)
    if d.month == 4 and 10 <= d.day <= 16:
        return 1.4

    # 11.11 & Year-End Mega Campaigns (Nov 5 - Dec 31)
    if d.month == 11 and 8 <= d.day <= 15:
        return 2.2
    if d.month == 12 and 15 <= d.day <= 31:
        return 1.7
    if d.month in (11, 12):
        return 1.35

    # General weekend uplift (Friday/Saturday in BD)
    if d.weekday() in (4, 5):
        return 1.15

    return 1.0


def generate_products(n_products: int = 600) -> pd.DataFrame:
    """Generate product catalog with realistic costs, prices, and margins."""
    products = []
    prod_id = 1
    cat_keys = list(PRODUCT_CATEGORIES.keys())

    # Distribute products across categories
    cat_distribution = {
        "Electronics": 0.12,
        "Mobile Accessories": 0.15,
        "Fashion": 0.25,
        "Beauty": 0.16,
        "Home & Living": 0.12,
        "Grocery": 0.08,
        "Sports": 0.06,
        "Books": 0.06
    }

    for cat, weight in cat_distribution.items():
        cat_count = int(n_products * weight)
        meta = PRODUCT_CATEGORIES[cat]
        for i in range(cat_count):
            subcat = random.choice(meta["subcategories"])
            brand = random.choice(meta["brands"])
            name = f"{brand} {subcat} {random.choice(['Pro', 'Max', 'Plus', 'Classic', 'Lite', 'Edition', 'Prime', 'Select', 'Series'])} {random.randint(10, 999)}"
            
            p_min, p_max = meta["price_range"]
            # Log-normal distribution of prices within range
            selling_price = round(float(np.exp(np.random.uniform(np.log(p_min), np.log(p_max)))), -1)
            selling_price = max(p_min, min(p_max, selling_price))

            margin = np.random.uniform(*meta["margin_range"])
            cost_price = round(selling_price * (1.0 - margin), 2)

            products.append({
                "product_id": prod_id,
                "product_name": name,
                "category": cat,
                "subcategory": subcat,
                "brand": brand,
                "cost_price": cost_price,
                "selling_price": selling_price
            })
            prod_id += 1

    return pd.DataFrame(products)


def generate_customers(n_customers: int = 35000) -> pd.DataFrame:
    """Generate customer demographics across Bangladesh."""
    customers = []
    div_names = list(DIVISION_WEIGHTS.keys())
    div_probs = [DIVISION_WEIGHTS[d] for d in div_names]

    for c_id in range(1, n_customers + 1):
        # Signup date distribution (growing over time)
        day_offset = int(np.random.beta(2.0, 1.2) * (TOTAL_DAYS - 30))
        signup_date = START_DATE + datetime.timedelta(days=day_offset)

        # Division & city
        div = np.random.choice(div_names, p=div_probs)
        city_tuples = DIVISIONS_CITIES[div]
        cities = [c[0] for c in city_tuples]
        c_weights = [c[1] for c in city_tuples]
        city = np.random.choice(cities, p=c_weights)

        # Demographics
        gender = np.random.choice(["Male", "Female"], p=[0.58, 0.42])
        # Age: concentrated around 22-38
        age = int(np.clip(np.random.normal(29, 7.5), 18, 68))
        
        c_type = np.random.choice(["Individual", "Corporate / SME"], p=[0.94, 0.06])
        channel = np.random.choice(ACQUISITION_CHANNELS, p=ACQUISITION_WEIGHTS)

        # Customer behavioral propensity archetype
        # 1: VIP / Champion (15%)
        # 2: Loyal / Repeat (35%)
        # 3: Casual / One-off (50%)
        tier = np.random.choice(["VIP", "Regular", "Casual"], p=[0.15, 0.35, 0.50])

        customers.append({
            "customer_id": c_id,
            "signup_date": signup_date,
            "gender": gender,
            "age": age,
            "city": city,
            "division": div,
            "customer_type": c_type,
            "acquisition_channel": channel,
            "_tier": tier  # Internal helper for order generation
        })

    return pd.DataFrame(customers)


def generate_orders_and_items(
    df_customers: pd.DataFrame,
    df_products: pd.DataFrame,
    target_orders: int = 120000
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate realistic orders and order items reflecting behavioral dynamics."""
    orders = []
    order_items = []
    order_id = 1
    item_id = 1

    prod_records = df_products.to_dict("records")
    prod_ids = [p["product_id"] for p in prod_records]
    prod_lookup = {p["product_id"]: p for p in prod_records}

    # Weight product selection by popularity
    # Cheaper items (Mobile accessories, Beauty, Grocery, Fashion) are bought more frequently
    prod_weights = []
    for p in prod_records:
        cat = p["category"]
        if cat in ["Mobile Accessories", "Fashion", "Beauty"]:
            prod_weights.append(3.5)
        elif cat in ["Grocery", "Home & Living"]:
            prod_weights.append(2.0)
        elif cat in ["Electronics", "Sports"]:
            prod_weights.append(1.0)
        else:
            prod_weights.append(1.2)
    prod_weights = np.array(prod_weights) / sum(prod_weights)

    cust_dict = df_customers.to_dict("records")

    print(f"Generating orders for {len(cust_dict)} customers...")

    for cust in cust_dict:
        c_id = cust["customer_id"]
        c_tier = cust["_tier"]
        signup = cust["signup_date"]
        avail_days = (END_DATE - signup).days
        if avail_days <= 0:
            continue

        # Determine number of orders for this customer based on tier
        if c_tier == "VIP":
            n_orders = int(np.random.geometric(0.12) + np.random.randint(3, 10))
            n_orders = min(32, n_orders)
        elif c_tier == "Regular":
            n_orders = np.random.choice([2, 3, 4, 5, 6], p=[0.35, 0.30, 0.20, 0.10, 0.05])
        else:  # Casual
            n_orders = np.random.choice([1, 2], p=[0.72, 0.28])

        # Generate timestamps for customer orders
        # Inter-purchase times
        current_date = signup + datetime.timedelta(days=random.randint(0, min(14, avail_days)))
        
        # Inactivity/churn factor: some customers stop purchasing after some point
        churn_drop = (random.random() < 0.38)

        for ord_idx in range(n_orders):
            if current_date > END_DATE:
                break

            # Seasonal boost check: higher probability of purchasing during peak seasons
            mult = get_seasonal_multiplier(current_date)
            
            # Payment method preference
            pay_method = np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS)
            status = np.random.choice(ORDER_STATUSES, p=ORDER_STATUS_WEIGHTS)

            # Shipping fee: Free if large or Dhaka standard (60 BDT), Outside Dhaka (120 BDT)
            is_dhaka = (cust["division"] == "Dhaka")
            base_shipping = 60.0 if is_dhaka else 120.0

            # Items in this order
            n_items = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.35, 0.32, 0.18, 0.09, 0.04, 0.02])
            chosen_prod_ids = np.random.choice(prod_ids, size=n_items, replace=True, p=prod_weights)

            order_subtotal = 0.0
            order_cost = 0.0
            item_rows = []

            for pid in chosen_prod_ids:
                prod = prod_lookup[pid]
                qty = 1 if prod["selling_price"] > 3000 else np.random.choice([1, 2, 3], p=[0.82, 0.14, 0.04])
                u_price = prod["selling_price"]
                u_cost = prod["cost_price"]

                # Item discount (promotions, vouchers)
                has_discount = (random.random() < 0.28)
                item_discount = round(u_price * random.choice([0.05, 0.10, 0.15, 0.20]) if has_discount else 0.0, 2)
                item_revenue = round((u_price - item_discount) * qty, 2)
                item_total_cost = round(u_cost * qty, 2)
                item_profit = round(item_revenue - item_total_cost, 2)

                order_subtotal += item_revenue
                order_cost += item_total_cost

                item_rows.append({
                    "order_item_id": item_id,
                    "order_id": order_id,
                    "product_id": pid,
                    "quantity": qty,
                    "unit_price": u_price,
                    "discount": round(item_discount * qty, 2),
                    "cost": item_total_cost,
                    "revenue": item_revenue,
                    "profit": item_profit
                })
                item_id += 1

            # Free shipping promotion on orders > 2500 BDT
            shipping_fee = 0.0 if order_subtotal > 2500 else base_shipping
            # Order level voucher or discount
            order_voucher = round(random.choice([50, 100, 200]) if (random.random() < 0.18 and order_subtotal > 1500) else 0.0, 2)
            final_total = max(50.0, round(order_subtotal + shipping_fee - order_voucher, 2))

            orders.append({
                "order_id": order_id,
                "customer_id": c_id,
                "order_date": current_date,
                "order_status": status,
                "payment_method": pay_method,
                "delivery_status": "Delivered" if status == "Delivered" else ("Returned" if status == "Returned" else "Cancelled"),
                "shipping_fee": shipping_fee,
                "discount_amount": order_voucher,
                "total_amount": final_total
            })

            order_items.extend(item_rows)
            order_id += 1

            # Advance date for next order
            if churn_drop and ord_idx >= 1:
                # Sudden long gap or inactivity
                break
            else:
                gap_days = int(np.random.exponential(scale=45.0) + 12)
                current_date = current_date + datetime.timedelta(days=gap_days)

    df_orders = pd.DataFrame(orders)
    df_order_items = pd.DataFrame(order_items)
    return df_orders, df_order_items


def inject_raw_data_imperfections(
    df_cust: pd.DataFrame,
    df_prod: pd.DataFrame,
    df_ord: pd.DataFrame,
    df_items: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Inject realistic real-world data quality issues into raw data to be caught
    by the Data Quality Pipeline:
    - Missing values (city, gender, discount_amount)
    - Inconsistent casing and whitespace in categorical fields
    - Negative quantities / zero unit prices (accidental returns or bad logs)
    - Outlier ages (e.g. 142, -4)
    - Duplicate rows
    - Invalid date formats
    - Dangling foreign keys
    """
    print("Injecting controlled data-quality imperfections into raw dataset...")
    df_c_raw = df_cust.drop(columns=["_tier"]).copy()
    df_p_raw = df_prod.copy()
    df_o_raw = df_ord.copy()
    df_i_raw = df_items.copy()

    # 1. Customers: Missing values
    missing_city_idx = df_c_raw.sample(frac=0.012, random_state=SEED).index
    df_c_raw.loc[missing_city_idx, "city"] = np.nan

    missing_gender_idx = df_c_raw.sample(frac=0.015, random_state=SEED + 1).index
    df_c_raw.loc[missing_gender_idx, "gender"] = np.nan

    missing_chan_idx = df_c_raw.sample(frac=0.010, random_state=SEED + 2).index
    df_c_raw.loc[missing_chan_idx, "acquisition_channel"] = np.nan

    # 2. Customers: Casing and whitespace inconsistencies in cities
    case_mod_idx = df_c_raw.sample(frac=0.04, random_state=SEED + 3).index
    for idx in case_mod_idx:
        val = str(df_c_raw.loc[idx, "city"])
        if val and val != "nan":
            choice = random.choice([val.lower(), val.upper(), f"  {val}  ", val.replace("Chattogram", "Chittagong")])
            df_c_raw.loc[idx, "city"] = choice

    # 3. Customers: Outlier ages
    outlier_age_idx = df_c_raw.sample(n=45, random_state=SEED + 4).index
    df_c_raw.loc[outlier_age_idx[:25], "age"] = [random.randint(110, 150) for _ in range(25)]
    df_c_raw.loc[outlier_age_idx[25:], "age"] = [random.randint(-10, 0) for _ in range(20)]

    # 4. Customers: Duplicates
    dup_cust = df_c_raw.sample(n=135, random_state=SEED + 5)
    df_c_raw = pd.concat([df_c_raw, dup_cust], ignore_index=True)

    # 5. Orders: Missing discounts
    null_discount_idx = df_o_raw.sample(frac=0.025, random_state=SEED + 6).index
    df_o_raw.loc[null_discount_idx, "discount_amount"] = np.nan

    # 6. Orders: Invalid dates (represented as corrupted strings)
    df_o_raw["order_date"] = df_o_raw["order_date"].astype(str)
    inv_date_idx = df_o_raw.sample(n=35, random_state=SEED + 7).index
    df_o_raw.loc[inv_date_idx, "order_date"] = "1970-00-00"

    # 7. Orders: Duplicates
    dup_orders = df_o_raw.sample(n=110, random_state=SEED + 8)
    df_o_raw = pd.concat([df_o_raw, dup_orders], ignore_index=True)

    # 8. Order Items: Negative quantities and negative prices
    neg_qty_idx = df_i_raw.sample(n=42, random_state=SEED + 9).index
    df_i_raw.loc[neg_qty_idx, "quantity"] = -1

    neg_price_idx = df_i_raw.sample(n=18, random_state=SEED + 10).index
    df_i_raw.loc[neg_price_idx, "unit_price"] = -50.0

    # 9. Order Items: Dangling product IDs
    dangling_prod_idx = df_i_raw.sample(n=22, random_state=SEED + 11).index
    df_i_raw.loc[dangling_prod_idx, "product_id"] = 999999

    return df_c_raw, df_p_raw, df_o_raw, df_i_raw


def main():
    print("=========================================================")
    print("STARTING BANGLADESH E-COMMERCE DATA GENERATION PIPELINE")
    print("=========================================================")

    # 1. Products
    print("Generating products catalog (600 products across 8 categories)...")
    df_prod = generate_products(n_products=600)

    # 2. Customers
    print("Generating customer demographics (35,000 customers across Bangladesh)...")
    df_cust = generate_customers(n_customers=35000)

    # 3. Orders & Order Items
    print("Simulating realistic order sequences and basket dynamics...")
    df_ord, df_items = generate_orders_and_items(df_cust, df_products=df_prod, target_orders=120000)

    print(f"Generated clean baseline: {len(df_cust)} customers, {len(df_prod)} products, {len(df_ord)} orders, {len(df_items)} items.")

    # 4. Inject Raw Imperfections
    df_c_raw, df_p_raw, df_o_raw, df_i_raw = inject_raw_data_imperfections(df_cust, df_prod, df_ord, df_items)

    # 5. Save Raw CSVs
    print(f"Saving raw datasets to: {RAW_DATA_DIR}")
    df_c_raw.to_csv(os.path.join(RAW_DATA_DIR, "customers_raw.csv"), index=False)
    df_p_raw.to_csv(os.path.join(RAW_DATA_DIR, "products_raw.csv"), index=False)
    df_o_raw.to_csv(os.path.join(RAW_DATA_DIR, "orders_raw.csv"), index=False)
    df_i_raw.to_csv(os.path.join(RAW_DATA_DIR, "order_items_raw.csv"), index=False)

    print("=========================================================")
    print("DATA GENERATION COMPLETE:")
    print(f" - Raw Customers:   {len(df_c_raw):,} rows")
    print(f" - Raw Products:    {len(df_p_raw):,} rows")
    print(f" - Raw Orders:      {len(df_o_raw):,} rows")
    print(f" - Raw Order Items: {len(df_i_raw):,} rows")
    print("=========================================================")


if __name__ == "__main__":
    main()
