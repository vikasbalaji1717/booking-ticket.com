import sqlite3
import pandas as pd

conn = sqlite3.connect("bus_booking.db")

df = pd.read_sql_query("SELECT * FROM users", conn)

df.to_excel("users.xlsx", index=False)

conn.close()

print("Users exported successfully!")