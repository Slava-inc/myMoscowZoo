with open('config.txt', 'r') as f:
    data = f.read().splitlines()

TOKEN = data[0].replace('TOKEN = ', '')
EMAIL = data[1].replace('EMAIL = ', '')
EMAIL_PASSWORD = data[2].replace('EMAIL_PASSWORD = ', '')
CONTACT_EMAIL = data[3].replace('CONTACT_EMAIL = ', '')
