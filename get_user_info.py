from flask import session
import database

# pull user phone number from database
def get_user_info(col):
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute(f"SELECT {col} FROM users WHERE email = ?", (session.get('email'),))
   
    user_info = cursor.fetchone()[0]
    conn.close()

    return user_info