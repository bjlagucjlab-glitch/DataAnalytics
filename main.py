import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_connection():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"Database not found {DB_PATH} ")

    return sqlite3.connect(DB_PATH)

def load_customers_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                cpii.customer_id
                , cpii.phone
                , cpii.national_id
                , cpii.card_last4
                , cpii.full_address
                , c.first_name
                , c.last_name
                , c.email
                , c.gender
                , c.birth_date
                , c.city
                , c.country
                , c.segment
                , c.signup_date
            FROM customers c
            JOIN customer_pii cpii ON c.customer_id = cpii.customer_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_products_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                p.product_id
                , p.name AS product
                , c.name AS category
                , s.name AS supplier
                , s.country
                , s.rating
                , p.price
                , p.cost
                , p.is_active
            FROM products p
            JOIN categories c ON c.category_id = p.category_id
            JOIN suppliers s ON s.supplier_id = p.supplier_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_returns_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                r.return_id
                , r.order_id
                , r.reason
                , r.return_date
                , r.refund_amount
            FROM returns r
            """
    df = pd.read_sql_query(query, conn)
    return df 

def load_employees_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                e.employee_id
                , e.first_name
                , e.last_name
                , e.title
                , e.region
                , e.hire_date
                , e.manager_id
                , es.base_salary
                , es.bonus
                , es.currency
            FROM employees e
            JOIN employee_salaries es ON es.employee_id = e.employee_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_orders_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                order_id
                , o.order_date
                , o.customer_id
                , o.employee_id
                , o.status
                , o.ship_country
                , o.ship_city
            FROM orders o
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_inventory_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                i.inventory_id
                , i.product_id
                , w.name
                , w.city
                , w.country
                , i.quantity
            FROM inventory i
            JOIN warehouses w ON w.warehouse_id = i.warehouse_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_shipments_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                s.shipment_id
                , s.order_id
                , s.shipped_date
                , s.delivered_date
                , s.cost
                , sh.name
                , sh.country
            FROM shipments s
            JOIN shippers sh ON sh.shipper_id = s.shipper_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_reviews_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                r.review_id
                , r.product_id
                , r.customer_id
                , r.rating
                , r.review_date
            FROM reviews r
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_payments_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                p.payment_id
                , p.order_id
                , p.method
                , p.amount
                , p.paid_at
            FROM payments p
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_order_items_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                oi.order_item_id
                , oi.order_id
                , oi.product_id
                , oi.quantity
                , oi.unit_price
                , oi.discount
                , p.name
                , p.discount_pct
                , p.start_date
                , p.end_date
            FROM order_items oi
            JOIN promotions p ON p.promotion_id = oi.promotion_id
            """
    df = pd.read_sql_query(query, conn)
    return df


HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, 'online_store.db')
connect = get_connection()

customers = load_customers_to_df(connect)
# print(customers.head(5))

products = load_products_to_df(connect)
# print(products.head(5))

employees = load_employees_to_df(connect)
# print(employees.head(5))

orders = load_orders_to_df(connect)
# print(orders.head(5))

returns = load_returns_to_df(connect)
# print(returns.head(5))

inventory = load_inventory_to_df(connect)
# print(inventory.head(5))

shipments = load_shipments_to_df(connect)
# print(shipments.head(5))

reviews = load_reviews_to_df(connect)
# print(reviews.head(5))

payments = load_payments_to_df(connect)
# print(payments.head(5))

order_items = load_order_items_to_df(connect)
# print(order_items.head(5))


#CRIIIIIIIIIIIIIIIIIIIIIIIIIT
completed_orders = orders[orders['status'] == 'completed']
full_orders = completed_orders.merge(order_items, on='order_id', how='inner')
full_orders['revenue'] = full_orders['unit_price'] * full_orders['quantity'] * (1 - full_orders['discount'])
full_orders['order_date'] = pd.to_datetime(full_orders['order_date'])
full_orders['year'] = full_orders['order_date'].dt.year
y_2022_to_2025 =  full_orders[full_orders['year'].between(2022, 2025)]
revenue_by_years = y_2022_to_2025.groupby('year')['revenue'].sum().reset_index()
sns.barplot(data=revenue_by_years, x='year', y='revenue', palette='Set2')
plt.show()
#############################


#Динаміка продажів за місяцями. Побудувати графік доходу та кількості замовлень за місяцями за весь період (2022–2025). Використати лінійний графік Seaborn і додати ковзне середнє.
df = orders.merge(order_items, on="order_id")

df["order_date"] = pd.to_datetime(df["order_date"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)

df["revenue"] = df["quantity"] * df["unit_price"]

monthly_stats = (
    df.groupby("month", as_index=False)
      .agg(
          revenue=("revenue", "sum"),
          orders_count=("order_id", "nunique")
      )
)

monthly_stats["revenue_ma"] = monthly_stats["revenue"].rolling(window=3).mean()
monthly_stats["orders_ma"] = monthly_stats["orders_count"].rolling(window=3).mean()

print(monthly_stats)

plt.figure(figsize=(14, 6))

sns.lineplot(data=monthly_stats, x="month", y="revenue", label="Revenue")
sns.lineplot(data=monthly_stats, x="month", y="revenue_ma", label="Revenue MA(3)")

plt.title("Revenue by Month")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

plt.figure(figsize=(14, 6))

sns.lineplot(data=monthly_stats, x="month", y="orders_count", label="Orders Count")
sns.lineplot(data=monthly_stats, x="month", y="orders_ma", label="Orders MA(3)")

plt.title("Orders Count by Month")
plt.xlabel("Month")
plt.ylabel("Orders Count")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


########## ТОП КАТЕГОРІЇ

df = order_items.merge(products, on="product_id")

df["revenue"] = df["quantity"] * df["unit_price"]
df["margin"] = df["quantity"] * (df["price"] - df["cost"])

top_products_revenue = (
    df.groupby("product", as_index=False)["revenue"]
      .sum()
      .sort_values("revenue", ascending=False)
      .head(10)
)

top_products_margin = (
    df.groupby("product", as_index=False)["margin"]
      .sum()
      .sort_values("margin", ascending=False)
      .head(10)
)

top_categories_revenue = (
    df.groupby("category", as_index=False)["revenue"]
      .sum()
      .sort_values("revenue", ascending=False)
      .head(10)
)

top_categories_margin = (
    df.groupby("category", as_index=False)["margin"]
      .sum()
      .sort_values("margin", ascending=False)
      .head(10)
)

fig, ax = plt.subplots(2, 2, figsize=(10, 10))

sns.barplot(data=top_products_revenue, x="revenue", y="product", ax=ax[0, 0], palette='Set2')
ax[0, 0].set_title("Top 10 Products by Revenue")

sns.barplot(data=top_products_margin, x="margin", y="product", ax=ax[0, 1], palette='Set2')
ax[0, 1].set_title("Top 10 Products by Margin")

sns.barplot(data=top_categories_revenue, x="revenue", y="category", ax=ax[1, 0], palette='Set2')
ax[1, 0].set_title("Top 10 Categories by Revenue")

sns.barplot(data=top_categories_margin, x="margin", y="category", ax=ax[1, 1], palette='Set2')
ax[1, 1].set_title("Top 10 Categories by Margin")
plt.show()
