from flask import Flask, render_template, request, redirect


app = Flask(__name__)

# Images list for current swipe functionality - Evan Riffle
images = ['pet-01.jpg',
          'pet-02.jpg',
          'pet-03.jpg'
          ]

current_image_index = 0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

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

@app.route('/shelter_all_pets')
def shelter_all_pets():
    return render_template('shelter_all_pets.html')

# Hardcoded shelter information, will replace later. (ex. name = request.args.get('name'))
shelter_info = {
    'name': 'Your Shelter Name',
    'description': 'Description of your shelter',
    # Need to figure out how to add photos
    'address': 'Address of your shelter',
    'link': 'some link',
}

@app.route('/shelter_profile', methods=['GET', 'POST'])
def shelter_profile():
    return render_template('shelter_profile.html', shelter_info=shelter_info)

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

        # Hard coded for now.
        if shelter_info['name'] != '':
            shelter_info['name'] = new_name
        if shelter_info['description'] != '':
            shelter_info['description'] = new_description
        if shelter_info['address'] != '':
            shelter_info['address'] = new_address
        if shelter_info['link'] != '':
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
    return render_template('likeDislike.html')

@app.route('/moreInfo')
def more_info():
    return render_template('moreInfo.html')

# Love Pet Function for Swipe Functionality - Evan Riffle
@app.route('/lovePet', methods=['POST'])
def lovePet():
    global current_image_index

    current_image_index = (current_image_index + 1) % len(images)
    return render_template('likeDislike.html', image = images[current_image_index])

# Pass Pet Function for Swipe Functionality - Evan Riffle
@app.route('/passPet', methods=['POST'])
def passPet():
    global current_image_index

    current_image_index = (current_image_index + 1) % len(images)
    return render_template('likeDislike.html', image = images[current_image_index])

# Open window function for moreIno functionality - Evan Riffle
@app.route('/openWindow', methods=['POST'])
def openWindow():
    return render_template('moreInfo.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
