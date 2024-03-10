import sqlite3

# CRUD table queries
CREATE_PROFILE_TABLE = """CREATE TABLE IF NOT EXISTS
profiles(profile_id INTEGER PRIMARY KEY AUTOINCREMENT)"""

CREATE_USERS_TABLE = """CREATE TABLE IF NOT EXISTS
users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, first_name TEXT, last_name TEXT,
email TEXT,password TEXT, phone INTEGER, house_type TEXT, current_pets TEXT, kids_under_ten TEXT, pet_insurance TEXT, seeking TEXT,account_type TEXT, matches_id INTEGER, FOREIGN KEY(profile_id) REFERENCES profiles(profile_id), FOREIGN KEY(matches_id) REFERENCES matches(matches_id))"""

CREATE_PASSED_PETS_TABLE = "CREATE TABLE IF NOT EXISTS passed_pets(pet_id INTEGER, passed_count INTEGER, FOREIGN KEY(pet_id) REFERENCES pets(pet_id))"

CREATE_MATCHES_TABLE = """CREATE TABLE IF NOT EXISTS
matches(matches_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, pet_id INTEGER, shelter_id INTEGER,
match_time INTERGER, FOREIGN KEY(user_id) REFERENCES users(user_id),FOREIGN KEY(pet_id) REFERENCES pets(pet_id), FOREIGN KEY(shelter_id) REFERENCES shelters(shelter_id))"""

CREATE_SHELTERS_TABLE = """CREATE TABLE IF NOT EXISTS
shelters(shelter_id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, shelter_name TEXT,shelter_email TEXT, shelter_password TEXT, shelter_address TEXT,account_type TEXT, about TEXT, link TEXT,
FOREIGN KEY(profile_id) REFERENCES profiles(profile_id))"""

CREATE_ADMIN_TABLE = """CREATE TABLE IF NOT EXISTS
admin(admin_id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, FOREIGN KEY(profile_id) REFERENCES profiles(profile_id))"""

CREATE_PETS_TABLE = """CREATE TABLE IF NOT EXISTS
pets(pet_id INTEGER PRIMARY KEY AUTOINCREMENT, shelter_id INTEGER, pet_name TEXT, pet_species TEXT, pet_breed TEXT,
pet_color TEXT, pet_likes TEXT, pet_dislikes TEXT, pet_age integer, pet_gender TEXT, pet_health TEXT, pet_photo TEXT, pet_good_with_other_animals TEXT,
pet_good_with_children TEXT, pet_size TEXT,adoption_status TEXT, matches_id INTEGER, FOREIGN KEY(shelter_id) REFERENCES shelters(shelter_id), FOREIGN KEY(matches_id) REFERENCES matches(matches_id))"""

CREATE_LIKES_TABLE = """CREATE TABLE IF NOT EXISTS
likes(likes_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, pet_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(user_id), FOREIGN KEY(pet_id) REFERENCES pets(pet_id))"""


GET_ALL_PROFILES = "SELECT * FROM profiles"

GET_ALL_USERS = "SELECT * FROM users"

GET_ALL_MATCHES = "SELECT * FROM matches"

GET_ALL_SHELTERS = "SELECT * FROM shelters"

GET_ALL_ADMINS = "SELECT * FROM admin"

GET_ALL_PETS = "SELECT * FROM pets"

ADD_NEW_PROFILE = "INSERT INTO profiles DEFAULT VALUES;"

ADD_NEW_USER = """INSERT INTO users (profile_id, first_name, last_name, email,password, phone, house_type, current_pets, kids_under_ten, pet_insurance, seeking, account_type, matches_id) 
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);"""

ADD_NEW_MATCH = "INSERT INTO matches (user_id, pet_id, shelter_id, match_time) VALUES (?,?,?,?);"

ADD_NEW_SHELTER = "INSERT INTO shelters (profile_id, shelter_name,shelter_email, shelter_password, shelter_address, account_type, about, link) VALUES (?,?,?,?,?,?,?,?);"

ADD_NEW_ADMIN = "INSERT INTO admin (profile_id) VALUES (?);"

