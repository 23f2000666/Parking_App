from wtforms.validators import DataRequired, NumberRange
from wtforms import StringField, SubmitField, IntegerField, FloatField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class ParkingLotForm(FlaskForm):
    name = StringField('Lot Name', validators=[DataRequired()])
    location = StringField('Location/Address', validators=[DataRequired()])
    capacity = IntegerField('Total Spots', validators=[DataRequired(
    ), NumberRange(min=1, message="Capacity must be at least 1.")])
    price_per_hour = FloatField('Price per Hour ($)', validators=[
                                DataRequired(), NumberRange(min=0, message="Price cannot be negative.")])
    submit = SubmitField('Create Lot')


class EmptyForm(FlaskForm):
    """An empty form used for requests that only need CSRF token protection."""
    submit = SubmitField('Submit')
