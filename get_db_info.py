from flask import session
import database

# pull user info from database
def get_user_info(col):
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute(f"SELECT {col} FROM users WHERE email = ?", (session.get('email'),))
   
    user_info = cursor.fetchone()[0]
    conn.close()

    return user_info


# pull shelter info from database
def get_shelter_info(col):
    conn = database.connect()
    cursor = conn.cursor()

    # username=shelter_name for now since we don't have email and password columns for shelters yet
    # change WHERE shelter_name to WHERE email once those columns added
    cursor.execute(f"SELECT {col} FROM shelters WHERE shelter_email = ?", (session.get('email'),))
   
    shelter_info = cursor.fetchone()[0]
    conn.close()

    return shelter_info

# pull pet info from database
def get_pet_info(col, pet_name):
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute(f"SELECT {col} FROM pets WHERE pet_name = ?", (pet_name,))
   
    pet_info = cursor.fetchone()[0]
    conn.close()

    return pet_info