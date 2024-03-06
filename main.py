from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from dotenv import load_dotenv
import os
import database, requests, random
import boto3
from bs4 import BeautifulSoup
from form_new_shelter import newShelterForm
from form_new_user  import newUserForm
from get_db_info import get_user_info, get_shelter_info

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id= os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket_name = os.getenv('AWS_BUCKET_NAME')
folder_name = os.getenv('FOLDER_NAME')

app = Flask(__name__)

# Database connection - check_same_thread set to false
connection = database.sqlite3.connect('data.db', check_same_thread=False)
database.create_tables(connection)

# globals for swipe page
pet_id = 0

pet_type = 'all'

pet_info = database.get_all_pets(connection)

user_id = None

shelter_id = None

#   Secret key is needed for flask
app.config["SECRET_KEY"]='why_a_dog?'
###########################################

# Hardcoded variables for now
pets = [
    {
        'name': 'Sparky',
        'breed': 'Labrador Retriever',
        'animal_type': 'Dog',
        'gender': 'Male',
        'fixed_status': 'Fixed',
        'availability': 'Available',
        'disposition': 'Good with other animals, Good with children',
        'view_status': 'Public',
        'image': 'Belle1.jpg'  # Assuming this is the filename of the pet image
    },
    {
        'name': 'Whiskers',
        'breed': 'Siamese',
        'animal_type': 'Cat',
        'gender': 'Female',
        'fixed_status': 'Not Fixed',
        'availability': 'Pending',
        'disposition': 'Good with children',
        'view_status': 'Private',
        'image': 'Belle2.jpg'  # Assuming this is the filename of the pet image
    },
    {
        'name': 'Rocky',
        'breed': 'Mixed Breed',
        'animal_type': 'Dog',
        'gender': 'Male',
        'fixed_status': 'Fixed',
        'availability': 'Adopted',
        'disposition': 'Animal must be leashed at all times',
        'view_status': 'Public',
        'image': 'Belle3.jpg'  # Assuming this is the filename of the pet image
    }
]

# Hardcoded shelter information, will replace later. (ex. name = request.args.get('name'))
shelter_info = {
    'name': 'Oregon Humane Society',
    'description': 'Description of your shelter',
    # Need to figure out how to add photos
    'address': '1067 NE Columbia Blvd, Portland, OR 97211',
    'link': 'https://www.oregonhumane.org',
}
###########################################

###########################################
# news scraper

url = 'https://www.humanesociety.org/news'

def getdata(url):
    r = requests.get(url)
    return r.text

htmldata = getdata(url)
soup = BeautifulSoup(htmldata, 'html.parser')

class Article:
    def __init__(self, title, description, link):
        self.title = title
        self.description = description
        self.link = link
articles = []

# find all article titles, which are under anchors for this site
anchor = soup.find_all('a', attrs={'hreflang':'en'})
# fidn all article descriptions
summary = soup.find_all('div', attrs={'class':'field--name-body'})
for (entry, attr) in enumerate(anchor):
    articles.append(Article(
        attr.contents[0], 
        summary[entry].contents[1].contents[0],
        'https://www.humanesociety.org'+attr['href']))
    
###########################################


@app.route('/')
def home():
    return render_template('home.html' )

