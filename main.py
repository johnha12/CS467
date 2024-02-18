from flask import Flask, render_template, request, redirect, jsonify
import database, requests
from bs4 import BeautifulSoup
from form_flask_select import simpleForm
from form_new_shelter import newShelterForm
from form_new_user  import newUserForm
from flask_wtf import Form
#from wtforms.fields.html5 import URLField
from wtforms.validators import InputRequired

app = Flask(__name__)

# Pet Info list for current swipe functionality - Evan Riffle
# Temporary for testing until database is set up
connection = database.connect()
database.create_tables(connection)

pet_id = 0

pet_type = 'all'

pet_info = database.get_all_pets(connection)

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
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if the user exists and the password is correct
    for user in users:
        if user['email'] == email and user['password'] == password:
            # Redirect based on the account type
            if user['account_type'] == 'user':
                return jsonify({'redirect_url': '/welcome'})  # Redirect to user dashboard
            elif user['account_type'] == 'shelter':
                return jsonify({'redirect_url': '/shelter'})  # Redirect to shelter dashboard

    # If login fails, return an error message and the home page URL
    return jsonify({'error': 'Invalid email or password. Please try again.', 'redirect_url': '/'})

@app.route('/welcome')
def welcome():
    return render_template('welcome.html', article_list=articles)

@app.route('/shelter_add_pet')
def shelter_add_pet():
    return render_template('shelter_add_pet.html')

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
    return render_template('shelter_all_adopters.html')

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

@app.route('/shelter_all_pets')
def shelter_all_pets():
    return render_template('shelter_all_pets.html', pets=pets)

# Hardcoded shelter information, will replace later. (ex. name = request.args.get('name'))
shelter_info = {
    'name': 'Oregon Humane Society',
    'description': 'Description of your shelter',
    # Need to figure out how to add photos
    'address': '1067 NE Columbia Blvd, Portland, OR 97211',
    'link': 'https://www.oregonhumane.org',
}

@app.route('/shelter_profile', methods=['GET', 'POST'])
def shelter_profile():
    # remove spaces from address to insert into google maps api
    def remove_spaces(addr):
        return addr.replace(' ','')
    stripped_addr = remove_spaces(shelter_info['address'])

    return render_template('shelter_profile.html', shelter_info=shelter_info, maps_api_address=stripped_addr) 

@app.route('/shelter_profile_edit', methods=['GET', 'POST'])
def shelter_profile_edit():
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

@app.route('/shelter_signup')
def shelter_signup():
    return render_template('shelter_signup.html')

@app.route('/shelter_single_adopter')
def shelter_single_adopter():
    return render_template('shelter_single_adopter.html')

@app.route('/shelter_single_pet')
def shelter_single_pet():
    return render_template('shelter_single_pet.html')

@app.route('/shelter')
def shelter():
    return render_template('shelter.html')

@app.route('/likeDislike')
def swipe():
    return render_template('likeDislike.html', image = pet_info[pet_id][11], pet_info = pet_info, pet_id = pet_id)

# Love Pet Function for Swipe Functionality - Evan Riffle
@app.route('/lovePet', methods=['POST'])
def lovePet():
    global pet_id
    pet_id = (pet_id + 1) % len(pet_info)
    return render_template('likeDislike.html', image = pet_info[pet_id][11], pet_info = pet_info, pet_id = pet_id)

# Pass Pet Function for Swipe Functionality - Evan Riffle
@app.route('/passPet', methods=['POST'])
def passPet():
    global pet_id
    pet_id = (pet_id + 1) % len(pet_info)
    return render_template('likeDislike.html', image = pet_info[pet_id][11], pet_info = pet_info, pet_id = pet_id)

#Still having issues getting filter to work currently. Needs more work this next week.
@app.route('/filter', methods=['POST'])
def filter():
    selected_pet_type = request.form.get('filterInput')
    global pet_type
    pet_type = selected_pet_type
    return render_template('likeDislike.html', image = pet_info[pet_id][11], pet_info = pet_info, pet_id = pet_id)

@app.route('/likeDislike_profile')
def likeDislike_profile():
    return render_template('likeDislike_profile.html', image = pet_info[pet_id][11], pet_info = pet_info, pet_id = pet_id)

#   Secret key is needed for flask
app.config["SECRET_KEY"]='why_a_dog?'
# Define an empty list to store user information
users = []
users.append({'email': 'shelter@oregonstate.edu', 'password': '111111', 'account_type': 'shelter'})

@app.route('/new_user_form', methods=['POST', 'GET'])
def new_user_form():

    form = newUserForm()

    if form.validate_on_submit() and request.method == 'POST':

        # Can add that only take unquie email

        # Extract email and password from the form submission
        email = request.form['email']
        password = request.form['password']
        
        # Append the email and password to the users list
        users.append({'email': email, 'password': password, 'account_type': 'user'})
        
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
