from flask import Flask, render_template, jsonify, request, flash
from cryptography.fernet import Fernet
import subprocess
import requests
import os


app = Flask(__name__)

# Encryption key 
key = Fernet.generate_key()
fernet = Fernet(key)

# Setting environment variables
app.config['SECRET_KEY'] = os.urandom(24).hex()

model_prompt = "I am calculating a price for an event based on the monthly revenue, \
the price ranges from 5 to 20 euros, i am going to give you a monthly revenue and \
you will respond with a price between 5 euros and 20 euros for that person. Do not give explanation nor price \
range just answer with one number between 5 and 20 followed by the € symbol not any other words just a number between 5 to 20, this is his revenue : "

participants=[]

def get_GPT_response(Nom, Prenom, Revenu):
    participant = {'Nom_Prenom': Nom + " " + Prenom, 'Revenu': Revenu + "€"}

    encMessage = fernet.encrypt((Nom + Prenom).encode())        
    # Get the response from ChatGPT
    prompt = model_prompt + Revenu + "euros per month"


    url = "https://pli-openai-api.azurewebsites.net/gpt3/"
    headers = {"Content-Type": "application/json"}

    data = {
        "model": "plitext-davinci-003",
        "prompt": prompt,
        "temperature": 0,
        "max_tokens": 300
    }

    response = requests.post(url, headers=headers, json=data)

    gptresponse = response.json()['response']
    participants.append({'NomPrenom' : encMessage, 'Nom_Prenom': 'Participant ' + str(len(participants)), 'Revenu': Revenu + "€", 'gptresponse' : gptresponse })

    return render_template('index.html', messages = participants)


@app.route('/')
def index():
    return render_template('index.html',messages=participants)



@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        Prenom = request.form['Prenom']
        Nom = request.form['Nom']
        Revenu = request.form['Revenu']
        print(Revenu)

        if not Prenom:
            flash('Le prénom est requis')
        if not Nom:
            flash('Le nom est requis')
        elif not Revenu:
            flash('Le revenu est requis')
        elif Revenu.isdigit() == False:
            flash("Le revenu doit être un nombre")
        else:
            return get_GPT_response(Nom, Prenom, Revenu)
        
    return render_template('create.html')


@app.route('/launch-attestation')
def launch_attestation():
    command = 'sudo ./AttestationClient -o token'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()
    return render_template('launch_attestation.html', output=output)





if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 