@app.route('/login', methods=['POST'])
def login():
    # Getting the info from the user
    email = request.form.get('email')
    password = request.form.get('password')
    account_type = "user" #user by default unless flipped

    #   connecting to the databse
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    if not user:
        # Check shelter table **place holder for shelter table that does not have email/password uses name of shelter and address instead**
        #cursor.execute("SELECT * FROM shelters WHERE shelter_name=? AND shelter_address=?", (email, password))
        # Check shelter table 
        cursor.execute("SELECT * FROM shelters WHERE shelter_email=? AND shelter_password=?", (email, password))
        user = cursor.fetchone()
        account_type = "shelter"
    conn.close()
    if user and account_type == "user":
        session['logged_in'] = True
        session['first_name'] = user[2]  # Assuming username is the 3rd column in the table
        session['last_Name'] = user[3] 
        #session['email'] = user[4]  # Assuming email is the 5th column in the table
        session['email'] = email    # Or just take the entered email from user and fill in the session info
        session['account_type'] = user[12]  # Assuming account type is the 13 column in the table 

        global user_id

        # get user_id from database after login is validated
        user_id = database.get_userid_email(connection, email)
        user_id = user_id[0]

        return jsonify({'redirect_url': '/welcome'})
    if user and account_type == "shelter": # Note, shelter table does not have password or email field atm 
        session['logged_in'] = True
        session['username'] = user[2]  # Assuming shelter_name is the 3rd column in the table
        #session['email'] = user[4]  # Assuming email is the 5th column in the table
        session['email'] = email    # Or just take the entered email from user and fill in the session info
        session['account_type'] = account_type  #hard coding this for now
        
        global shelter_id
        shelter_id = database.get_shelterid_email(connection, email)
        shelter_id = shelter_id[0]

        return jsonify({'redirect_url': '/shelter'})
    else:
        print("Invalid username or password")
    return jsonify({'error': 'Invalid email or password. Please try again.', 'redirect_url': '/'})
    
@app.route('/sign_out') #   Clear ALL session info
def sign_out():
    session.pop('email', None)
    session.pop("account_type", None)
    session.pop("username", None)
    session.pop("first_name", None)
    session.pop("last_name", None)
    session.pop("logged_in", None)
    return redirect(url_for('home'))

@app.route('/welcome')
def welcome():
    if 'email' in session and session["account_type"] == "user":
        poss_pet_ids = list(range(1, len(pet_info)))
        rand_pet_id_list = random.sample(poss_pet_ids, 3)

        pet_url_list = []
        for id in rand_pet_id_list:
            signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key':pet_info[id][11]}, ExpiresIn=3600)
            pet_url_list.append({'pet_id': id, 'img_url': signed_url})

        return render_template('welcome.html', article_list=articles, image_urls=pet_url_list)
    elif 'email' in session: #user is logged in on differnet account type redirect to home page
        return render_template('shelter.html')
    return render_template('home.html' )



@app.route('/shelter_add_pet')
def shelter_add_pet():
    if 'email' in session and session["account_type"] == "shelter":
        shelter_name = get_shelter_info("shelter_name")
        return render_template('shelter_add_pet.html', shelter_name=shelter_name)
    return render_template('home.html' )

# Adding pet function
@app.route('/add_pet', methods=['POST'])
def add_pet():
    if request.method == 'POST':
        global shelter_id
        # Retrieve form data
        pet_name = request.form['petName']
        breed = request.form['breed']
        animal_type = request.form['animalType']
        color = request.form['color']
        likes = request.form['likes']
        dislikes = request.form['dislikes']
        age = request.form['size']
        size = request.form['age']
        gender = request.form['gender']
        fixed = request.form['fixed']
        availability = request.form['availability']
        good_with_other_animals = request.form.get('goodWithOtherAnimals', False)
        good_with_children = request.form.get('goodWithChildren', False)
        animal_must_be_leashed = request.form.get('animalMustBeLeashedAtAllTimes', False)

        # Grab image and setup for bucket upload and key creation
        picture = request.files['picture1']
        filename = picture.filename
        key = f"{folder_name}/{filename}"

        # Upload image to amazon s3 bucket
        s3.upload_fileobj(picture,bucket_name,f"{folder_name}/{filename}")

        # Process the form data (you can perform database operations here)
        database.add_pet(connection,shelter_id,pet_name,animal_type,breed,color,likes,dislikes,age,gender,fixed,key,good_with_other_animals,good_with_children,size,availability,0)
        connection.commit()

        global pet_info
        pet_info = database.get_all_pets(connection)
        # Redirect to a different page after processing the form data
        return redirect('/shelter_add_pet')

