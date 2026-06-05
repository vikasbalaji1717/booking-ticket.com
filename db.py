import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="vik@s17",
    database="areobus"
)

cursor = db.cursor()
print("Connected Successfully!")