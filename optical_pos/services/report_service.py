import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from datetime import date
from optical_pos.db import models
from optical_pos.db.database import engine

def get_sales_report(start_date: date, end_date: date) -> pd.DataFrame:
    """
    Generates a sales report for a given date range.
    Returns a pandas DataFrame.
    """
    query = select(
        models.Sale.id,
        models.Sale.date,
        models.Customer.name.label("customer_name"),
        models.Sale.total
    ).join(models.Sale.customer).where(
        models.Sale.date.between(start_date, end_date)
    )

    df = pd.read_sql_query(query, engine)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def get_top_products_report(limit: int = 5) -> pd.DataFrame:
    """
    Generates a report of the top selling products by quantity.
    Returns a pandas DataFrame.
    """
    query = select(
        models.Product.name,
        func.sum(models.SaleItem.qty).label("total_quantity")
    ).join(models.SaleItem.product).group_by(
        models.Product.name
    ).order_by(
        func.sum(models.SaleItem.qty).desc()
    ).limit(limit)

    df = pd.read_sql_query(query, engine)
    return df

def get_profit_loss_report(start_date: date, end_date: date) -> pd.DataFrame:
    """
    Generates a simplified profit/loss report.
    Note: This is a simplified version. A real implementation would be more complex.
    """
    sales_query = select(
        func.sum(models.Sale.total).label("total_revenue")
    ).where(models.Sale.date.between(start_date, end_date))

    # This is a very simplified cost calculation.
    # It calculates cost based on the products sold in the period.
    cost_query = select(
        func.sum(models.Product.cost_price * models.SaleItem.qty).label("total_cost")
    ).join(models.SaleItem.product).where(
        models.SaleItem.sale.has(models.Sale.date.between(start_date, end_date))
    )

    with engine.connect() as connection:
        total_revenue = connection.execute(sales_query).scalar_one_or_none() or 0
        total_cost = connection.execute(cost_query).scalar_one_or_none() or 0

    profit = total_revenue - total_cost

    data = {
        "Metric": ["Total Revenue", "Total Cost of Goods Sold", "Gross Profit"],
        "Amount": [total_revenue, total_cost, profit]
    }

    return pd.DataFrame(data)
