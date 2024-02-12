from flask_wtf import FlaskForm
import email_validator
from wtforms import StringField, SubmitField, SelectField, PasswordField, ValidationError
from wtforms.validators import InputRequired, Length, EqualTo, Email

class newShelterForm(FlaskForm):
    shelter_name=StringField("Shelter Name", validators=[InputRequired(), Length(min=2, max=30)])
    shelter_address=StringField("Address of shelter", validators=[InputRequired(), Length(min=2, max=30)])
    shelter_email=StringField("Email Adress", validators=[InputRequired(), Email()])
    shelter_phone=StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=12)])

    password= PasswordField("Account Password (Must be 6-16 characters)", validators=[InputRequired(), Length(min=6, max=16)])
    checkPassword = PasswordField("Confirm password", validators=[InputRequired(), EqualTo('password')])

    submit = SubmitField("Create Account")



