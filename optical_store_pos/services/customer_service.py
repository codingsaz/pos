import sqlite3
from optical_store_pos.models.customer import Customer
from optical_store_pos.db.database import create_connection

class CustomerService:
    def get_all_customers(self):
        conn = create_connection()
        if conn is None:
            return []

        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM customers")

            rows = cur.fetchall()
            customers = []
            for row in rows:
                customers.append(Customer(*row))
            return customers
        except sqlite3.Error as e:
            print(e)
            return []
        finally:
            if conn:
                conn.close()
