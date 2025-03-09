from email_validator import validate_email
import regex as re



email = 'mark.gorenc@gmail.com'

if not validate_email(email, check_deliverability=False):
    print('Invalid email')
else:
    print('Valid email')