from flask import Flask, render_template


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

@app.route('/shelter_all_adopters')
def shelter_all_adopters():
    return render_template('shelter_all_adopters.html')

@app.route('/shelter_all_pets')
def shelter_all_pets():
    return render_template('shelter_all_pets.html')

@app.route('/shelter_profile')
def shelter_profile():
    return render_template('shelter_profile.html')

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