@app.route('/shelter_all_adopters')
def shelter_all_adopters():
    if 'email' in session and session["account_type"] == "shelter":
        shelter_name = get_shelter_info("shelter_name")
        global shelter_id
        print(shelter_id)
        users = database.like_join(connection,shelter_id)
        return render_template('shelter_all_adopters.html', shelter_name=shelter_name, users=users)
    if 'email' in session: #user is logged in on differnet account type redirect to home page
        return render_template('welcome.html', article_list=articles)
    return render_template('home.html' )

@app.route('/shelter_all_pets')
def shelter_all_pets():
    if 'email' in session and session["account_type"] == "shelter":
        shelter_name = get_shelter_info("shelter_name")
        return render_template('shelter_all_pets.html', shelter_name=shelter_name, pets=pets)
    if 'email' in session: #user is logged in on differnet account type redirect to home page
        return render_template('welcome.html', article_list=articles)
    return render_template('home.html' )

@app.route('/shelter_profile', methods=['GET', 'POST'])
def shelter_profile():
    if 'email' in session and session["account_type"] == "shelter":
        shelter_name = get_shelter_info("shelter_name")
        addr = get_shelter_info("shelter_address")
        return render_template('shelter_profile.html', shelter_name=shelter_name, shelter_addr=addr, shelter_info=shelter_info)
    if 'email' in session: #user is logged in on differnet account type redirect to home page
        return render_template('welcome.html', article_list=articles)
    return render_template('home.html' )

@app.route('/shelter_profile_edit', methods=['GET', 'POST'])
def shelter_profile_edit():
    if 'email' in session:
        # Only accessible from shelter profile button
        if request.method == 'GET':
            shelter_name = get_shelter_info("shelter_name")
            addr = get_shelter_info("shelter_address")
            return render_template('shelter_profile_edit.html', shelter_name=shelter_name, shelter_addr=addr, shelter_info=shelter_info)
        elif request.method == 'POST':
            new_name = request.form['new_name']
            new_description = request.form['new_description']
            new_address = request.form['new_address']
            new_link = request.form['new_link']

            # Check if the form fields are not empty before updating shelter_info
            if new_name:
                shelter_info['name'] = new_name
                conn = database.connect()
                cursor = conn.cursor()
                # Update the attribute in the database
                cursor.execute("UPDATE shelters SET shelter_name = ? WHERE shelter_email = ?", (new_name, session['email']))
                conn.commit()
                conn.close()

                conn = database.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT shelter_name FROM shelters WHERE shelter_email=?", (session['email'],))
                session['username'] = cursor.fetchone()
                conn.close()

            if new_description:
                shelter_info['description'] = new_description
            if new_address:
                shelter_info['address'] = new_address
                conn = database.connect()
                cursor = conn.cursor()
                # Update the attribute in the database
                cursor.execute("UPDATE shelters SET shelter_address = ? WHERE shelter_email = ?", (new_address, session['email']))
                conn.commit()
                conn.close()
            if new_link:
                shelter_info['link'] = new_link
            
            # Now need to process data and redirect
            

            return redirect('shelter_profile')

    return render_template('home.html' )    

@app.route('/shelter_signup')
def shelter_signup():
    return render_template('shelter_signup.html')

@app.route('/shelter_single_adopter')
def shelter_single_adopter():
    if 'email' in session and session["account_type"] == "shelter":
        shelter_name = get_shelter_info("shelter_name")
        return render_template('shelter_single_adopter.html', shelter_name=shelter_name)
    if 'email' in session: #user is logged in on differnet account type redirect to home page
        return render_template('welcome.html', article_list=articles)
    return render_template('home.html' )
    

@app.route('/shelter_single_pet')
def shelter_single_pet():
    if 'email' in session and session["account_type"] == "shelter":
        shelter_name = get_shelter_info("shelter_name")
        return render_template('shelter_single_pet.html', shelter_name=shelter_name)
    if 'email' in session: #user is logged in on differnet account type redirect to home page
        return render_template('welcome.html', article_list=articles)
    return render_template('home.html' )

