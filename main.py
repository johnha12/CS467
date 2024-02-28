from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from dotenv import load_dotenv
import os
import database, requests
import boto3
from bs4 import BeautifulSoup
from form_flask_select import simpleForm
from form_new_shelter import newShelterForm
from form_new_user  import newUserForm
from flask_wtf import Form
#from wtforms.fields.html5 import URLField
from wtforms.validators import InputRequired

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id= os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket_name = os.getenv('AWS_BUCKET_NAME')
print(bucket_name)
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

# Define an empty list to store user information WILL be replaced by database
users = []
users.append({'email': 'shelter@oregonstate.edu', 'password': '111111', 'account_type': 'shelter'})
users.append({'email': 'user@oregonstate.edu', 'password': '111111', 'account_type': 'user'})

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
        # Check shelter  table
        cursor.execute("SELECT * FROM shelters WHERE shelter_name=? AND shelter_address=?", (email, password))
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

        return jsonify({'redirect_url': '/shelter_profile'})
    else:
        print("Invalid username or password")
    return jsonify({'error': 'Invalid email or password. Please try again.', 'redirect_url': '/'})
    
@app.route('/sign_out')
def sign_out():
    session.pop('email', None)
    session.pop("account_type", None)
    return redirect(url_for('home'))

@app.route('/welcome')
def welcome():
    if 'email' in session and session["account_type"] == "user":
        return render_template('welcome.html', article_list=articles)
    return render_template('home.html' )

@app.route('/shelter_add_pet')
def shelter_add_pet():
    if 'email' in session and session["account_type"] == "shelter":
        return render_template('shelter_add_pet.html')
    return render_template('home.html' )

# Adding pet function
@app.route('/add_pet', methods=['POST'])
def add_pet():
    if request.method == 'POST':
        # Retrieve form data
        pet_name = request.form['petName']
        breed = request.form['breed']
        animal_type = request.form['animalType']
        gender = request.form['gender']
        fixed = request.form['fixed']
        availability = request.form['availability']
        good_with_other_animals = request.form.get('goodWithOtherAnimals', False)
        good_with_children = request.form.get('goodWithChildren', False)
        animal_must_be_leashed = request.form.get('animalMustBeLeashedAtAllTimes', False)
        # Process the form data (you can perform database operations here)

        # Redirect to a different page after processing the form data
        return redirect('/shelter_add_pet')

@app.route('/shelter_all_adopters')
def shelter_all_adopters():
    if 'email' in session and session["account_type"] == "shelter":
        return render_template('shelter_all_adopters.html')
    return render_template('home.html' )

@app.route('/shelter_all_pets')
def shelter_all_pets():
    if 'email' in session and session["account_type"] == "shelter":
        return render_template('shelter_all_pets.html', pets=pets)
    return render_template('home.html' )

@app.route('/shelter_profile', methods=['GET', 'POST'])
def shelter_profile():
    if 'email' in session and session["account_type"] == "shelter":
        # remove spaces from address to insert into google maps api
        def remove_spaces(addr):
            return addr.replace(' ','')
        stripped_addr = remove_spaces(shelter_info['address'])

        return render_template('shelter_profile.html', shelter_info=shelter_info, maps_api_address=stripped_addr)
    return render_template('home.html' )

@app.route('/shelter_profile_edit', methods=['GET', 'POST'])
def shelter_profile_edit():
    if 'email' in session and session["account_type"] == "shelter":
        # Only accessible from shelter profile button
        if request.method == 'GET':
            return render_template('shelter_profile_edit.html', shelter_info=shelter_info)
        elif request.method == 'POST':
            new_name = request.form['new_name']
            new_description = request.form['new_description']
            new_address = request.form['new_address']
            new_link = request.form['new_link']

            # Check if the form fields are not empty before updating shelter_info
            if new_name:
                shelter_info['name'] = new_name
            if new_description:
                shelter_info['description'] = new_description
            if new_address:
                shelter_info['address'] = new_address
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
        return render_template('shelter_single_adopter.html')
    return render_template('home.html' )
    

@app.route('/shelter_single_pet')
def shelter_single_pet():
    if 'email' in session and session["account_type"] == "shelter":
        return render_template('shelter_single_pet.html')
    return render_template('home.html' )
    

@app.route('/shelter')
def shelter():
    if 'email' in session and session["account_type"] == "shelter":
        return render_template('shelter.html')
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

@app.route('/likeDislike_profile')
def likeDislike_profile():
    if 'email' in session:
        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key':pet_info[pet_id][11]}, ExpiresIn=3600)
        return render_template('likeDislike.html', image_url = signed_url, pet_info = pet_info, pet_id = pet_id, pet_type = pet_type)
    return render_template('home.html' )

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
        return render_template('new_shelter_handler.html', title="New Shelter Form Handler", header="New Shelter Form Handler", result=result)
    return render_template('new_shelter.html', title = "New Shelter", header="Simple New Shelter Form", form=form)

# route for user to view matches
@app.route('/user_matches')
def userMatch():
    if "email" in session and session["account_type"] == "user":
        return render_template('user_matches.html')
    return render_template('home.html' )

# route for user to view matches
@app.route('/user_profile')
def user_profile():
    if "email" in session and session["account_type"] == "user":
        return render_template('user_profile.html')
    return render_template('home.html' )

# route for user to view matches
@app.route('/user_liked_pets')
def user_liked_pets():
    if "email" in session and session["account_type"] == "user":
        return render_template('user_liked_pets.html')
    return render_template('home.html' )
    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
