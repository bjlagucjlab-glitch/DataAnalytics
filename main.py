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

def load_promotions_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                promotion_id
                , name AS promotion
                , discount_pct AS discount_pct_pr
            FROM promotions
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
                , p.name as promotion
                , p.discount_pct
                , p.start_date
                , p.end_date
            FROM order_items oi
            LEFT JOIN promotions p ON p.promotion_id = oi.promotion_id
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


# customers.info()
customers['email'] = customers['email'].fillna('no_data')
customers['card_last4'] = customers['card_last4'].astype(int)
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
customers['birth_date'] = pd.to_datetime(customers['birth_date'])
customers['gender'] = customers['gender'].str.lower().replace('','no_data')
customers['city'] = customers['city'].str.strip().str.capitalize() 

country_mapping = {
    'poland': 'PL', 'polska': 'PL', 'pl': 'PL',
    'united kingdom': 'UK', 'u.k.': 'UK', 'uk': 'UK', 'britain': 'UK',
    'united states': 'US', 'u.s.a.': 'US', 'usa': 'US', 'us': 'US',
    'germany': 'DE', 'deutschland': 'DE', 'de': 'DE',
    'france': 'FR', 'fr': 'FR',
    'spain': 'ES', 'españa': 'ES', 'es': 'ES',
    'italy': 'IT', 'italia': 'IT', 'it': 'IT'
}
customers['country'] = customers['country'].str.strip().str.replace(country_mapping)

promotions = load_promotions_to_df(connect)


#CRIT «Рада директорів через 15 хвилин»  
completed_orders = orders[orders['status'] == 'completed']
full_orders = completed_orders.merge(order_items, on='order_id', how='inner')
revenue_clean = (
    full_orders['unit_price'] * full_orders['quantity'] * (1 - full_orders['discount'].fillna(0)) * (1 - full_orders['discount_pct'].fillna(0))
)
full_orders['revenue'] = revenue_clean
full_orders['order_date'] = pd.to_datetime(full_orders['order_date'])
full_orders['year'] = full_orders['order_date'].dt.year
y_2022_to_2025 = full_orders[full_orders['year'].between(2022, 2025)].copy()
revenue_by_years = y_2022_to_2025.groupby('year')['revenue'].sum().reset_index()

plt.figure(figsize=(10, 6))
sns.barplot(data=revenue_by_years, x='year', y='revenue', palette='Set2')
plt.show()


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


########## Топкатегорії та товари.

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

#Аналіз ефективності промоакцій. 
df = order_items.merge(products[["product_id", 'cost']], on='product_id')
df['discount'] = df['discount'].fillna(0)
df['discount_pct'] = df['discount_pct'].fillna(0)
df['promotion'] = df['promotion'].fillna('Без акції')

df['revenue'] = df['quantity'] * df['unit_price'] * (1 - df['discount']) * (1 - df['discount_pct'])
df['total_cost'] = df['quantity'] * df['cost']
df['margin_val'] = df['revenue'] - df['total_cost']


orders_grouped = df.groupby(['order_id', 'promotion']).agg(
    order_revenue=('revenue', 'sum'),
    order_margin=('margin_val', 'sum')
).reset_index()

promo_analysis = orders_grouped.groupby('promotion').agg(
    avg_check=('order_revenue', 'mean'),        
    avg_margin=('order_margin', 'mean'),        
    total_revenue=('order_revenue', 'sum'),    
    total_margin=('order_margin', 'sum'),       
    orders_count=('order_id', 'count')          
).round(2)

promo_analysis['margin_pct'] = (promo_analysis['total_margin'] / promo_analysis['total_revenue'] * 100).round(2)

promo_analysis = promo_analysis.sort_values('avg_check', ascending=False).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
sns.barplot(data=promo_analysis, x='avg_check', y='promotion', ax=axes[0], palette='Blues_r')
axes[0].set_title('Средний чек по акциям')
axes[0].set_xlabel('Сумма чека')
axes[0].set_ylabel('Промоакция')

sns.barplot(data=promo_analysis, x='avg_margin', y='promotion', ax=axes[1], palette='Greens_d')
axes[1].set_title('Средняя маржа заказа по акциям')
axes[1].set_xlabel('Маржа')
axes[1].set_ylabel('')

plt.tight_layout()
plt.show()


#Способи оплати

order_by_method=(payments.groupby('method')['order_id'].nunique().reset_index(name='order_count'))
revenue_by_method=(payments.groupby('method')['amount'].sum().reset_index(name='payments_sum'))

order_revenue=(revenue_df.groupby('order_id')['revenue'].sum().reset_index())
check_df=order_revenue.merge(payments.groupby('order_id')['amount'].sum().reset_index(),on='order_id',how='left')

check_df['amount']=check_df['amount'].fillna(0)
check_df['difference']=(check_df['revenue']-check_df['amount'])
check_df['revenue']=check_df['revenue'].round(2)
check_df['amount']=check_df['amount'].round(2)

no_payment= check_df[check_df['amount']==0]
print('Кількість замовлень без оплат',len(no_payment))

difference=check_df[check_df['difference'].abs()>0.01]
print(difference)
print(check_df.head(20))

# Вітрина доходу.
completed_orders = orders[orders['status'] == 'completed']

revenue_df = completed_orders.merge(order_items,on='order_id',how='inner')

revenue_df['revenue'] = (revenue_df['quantity']* revenue_df['unit_price']* (1 - revenue_df['discount']))

revenue_df.to_csv('revenue_mart.csv',index=False)

print(revenue_df.head())
print(revenue_df.shape)

#Уякому місяці ми продаємо найкраще

revenue_df['order_date'] = pd.to_datetime(revenue_df['order_date'])
orders_revenue = revenue_df.groupby(['order_id', 'order_date'])['revenue'].sum().reset_index()
orders_revenue['month'] = orders_revenue['order_date'].dt.month
month_revenue = orders_revenue.groupby('month')['revenue'].mean().reset_index()

print(month_revenue)

sns.barplot(data=month_revenue, x='month', y='revenue')
plt.title('Середня виручка за місяцями')
plt.xlabel('Місяць')
plt.ylabel('Середня виручка')

plt.show()

best_month = month_revenue.loc[month_revenue['revenue'].idxmax(),'month']

print('Місяць з найбільшою середньою виручкою:', best_month)

print(revenue_df.head())

# Скільки ми втрачаємо через скасування?
total_orders = len(orders)

cancelled_orders = len(
orders[orders["status"].str.lower() == "cancelled"]
)

cancelled_share = round(
cancelled_orders / total_orders * 100,
2
)

print(f"Cancelled orders: {cancelled_orders}")
print(f"Total orders: {total_orders}")
print(f"Share of cancelled orders: {cancelled_share}%")

cancel_data = pd.DataFrame({
"Status": ["Cancelled", "Completed"],
"Count": [
cancelled_orders,
total_orders - cancelled_orders
]
})

plt.figure(figsize=(6, 4))
sns.barplot(
data=cancel_data,
x="Status",
y="Count"
)

plt.title("Cancelled vs Other Orders")
plt.xlabel("Order Status")
plt.ylabel("Number of Orders")
plt.tight_layout()
plt.show()
