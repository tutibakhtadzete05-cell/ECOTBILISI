from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

# 1.  original Incident Reporting form
class ReportProblemForm(FlaskForm):
    location = StringField("Location / District", validators=[DataRequired()])
    description = TextAreaField("Description of Problem", validators=[DataRequired()])
    submit = SubmitField("Submit Report")

# 2.  AI Assistant form
class AskForm(FlaskForm):
    question = StringField("Ask our AI Eco-Assistant", validators=[
        DataRequired(),
        Length(max=200, message="Maximum 200 characters allowed.")
    ])
    submit = SubmitField("Send to AI")

# 3.: Registration Form
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField("Create Account")

# 4. : Login Form
class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")