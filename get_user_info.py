from flask import session
import database

# pull user phone number from database
def get_user_phone():
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT phone FROM users WHERE email = ?", (session.get('email'),))
   
    user_phone = cursor.fetchone()[0]
    conn.close()

    return user_phone