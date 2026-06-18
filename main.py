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
    
HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, 'online_store.db')
connect = get_connection()


order_items = load_order_items_to_df(connect)
# print(order_items.head(5))

orders = load_orders_to_df(connect)
# print(orders.head(5))

products = load_products_to_df(connect)

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