@app.route('/shelter')
def shelter():
    if 'email' in session and session["account_type"] == "shelter":
        shelter_name = get_shelter_info("shelter_name")
        return render_template('shelter.html', shelter_name = shelter_name)
    if 'email' in session: #user is logged in on differnet account type redirect to home page
        return render_template('welcome.html', article_list=articles)
    return render_template('home.html' )
    

@app.route('/likeDislike')
def swipe():
    if 'email' in session:
        global pet_id
        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key':pet_info[pet_id][11]}, ExpiresIn=3600)
        return render_template('likeDislike.html', image_url = signed_url, pet_info = pet_info, pet_id = pet_id, pet_type = pet_type)
    return render_template('home.html' )
    

# Love Pet Function for Swipe Functionality - Evan Riffle
@app.route('/lovePet', methods=['POST'])
def lovePet():

    if 'email' in session:
        global pet_type
        global pet_id
        global user_id

        if pet_type != 'all':
            while True:
                pet_id = (pet_id + 1) % len(pet_info)
                if pet_info[pet_id][3] == pet_type:
                    break
        else:
            pet_id = (pet_id + 1) % len(pet_info)
            
        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key':pet_info[pet_id][11]}, ExpiresIn=3600)
        
        # Track liked pets in database like table. Tracks via user_id and pet_id
        like_check = database.check_match_exists(connection,user_id,pet_id,shelter_id)
        if like_check[0] == 0:
            database.add_like(connection,user_id,pet_id)
            connection.commit()
        
        return render_template('likeDislike.html', image_url = signed_url, pet_info = pet_info, pet_id = pet_id, pet_type = pet_type)
    return render_template('home.html' )

    

# Pass Pet Function for Swipe Functionality - Evan Riffle
@app.route('/passPet', methods=['POST'])
def passPet():

    if 'email' in session:
        global pet_type
        global pet_id
        if pet_type != 'all':
            while True:
                pet_id = (pet_id + 1) % len(pet_info)
                if pet_info[pet_id][3] == pet_type:
                    break
        else:
            pet_id = (pet_id + 1) % len(pet_info)

        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key':pet_info[pet_id][11]}, ExpiresIn=3600)
        return render_template('likeDislike.html', image_url = signed_url, pet_info = pet_info, pet_id = pet_id, pet_type = pet_type)
    return render_template('home.html' )

    

#Still having issues getting filter to work currently. Needs more work this next week.
@app.route('/filter', methods=['POST'])
def filter():
    if 'email' in session:
        selected_pet_type = request.form['pet_type']
        global pet_type
        pet_type = selected_pet_type

        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key':pet_info[pet_id][11]}, ExpiresIn=3600)
        return render_template('likeDislike.html', image_url = signed_url, pet_info = pet_info, pet_id = pet_id, pet_type = pet_type)
    return render_template('home.html' )

@app.route('/likeDislike_profile/<int:pet_id>')
def likeDislike_profile(pet_id):
    if 'email' in session:
        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key':pet_info[pet_id][11]}, ExpiresIn=3600)
        
        # remove spaces from address to insert into google maps api
        stripped_addr=shelter_info['address'].replace(' ','')
        
        return render_template('likeDislike_profile.html', image_url = signed_url, pet_info = pet_info, pet_id = pet_id, pet_type = pet_type, maps_api_address=stripped_addr)
    return render_template('home.html' )

def is_email_available(email):
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT shelter_name FROM shelters WHERE shelter_email=?", (email,))
    taken = cursor.fetchone()  # Fetch one row
    conn.close()
    # if taken is None, need to check user table.
    if (taken is None):
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT first_name FROM users WHERE email=?", (email,))
        taken = cursor.fetchone()  # Fetch one row
        conn.close()
    # if is_email_avaiable is false, then the email is taken
    # if is_email_avaiable is true, then email is available
    return (taken is None)

