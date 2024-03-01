from flask import session
import database

# function to pull shelter name from database
def get_shelter_name():
    conn = database.connect()
    cursor = conn.cursor()

    # username=shelter_name for now since we don't have email and password columns for shelters yet
    # change WHERE shelter_name to WHERE email once those columns added
    cursor.execute("SELECT shelter_name FROM shelters WHERE shelter_name = ?", (session.get('username'),))
   
    shelter_name = cursor.fetchone()[0]
    conn.close()

    return shelter_name