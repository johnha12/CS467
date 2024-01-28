from form_flask_select import simpleForm

from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)

#   Secret key is needed for flask
app.config["SECRET_KEY"]='why_a_dog?'

@app.route("/")
def my_redirect():
    return redirect(url_for('simple_form'))

@app.route('/simple_form', methods=['POST', 'GET'])
def simple_form():
    form = simpleForm()
    if form.is_submitted():
        result = request.form
        return render_template('simple_form_select_handler.html', title="Simple Form Handler", header="Simple Form Handler", result=result)
    return render_template('simple_form_select.html', title = "Simple Form", header="Simple New User Form", form=form)

if __name__ == "__main__": 
    app.run(debug=True)