@app.route('/new_user_form', methods=['POST', 'GET'])
def new_user_form():

    form = newUserForm()

    if form.validate_on_submit() and request.method == 'POST':

        # Can add that only take unquie email

        # Extract email and password from the form submission
        profile_id = 0 # Hard codeded
        first_name = request.form['first_name']
        last_name= request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        house_type = request.form['house_type']
        seeking = request.form['seeking']
        matches_id = 0
        password = request.form['password']
        current_pets = request.form['current_pets']
        kids_under_ten = request.form['kids_under_10']
        pet_insurance = request.form['pet_insurance']
        account_type = 'user'
        

        connection = database.connect()

        # need to check if email is taken
        if (not is_email_available(email)):
            print("Email is already taken. Try again")
            return render_template('new_user_form.html', title = "New User", header="Simple New User Form", form=form)

        database.add_user(connection, profile_id, first_name, last_name, email, password, phone, house_type, current_pets, kids_under_ten, pet_insurance, seeking, account_type, matches_id)
        
        # Redirect to a success page or display a success message
        result = request.form
        return render_template('new_user_form_handler.html', title="New User Form Handler", header="New User Form Handler", result=result)
    return render_template('new_user_form.html', title = "New User", header="Simple New User Form", form=form)

# testing route for new shelter form
@app.route('/new_shelter_form', methods=['POST', 'GET'])
def new_shelter_form():
    form = newShelterForm()
    if  form.validate_on_submit():
        result = request.form

        connection = database.connect()
        profile_id = 0
        shelter_name = request.form['shelter_name']
        shelter_email = request.form['shelter_email']
        shelter_password = request.form['checkPassword']
        shelter_address = request.form['shelter_address']
        account_type = 'shelter'

        if (not is_email_available(shelter_email)):
            print("Email is already taken. Try again")
            return render_template('new_user_form.html', title = "New User", header="Simple New User Form", form=form)

        database.add_shelter(connection,profile_id,shelter_name,shelter_email,shelter_password, shelter_address, account_type)

        return render_template('new_shelter_handler.html', title="New Shelter Form Handler", header="New Shelter Form Handler", result=result)
    return render_template('new_shelter.html', title = "New Shelter", header="Simple New Shelter Form", form=form)

# route for user to view matches
@app.route('/user_matches')
def userMatch():
    if "email" in session and session["account_type"] == "user":
        return render_template('user_matches.html')
    elif "email" in session and session["account_type"] == "shelter":
        return render_template('shelter.html')
    else:
        return render_template('home.html' )

# route for user to view matches
@app.route('/user_profile')
def user_profile():
    if "email" in session and session["account_type"] == "user":
        user_phone = get_user_info("phone")
        pref = get_user_info("seeking")
        return render_template('user_profile.html', phone=user_phone, pet_pref=pref)
    elif "email" in session and session["account_type"] == "shelter":
        return render_template('shelter.html')
    else:
        return render_template('home.html' )

# route for user to view matches
@app.route('/user_liked_pets')
def user_liked_pets():
    if "email" in session and session["account_type"] == "user":
        return render_template('user_liked_pets.html')
    elif "email" in session and session["account_type"] == "shelter":
        return render_template('shelter.html')
    else:
        return render_template('home.html' )

# route to update pet status to pending and contact adopter
@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        global shelter_id
        userid = request.form['user_info']

        match_check = database.check_match_exists(connection,int(userid[0]),int(userid[3]),shelter_id)
        
        
        # update pet_status to pending
        database.update_adoption_status_pending(connection,'pending',int(userid[3]))
        connection.commit()

        # add pet and user to matches table
        if match_check[0] == 0:
            database.add_new_match(connection,int(userid[0]),int(userid[3]),shelter_id,0)
            connection.commit()

        return redirect('/shelter_profile')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
