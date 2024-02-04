from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, SelectField, PasswordField, ValidationError
from wtforms.validators import InputRequired, Length, EqualTo

class simpleForm(FlaskForm):
    firstName=StringField("First Name", validators=[InputRequired(), Length(min=2, max=30)])
    lastName=StringField("Last Name", validators=[InputRequired(), Length(min=2, max=30)])
    email=StringField("Email Adress", validators=[InputRequired(), Length(min=5, max=30)])
    phone=StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=12)])

    password= PasswordField("Account Password (Must be 6-16 characters)", validators=[InputRequired(), Length(min=6, max=16)])
    checkPassword = PasswordField("Confirm password", validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    #Password validation error message still not displaying with password mismatch

    housingType = SelectField(u'Type of house', 
        choices=[('apartment', 'Apartment or Condo'), ('smallYard', 'Home with small yard'), ('largeYard', 'Home with large yard')])
    
    pets = SelectField(u'Any current pets?', choices=[('yes', 'Yes, at least one other pet'), ('no', 'No other pets')])
        
    kids = SelectField(u'Any children under the age of 10 years old? ', 
        choices=[('yes', 'Yes, at least one child under 10yrs'), ('no', 'No children under 10yrs')])

    insurance = SelectField(u'Do you have/plan to have pet insurance?', 
        choices=[('yes', 'Yes, I have pet insurance'), ('no', 'No I do not have pet insurance')])

    petHistory = SelectField(u'Have you had pets previously?', 
        choices=[('yes', 'Yes, I have had pets before'), ('no', 'No, I have never had a pet before')])

    goalPet = SelectField(u'Are you looking for a Dog, Cat, Other, or all the above?', 
        choices=[('dog', 'Looking for a Dog'), ('cat', 'Looking for a cat'),
            ('other', 'Looking for something else (not dog/cat)'), ('all', 'Looking for any kind of pet')])

    income = StringField("OPTIONAL Income")

    submit = SubmitField("Create Account")



class loginForm(FlaskForm):
    email=StringField("Email Adress", validators=[InputRequired(), Length(min=5, max=30)])
    
    password= PasswordField("Password", validators=[InputRequired(), Length(min=6, max=16)])
    
    submit = SubmitField("Login to Account")

