from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
from prediction import leaf_prediction
import os
import pandas as pd
import pyttsx3
import random
from random import randint

app = Flask(__name__)
app.secret_key = "leaves"


@app.route('/home')
def home():
    return render_template("prediction.html")


AUDIO_FOLDER = 'static/audio'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

app.config['AUDIO_FOLDER'] = AUDIO_FOLDER


def text_to_speech(text, AUDIO_FOLDER):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)

    random_number = random.randint(1000, 9999)
    unique_filename = str(random_number) + ".mp3"
    audio_path = os.path.join(AUDIO_FOLDER, unique_filename)

    # Replace backslashes with forward slashes
    audio_path = audio_path.replace("\\", "/")

    engine.save_to_file(text, audio_path)
    engine.runAndWait()

    return audio_path


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        img = request.files['file_']
        img_path = "static/user_input/" + img.filename
        img.save(img_path)
        p = leaf_prediction(img_path)
        prediction = p[0]
        p_score = p[1]
        leaf_info = p[2]

        print("leaf_info : ", leaf_info)

        # Pass AUDIO_FOLDER to text_to_speech function
        speech_path = text_to_speech(
            leaf_info, app.config['AUDIO_FOLDER'])

        print("p_score : ", p_score)
        formatted_score = "{:.2f}%".format(p_score * 100)
        print(formatted_score)

        return render_template("prediction.html", prediction=prediction, img_path=img_path, p_score=formatted_score, l_info=leaf_info, speech=speech_path)


@app.route('/camera', methods=['GET', 'POST'])
def camera():
    try:
        if request.method == 'POST':
            fs = request.files.get('snap')
            if fs:
                r1 = randint(1, 1000)
                img_name = "image" + str(r1) + ".png"
                file = "static/uploaded/" + img_name
                fs.save(file)
                p = leaf_prediction(file)
                prediction = p[0]
                p_score = p[1]
                leaf_info = p[2]

                print("leaf_info : ", leaf_info)

                # Pass AUDIO_FOLDER to text_to_speech function
                speech_path = text_to_speech(
                    leaf_info, app.config['AUDIO_FOLDER'])

                print("p_score : ", p_score)
                formatted_score = "{:.2f}%".format(p_score * 100)
                print(formatted_score)

                return jsonify(prediction=prediction, img_path=file, p_score=formatted_score, l_info=leaf_info, speech_path=speech_path)
            
        return render_template('camera.html')

    except IndexError:
        return jsonify(prediction="Not matched with Database")

@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["pwd"]

        users_df = pd.read_excel('user.xlsx')

        for index, row in users_df.iterrows():
            if row["email"] == email and row["password"] == pwd:

                return redirect(url_for('home'))

        error_message = 'Invalid email or password. Please try again.'
        return render_template('login.html', msg=error_message)

    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        if request.method == 'POST':
            email = request.form['email']
            pwd = request.form['pwd']
            repwd = request.form['repwd']
            if pwd == repwd:  # Fix the comparison operator
                col_list = ["email", "password"]
                try:
                    # Try reading the existing file, if it exists
                    r1 = pd.read_excel('user.xlsx', usecols=col_list)
                except FileNotFoundError:
                    # If the file doesn't exist, create an empty DataFrame
                    r1 = pd.DataFrame(columns=col_list)

                new_row = {'email': email, 'password': pwd}
                r1 = r1.append(new_row, ignore_index=True)
                r1.to_excel('user.xlsx', index=False)
                print("Records created successfully")
                msg = 'Registration Successful. You can log in here.'
                return render_template('login.html', msg=msg)
            else:
                msg = 'Password and Re-enter password do not match.'
                return render_template('register.html', msg=msg)
        return render_template('register.html')
    except:
        return render_template('register.html', msg="Please Enter valid mail pattern like xyz@gmail.com")


@app.route('/password', methods=['POST', 'GET'])
def password():
    try:
        if request.method == 'POST':
            current_pass = request.form['current']
            new_pass = request.form['new']
            verify_pass = request.form['varify']
            r1 = pd.read_excel('user.xlsx')
            for index, row in r1.iterrows():
                if row["password"] == str(current_pass):
                    if new_pass == verify_pass:
                        r1.loc[index, "password"] = verify_pass
                        r1.to_excel("user.xlsx", index=False)
                        msg1 = 'Password changed successfully'
                        return render_template('password.html', msg=msg1)
                    else:
                        msg = 'Re-entered password is not matched'
                        return render_template('password.html', msg=msg)
            else:
                msg3 = 'Incorrect Password'
                return render_template('password.html', msg=msg3)
        return render_template('password.html')
    except Exception as e:
        return render_template('password.html', msg=e)


@app.route('/graph')
def graph():
    return render_template("graph.html")


@app.route('/logout')
def logout():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(port=5891, debug=True, host='0.0.0.0')
