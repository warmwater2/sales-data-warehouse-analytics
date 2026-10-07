import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

connection_string = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(connection_string)

file_path = "data/processed/cleaned_sales.csv"
df = pd.read_csv(file_path)

df["Order Date"] = pd.to_datetime(df["Order Date"])

with engine.begin() as connection:

    connection.execute(text("TRUNCATE TABLE fact_sales, dim_date, dim_customer, dim_product, dim_location RESTART IDENTITY CASCADE"))

    customers = df[
        ["Customer ID", "Customer Name", "Segment"]
    ].drop_duplicates()

    for _, row in customers.iterrows():
        connection.execute(
            text("""
                INSERT INTO dim_customer
                (customer_id, customer_name, segment)
                VALUES (:customer_id, :customer_name, :segment)
                ON CONFLICT (customer_id) DO NOTHING
            """),
            {
                "customer_id": row["Customer ID"],
                "customer_name": row["Customer Name"],
                "segment": row["Segment"]
            }
        )

    products = df[
        ["Product ID", "Product Name", "Category", "Sub-Category"]
    ].drop_duplicates()

    for _, row in products.iterrows():
        connection.execute(
            text("""
                INSERT INTO dim_product
                (product_id, product_name, category, sub_category)
                VALUES (:product_id, :product_name, :category, :sub_category)
                ON CONFLICT (product_id) DO NOTHING
            """),
            {
                "product_id": row["Product ID"],
                "product_name": row["Product Name"],
                "category": row["Category"],
                "sub_category": row["Sub-Category"]
            }
        )

    locations = df[
        ["City", "State", "Region"]
    ].drop_duplicates()

    for _, row in locations.iterrows():
        connection.execute(
            text("""
                INSERT INTO dim_location
                (city, state, region)
                VALUES (:city, :state, :region)
                ON CONFLICT (city, state, region) DO NOTHING
            """),
            {
                "city": row["City"],
                "state": row["State"],
                "region": row["Region"]
            }
        )

    dates = df[["Order Date"]].drop_duplicates()

    for _, row in dates.iterrows():
        date = row["Order Date"]

        connection.execute(
            text("""
                INSERT INTO dim_date
                (date_key, full_date, day, month, month_name, quarter, year)
                VALUES (:date_key, :full_date, :day, :month,
                        :month_name, :quarter, :year)
                ON CONFLICT (date_key) DO NOTHING
            """),
            {
                "date_key": int(date.strftime("%Y%m%d")),
                "full_date": date.date(),
                "day": date.day,
                "month": date.month,
                "month_name": date.strftime("%B"),
                "quarter": (date.month - 1) // 3 + 1,
                "year": date.year
            }
        )

    for _, row in df.iterrows():

        date = row["Order Date"]

        customer_result = connection.execute(
            text("""
                SELECT customer_key
                FROM dim_customer
                WHERE customer_id = :customer_id
            """),
            {"customer_id": row["Customer ID"]}
        ).fetchone()

        product_result = connection.execute(
            text("""
                SELECT product_key
                FROM dim_product
                WHERE product_id = :product_id
            """),
            {"product_id": row["Product ID"]}
        ).fetchone()

        location_result = connection.execute(
            text("""
                SELECT location_key
                FROM dim_location
                WHERE city = :city
                AND state = :state
                AND region = :region
            """),
            {
                "city": row["City"],
                "state": row["State"],
                "region": row["Region"]
            }
        ).fetchone()

        connection.execute(
            text("""
                INSERT INTO fact_sales
                (
                    date_key,
                    customer_key,
                    product_key,
                    location_key,
                    quantity,
                    sales_amount,
                    discount,
                    profit
                )
                VALUES
                (
                    :date_key,
                    :customer_key,
                    :product_key,
                    :location_key,
                    :quantity,
                    :sales_amount,
                    :discount,
                    :profit
                )
            """),
            {
                "date_key": int(date.strftime("%Y%m%d")),
                "customer_key": customer_result[0],
                "product_key": product_result[0],
                "location_key": location_result[0],
                "quantity": int(row["Quantity"]),
                "sales_amount": float(row["Sales"]),
                "discount": float(row["Discount"]),
                "profit": float(row["Profit"])
            }
        )

print("Data loaded successfully into PostgreSQL.")