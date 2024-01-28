from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, SelectField

class simpleForm(FlaskForm):
    firstName=StringField("First Name")
    lastName=StringField("Last Name")
    email=StringField("Email Adress")
    phone=StringField("Phone Number")

    #first select field
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

    submit = SubmitField("Enter")

