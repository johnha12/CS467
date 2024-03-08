from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import InputRequired, Length, EqualTo, Email

class newUserForm(FlaskForm):
    first_name=StringField("First Name", validators=[InputRequired(), Length(min=2, max=30)])
    last_name=StringField("Last Name", validators=[InputRequired(), Length(min=2, max=30)])
    email=StringField("Email Address", validators=[InputRequired(), Email()])
    phone=StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=12)])
    password= PasswordField("Account Password (Must be 6-16 characters)", validators=[InputRequired(), Length(min=6, max=16)])
    passwordCheck = PasswordField("Confirm password", validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    house_type = SelectField(u'Type of house', 
        choices=[('apartment', 'Apartment or Condo'), ('smallYard', 'Home with small yard'), ('largeYard', 'Home with large yard')])
    current_pets = SelectField(u'Any current pets?', choices=[('yes', 'Yes, at least one other pet'), ('no', 'No other pets')])      
    kids_under_10 = SelectField(u'Any children under the age of 10 years old? ', 
        choices=[('yes', 'Yes, at least one child under 10yrs'), ('no', 'No children under 10yrs')])
    pet_insurance = SelectField(u'Do you have/plan to have pet insurance?', 
        choices=[('yes', 'Yes, I have pet insurance'), ('no', 'No I do not have pet insurance')])
    pet_history = SelectField(u'Have you had pets previously?', 
        choices=[('yes', 'Yes, I have had pets before'), ('no', 'No, I have never had a pet before')])
    seeking = SelectField(u'Are you looking for a Dog, Cat, Other, or all the above?', 
        choices=[('dog', 'Looking for a Dog'), ('cat', 'Looking for a cat'),
            ('other', 'Looking for something else (not dog/cat)'), ('all', 'Looking for any kind of pet')])
    income = StringField("OPTIONAL Income")
    submit = SubmitField("Create Account")



class loginForm(FlaskForm):
    email=StringField("Email Adress", validators=[InputRequired(), Length(min=5, max=30)])
    password= PasswordField("Password", validators=[InputRequired(), Length(min=6, max=16)])
    submit = SubmitField("Login to Account")

