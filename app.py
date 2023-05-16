from flask import Flask, render_template, jsonify, request, flash
from cryptography.fernet import Fernet
import stat
import subprocess
import requests
import os
import string



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



@app.route('/attestation/')
def attestation():
    filename = "./verbose-report"
    # make sure the file is executable
    if not os.access(filename, os.X_OK):
        # make it executable if it's not
        st = os.stat(filename)
        os.chmod(filename, st.st_mode |
                 stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    out = (subprocess.run(filename,
                          capture_output=True, encoding="UTF-8")).stdout

    formatted_text = out.replace("\n", " ").split(" ")
    formatted_text = [x for x in formatted_text if x != ""]

    def is_hex(x): return all(c in string.hexdigits for c in x)

    out = []
    temp_out = ["<br>"]
    counter = 0
    start_flag = False
    for item in formatted_text:
        # there are some headers before the actual data we want to display
        if "AMD" in item:
            start_flag = True

        if start_flag:
            # add a line break before and after each header
            if item.endswith(":"):
                temp_out.append(item)
                temp_out.append("<br>")
                # bold the header
                out.append("<strong>")
                out.append(" ".join(temp_out))
                out.append("</strong>")
                temp_out = ["<br>"]
                counter = 0

            # these are the header words before the colon at the end of the line
            elif not is_hex(item):
                temp_out.append(item)
                counter = 0
            # fall-through case of data
            else:
                if counter == 2:
                    out.append("<br>")
                    counter = 0
                out.append(item)
                counter += 1

    # ACI image source
    image = "<img src=\"https://azure.microsoft.com/svghandler/container-instances?width=600&height=315\" alt=\"Microsoft ACI Logo\" width=\"600\" height=\"315\"><br>"
    style = """
    <style>
        body {
            text-align: center;
            font-family: 'Courier New', monospace;
        }
    </style>
    """
    # put everything together
    return (
        style +
        "<div>" + "<h1>Welcome to Confidential containers on Azure Container Instances!</h1>" +
        image + " ".join(out) +
        "</div>"
    )



if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 
