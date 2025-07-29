from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from models import Customer

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(max=100, message='Name must be less than 100 characters')
    ])
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(max=15, message='Phone must be less than 15 characters')
    ])
    submit = SubmitField('Save Customer')
    
    def __init__(self, customer_id=None, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.customer_id = customer_id
    
    def validate_email(self, field):
        # Check if email already exists (excluding current customer if editing)
        query = Customer.query.filter_by(email=field.data)
        if self.customer_id:
            query = query.filter(Customer.id != self.customer_id)
        
        if query.first():
            raise ValidationError('Email address already exists')

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Login')

class DeleteConfirmForm(FlaskForm):
    customer_id = HiddenField('Customer ID')
    submit = SubmitField('Confirm Delete')