ADD_NEW_PET = """INSERT INTO pets (shelter_id, pet_name, pet_species, pet_breed, pet_color, pet_likes, pet_dislikes, pet_age, pet_gender, pet_health, pet_photo, pet_good_with_other_animals, pet_good_with_children, pet_size, adoption_status, matches_id) 
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""

GET_PET_IMAGE = """SELECT pet_photo FROM pets WHERE pet_id = (?)"""

GET_PET_COUNT = "SELECT COUNT(*) FROM pets"

REMOVE_PROFILE = "DELETE FROM profiles WHERE profile_id = (?)"

REMOVE_USER = "DELETE FROM users WHERE user_id = (?)"

REMOVE_MATCH = "DELETE FROM matches WHERE matches_id = (?)"

REMOVE_SHELTER = "DELETE FROM shelters WHERE shelter_id = (?)"

REMOVE_ADMIN = "DELETE FROM admin WHERE admin_id = (?)"

REMOVE_PET = "DELETE FROM pets WHERE pet_id = (?)"

ADD_NEW_LIKE = "INSERT INTO likes (user_id, pet_id) VALUES (?,?);"

GET_USER_ID_BY_EMAIL = "SELECT user_id FROM users WHERE email = (?)"

GET_SHELTER_ID_BY_EMAIL = "SELECT shelter_id FROM shelters WHERE shelter_email = (?)"

GET_ALL_LIKES = "SELECT * FROM likes"

GET_LIKES_WITH_PET_ID = "SELECT * FROM likes WHERE pet_id = (?)"

GET_PETID_WITH_SHELTERID = "SELECT pet_id FROM pets WHERE shelter_id = (?)"

GET_LIKES_WITH_USER_ID = "SELECT * FROM likes WHERE user_id = (?)"

LIKE_TABLE_JOIN = """SELECT u.first_name, u.last_name, p.pet_name, u.user_id, p.pet_id
FROM likes l
JOIN pets p ON l.pet_id = p.pet_id
JOIN users u ON l.user_id = u.user_id
WHERE p.shelter_id = (?)"""

USER_UNIQUE_LIKES_JOIN = """
SELECT p.*
FROM likes l
JOIN pets p ON l.pet_id = p.pet_id
WHERE l.user_id = ?
"""

USER_UNIQUE_MATCHES_JOIN = """
SELECT p.*
FROM matches m
JOIN pets p ON m.pet_id = p.pet_id
WHERE m.user_id = ?
"""

SHELTER_PETS = """SELECT * from pets WHERE shelter_id = ?"""

UPDATE_PET_STATUS = """
UPDATE pets
SET adoption_status = ?
WHERE pet_id = ?
"""

CHECK_MATCH_EXISTS = """SELECT COUNT(*) FROM matches WHERE user_id = ? AND pet_id = ? and shelter_id = ?"""

CHECK_LIKE_EXISTS = """SELECT COUNT(*) FROM likes WHERE user_id = ? AND pet_id = ?"""

GET_MATCHID = """SELECT matches_id FROM matches WHERE pet_id = ? AND shelter_id = ? AND user_id = ?"""

CHECK_PET_MATCHES = """SELECT COUNT(*) FROM matches WHERE pet_id = ?"""

DELETE_LIKES_AT_PETID = """DELETE FROM likes WHERE pet_id = ?"""

PET_FROM_LIKES = """SELECT pet_id FROM likes where user_id = ?"""

USER_FROM_ID = """SELECT * FROM users where user_id = ?"""


# Define connection function
def connect():
    return sqlite3.connect("data.db")


# create tables function
def create_tables(connection):
    with connection:
        connection.execute(CREATE_PROFILE_TABLE)
        connection.execute(CREATE_USERS_TABLE)
        connection.execute(CREATE_MATCHES_TABLE)
        connection.execute(CREATE_SHELTERS_TABLE)
        connection.execute(CREATE_ADMIN_TABLE)
        connection.execute(CREATE_PETS_TABLE)
        connection.execute(CREATE_LIKES_TABLE)
        connection.execute(CREATE_PASSED_PETS_TABLE)

#----------------------------------------------------------------------------------------#
# insert new profile into table
def add_profile(connection):
    with connection:
        return connection.execute(ADD_NEW_PROFILE)


def get_all_profiles(connection):
    with connection:
        return connection.execute(GET_ALL_PROFILES).fetchall()


def remove_profile(connection, profile_id):
    return connection.execute(REMOVE_PROFILE, (profile_id,))

#----------------------------------------------------------------------------------------#
# insert new user into table
def add_user(connection, profile_id, first_name, last_name, email,password, phone, house_type, current_pets, kids_under_ten, pet_insurance, seeking,account_type, matches_id):
    with connection:
        return connection.execute(ADD_NEW_USER, (profile_id, first_name, last_name, email,password, phone, house_type, current_pets, kids_under_ten, pet_insurance, seeking,account_type, matches_id))


def get_all_users(connection):
    with connection:
        return connection.execute(GET_ALL_USERS).fetchall()


def remove_user(connection, user_id):
    return connection.execute(REMOVE_USER, (user_id,))

#----------------------------------------------------------------------------------------#
# insert new shelter into table
def add_shelter(connection,profile_id,shelter_name,shelter_email,shelter_password, shelter_address, account_type, about, link):
    with connection:
        return connection.execute(ADD_NEW_SHELTER, (profile_id,shelter_name,shelter_email, shelter_password,  shelter_address, account_type, about, link))


def get_all_shelters(connection):
    with connection:
        return connection.execute(GET_ALL_SHELTERS).fetchall()


def remove_shelter(connection, shelter_id):
    return connection.execute(REMOVE_SHELTER, (shelter_id,))

#----------------------------------------------------------------------------------------#
# insert new admin into table
def add_admin(connection, profile_id):
    with connection:
        return connection.execute(ADD_NEW_ADMIN, (profile_id,))


def get_all_admins(connection):
    with connection:
        return connection.execute(GET_ALL_ADMINS).fetchall()


def remove_admin(connection, admin_id):
    return connection.execute(REMOVE_ADMIN, (admin_id,))

#----------------------------------------------------------------------------------------#
# insert new pet into table
def add_pet(connection, shelter_id, pet_name, pet_species, pet_breed, pet_color, pet_likes, pet_dislikes,pet_age, pet_gender, pet_health, pet_photo, pet_good_with_other_animals, pet_good_with_children, pet_size, adoption_status, matches_id):
    with connection:
        return connection.execute(ADD_NEW_PET, (shelter_id, pet_name, pet_species, pet_breed, pet_color, pet_likes, pet_dislikes, pet_age, pet_gender, pet_health, pet_photo, pet_good_with_other_animals, pet_good_with_children, pet_size,adoption_status, matches_id))


def get_all_pets(connection):
    with connection:
        return connection.execute(GET_ALL_PETS).fetchall()
    
def get_pet_image(connection, pet_id):
    with connection:
        return connection.execute(GET_PET_IMAGE, (pet_id,))

def get_pet_count(connection):
    with connection:
        return connection.execute(GET_PET_COUNT)

def remove_pet(connection, pet_id):
    return connection.execute(REMOVE_PET, (pet_id,))
#----------------------------------------------------------------------------------------#
def add_like(connection, user_id, pet_id):
    with connection:
        return connection.execute(ADD_NEW_LIKE, (user_id, pet_id,))
    
def get_userid_email(connection, email):
    with connection:
        return connection.execute(GET_USER_ID_BY_EMAIL,(email,)).fetchone()

def get_shelterid_email(connection, email):
    with connection:
        return connection.execute(GET_SHELTER_ID_BY_EMAIL,(email,)).fetchone()

def get_all_likes(connection):
    with connection:
        return connection.execute(GET_ALL_LIKES).fetchall()

def get_likes_with_petid(connection, pet_id):
    with connection:
        return connection.execute(GET_LIKES_WITH_PET_ID,(pet_id,)).fetchall()

def get_likes_with_userid(connection, user_id):
    with connection:
        return connection.execute(GET_LIKES_WITH_USER_ID,(user_id,)).fetchall()

def get_petid_with_shelterid(connection, shelter_id):
    with connection:
        return connection.execute(GET_PETID_WITH_SHELTERID,(shelter_id,)).fetchall()
    
def like_join(connection, shelter_id):
    with connection:
        return connection.execute(LIKE_TABLE_JOIN,(shelter_id,)).fetchall()
    
def update_adoption_status_pending(connection, status, pet_id):
    with connection:
        return connection.execute(UPDATE_PET_STATUS,(status,pet_id))


def add_new_match(connection, user_id, pet_id, shelter_id, match_time):
    with connection:
        return connection.execute(ADD_NEW_MATCH,(user_id,pet_id,shelter_id,match_time))
    
def get_all_matches(connection):
    with connection:
        return connection.execute(GET_ALL_MATCHES).fetchall()
    

def check_match_exists(connection, user_id, pet_id, shelter_id):
    with connection:
        return connection.execute(CHECK_MATCH_EXISTS,(user_id,pet_id,shelter_id)).fetchone()

def check_like_exists(connection, user_id, pet_id):
    with connection:
        return connection.execute(CHECK_LIKE_EXISTS,(user_id,pet_id)).fetchone()
    
def update_adoption_status_available(connection, status, pet_id):
    with connection:
        return connection.execute(UPDATE_PET_STATUS,(status,pet_id))
    
def remove_match(connection, match_id):
    with connection:
        return connection.execute(REMOVE_MATCH,(match_id,))
    
def get_matchid(connection, pet_id,shelter_id,user_id):
    with connection:
        return connection.execute(GET_MATCHID,(pet_id,shelter_id,user_id)).fetchone()
    
def pet_matches(connection, pet_id):
    with connection:
        return connection.execute(CHECK_PET_MATCHES,(pet_id,)).fetchone()
    
def remove_likes_petid(connection,pet_id):
    with connection:
        return connection.execute(DELETE_LIKES_AT_PETID,(pet_id,))
    
def get_unique_likes_with_userid(connection, user_id):
    with connection:
        return connection.execute(PET_FROM_LIKES,(user_id,)).fetchall()
    
def user_like_join(connection, user_id):
    with connection:
        return connection.execute(USER_UNIQUE_LIKES_JOIN,(user_id,)).fetchall()

def user_match_join(connection, user_id):
    with connection:
        return connection.execute(USER_UNIQUE_MATCHES_JOIN,(user_id,)).fetchall()
    
def get_pets_by_shelter(connection, shelter_id):
    with connection:
        return connection.execute(SHELTER_PETS,(shelter_id,)).fetchall()

def get_user_with_id(connection, user_id):
    with connection:
        return connection.execute(USER_FROM_ID,(user_id,)).fetchone()