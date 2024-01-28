from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/shelter_add_pet')
def shelter_add_pet():
    return render_template('shelter_add_pet.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)