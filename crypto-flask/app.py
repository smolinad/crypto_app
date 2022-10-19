from algorithms.caesar import caesarEncrypt, caesarDecrypt
from algorithms.vigenere import vigenereEncrypt, vigenereDecrypt
from algorithms.affine import affineEncrypt, affineDecrypt
from algorithms.substitution import substitutionEncrypt, substitutionDecrypt, substitutionCryptanalysis
from algorithms.permutation import permutationDecrypt, permutationEncrypt
from algorithms.hillText import hillCryptoAnalysis, hillEncrypt, hillDecrypt
from algorithms.hillImage import hillImgEncrypt, hillImgDecrypt
from algorithms.des3 import des3Encrypt
from algorithms.des import desEncrypt
from algorithms.sdes import sdesEncrypt
from algorithms.aes import aesEncrypt
from algorithms.goodies import processInput, InputKeyError, deleteImages, strToByte

from flask import Flask, redirect, url_for, session, flash
# from flask_session import Session
from flask.templating import render_template
from werkzeug.utils import secure_filename
import cv2 as cv

from algorithms.form import InputForm, ImageForm

import os

dir = 'web/static/uploads/'
img_dir = 'uploaded'
upkey_dir = 'uploaded_key'
key_dir = 'key'
enc_dir = 'encrypted'
dec_dir = 'decrypted'

UPLOAD_FOLDER = 'web/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='web/templates')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

list_dir = [
    os.path.join(app.config['UPLOAD_FOLDER'], img_dir),
    os.path.join(app.config['UPLOAD_FOLDER'], key_dir),
    os.path.join(app.config['UPLOAD_FOLDER'], enc_dir),
    os.path.join(app.config['UPLOAD_FOLDER'], dec_dir),
    os.path.join(app.config['UPLOAD_FOLDER'], upkey_dir)
]

@app.route('/', methods=['GET', 'POST'])
def home():
    deleteImages(list_dir)
    form = InputForm()
    if form.validate_on_submit():
        cypher_mode = form.cypher_mode.data
        input_text = processInput(form.input_text.data)
        input_key = form.input_key.data

        if form.encrypt.data:
            session["encrypted_or_decrypted"] = "encrypted"
            if input_key != '':
                try:
                    match cypher_mode:
                        case "Caesar cipher":
                            session["output_text"], session["output_key"] = caesarEncrypt(input_text, input_key) #Ok
                        case "Vigenere cipher":
                            session["output_text"], session["output_key"] = vigenereEncrypt(input_text, input_key) #Ok
                        case "Affine cipher":
                            session["output_text"], session["output_key"] = affineEncrypt(input_text, input_key) #Ok 
                        case "Substitution cipher":
                            session["output_text"], session["output_key"] = substitutionEncrypt(input_text, input_key) #Ok
                        case "Permutation cipher":
                            session["output_text"], session["output_key"] = permutationEncrypt(input_text, input_key) #Ok
                        case "Hill (Text) cipher":
                            session["output_text"], session["output_key"] = hillEncrypt(input_text, input_key) # Ok
                        case "DES (text) cipher":
                            session["output_text"], session["output_key"] = sdesEncrypt(input_text, input_key, 'ECB') 
                    return redirect(url_for('outputTextAndKey')) 

                except InputKeyError as e:
                    flash(e.message)     
                         
            else:
                match cypher_mode:
                    case "Caesar cipher":
                        session["output_text"], session["output_key"] = caesarEncrypt(input_text) #Ok 
                    case "Vigenere cipher":
                        session["output_text"], session["output_key"] = vigenereEncrypt(input_text) #Ok
                    case "Affine cipher":
                        session["output_text"], session["output_key"] = affineEncrypt(input_text) #Ok
                    case "Substitution cipher":
                        session["output_text"], session["output_key"] = substitutionEncrypt(input_text) # Ok (I hope :s)
                    case "Permutation cipher":
                        session["output_text"], session["output_key"] = permutationEncrypt(input_text) # Ok
                    case "Hill (Text) cipher":
                        session["output_text"], session["output_key"] = hillEncrypt(input_text) # Ok
                return redirect(url_for('outputTextAndKey')) 
                
        elif form.decrypt.data:
            if input_key != '':
                try:
                    session["encrypted_or_decrypted"] = "decrypted"
                    match cypher_mode:
                        case "Caesar cipher":
                            session["output_text"], session["output_key"] = caesarDecrypt(input_text, input_key) # Ok
                        case "Vigenere cipher":
                            session["output_text"], session["output_key"] = vigenereDecrypt(input_text, input_key) # Ok
                        case "Affine cipher":
                            session["output_text"], session["output_key"] = affineDecrypt(input_text, input_key) # Ok
                        case "Substitution cipher":
                            session["output_text"], session["output_key"] = substitutionDecrypt(input_text, input_key) #Ok
                        case "Permutation cipher":
                            session["output_text"], session["output_key"] = permutationDecrypt(input_text, input_key) # Ok
                        case "Hill (Text) cipher":
                            session["output_text"], session["output_key"] = hillDecrypt(input_text, input_key) #Ok

                    return redirect(url_for('outputTextAndKey'))  

                except InputKeyError as e:
                    flash(e.message) 

            else:
                match cypher_mode:
                    case "Caesar cipher":
                        session["analysis_output"] = caesarDecrypt(input_text) # Ok
                        return redirect(url_for('bruteForceAnalysis'))
                    case "Vigenere cipher":
                        session["analysis_output"] = vigenereDecrypt(input_text) # Ok
                        return redirect(url_for('bruteForceAnalysis'))
                    case "Affine cipher":
                        session["analysis_output"] = affineDecrypt(input_text) # Ok
                        return redirect(url_for('bruteForceAnalysis'))
                    case "Substitution cipher":
                        session["analysis_output"] = substitutionCryptanalysis(input_text) #Ok
                        return redirect(url_for('substitutionAnalysis'))
                    case "Permutation cipher":
                        session["analysis_output"] = permutationDecrypt(input_text) # Ok
                        return redirect(url_for('bruteForceAnalysis'))
                    case "Hill (Text) cipher":
                        return
                        # session["output_text"] = hillCryptoAnalysis(input_text)
                        # return redirect(url_for('outputTextAndKey'))  

                

    return render_template('textalg.html', form=form)


@app.route('/encrypted', methods=['GET'])
def outputTextAndKey():
    output_text = session.get("output_text", None)
    output_key = session.get("output_key", None)
    encrypted_or_decrypted = session.get("encrypted_or_decrypted", None)
    return render_template(
        'output.html', 
        encrypted_or_decrypted=encrypted_or_decrypted, 
        output_text=output_text, 
        output_key=output_key)
    

@app.route('/decrypted', methods=['GET'])
def bruteForceAnalysis():
    output = session.get("analysis_output", None)
    return render_template('bruteforce.html', output=output)


@app.route('/decrypted-', methods=['GET'])
def substitutionAnalysis():
    frequency, digraphs = session.get("analysis_output", None)
    return render_template('subsanalysis.html', frequency=frequency, digraphs=digraphs)


@app.route('/image-ciphers', methods=['GET', 'POST'])
def imgAlgorithms():
    deleteImages(list_dir)
    form = ImageForm()
    if form.validate_on_submit():
        cypher_mode = form.cypher_mode.data
        input_key = strToByte(form.input_key.data)
        input_img = form.input_img.data
        input_mode = form.block_mode.data
        filename = secure_filename(input_img.filename)
        path_ = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded', filename)
        input_img.save(path_)

        session["input_img_folder"] = 'uploads/uploaded/'
        session["input_img_filename"] = filename

        if form.encrypt_img.data:
            session["encrypted_or_decrypted"] = "encrypted"
            session["hill"] = False
            try:
                match cypher_mode:
                    case "Hill (Image) cipher":
                        session["hill"] = True
                        if form.input_key_as_img.data:
                            input_key_img = form.input_key_as_img.data
                            key_filename = secure_filename(input_key_img.filename)
                            session["key_img_folder"] = upkey_dir + "/"
                            session["key_img_filename"] = key_filename
                            path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_key', key_filename)
                            input_key_img.save(path_to_save)
                        else:
                            key_filename = ""
                            session["key_img_folder"] = key_dir + "/"
                            session["key_img_filename"] = filename
                        hillImgEncrypt(filename, key_filename)
                        return redirect(url_for('outputImgAndKey')) 
                    case "3DES cipher":
                        session["result_dict"] = des3Encrypt(filename, input_mode, input_key)
                        return redirect(url_for('outputImgAndKey'))
                    case "DES cipher":
                        session["result_dict"] = desEncrypt(filename, input_mode, input_key)
                        return redirect(url_for('outputImgAndKey')) 
                    case "AES cipher":
                        session["result_dict"] = aesEncrypt(filename, input_mode, input_key)
                        return redirect(url_for('outputImgAndKey')) 

            except InputKeyError as e:
                flash(e.message)                          
                
        elif form.decrypt_img.data:
            try:
                session["encrypted_or_decrypted"] = "decrypted"
                session["hill"] = False
                match cypher_mode:
                    case "Hill (Image) cipher":
                        session["hill"] = True
                        if form.input_key_as_img.data:
                            input_key_img = form.input_key_as_img.data
                            key_filename = secure_filename(input_key_img.filename)
                            session["key_img_folder"] = upkey_dir + "/"
                            session["key_img_filename"] = key_filename
                            path_to_save = os.path.join(
                                app.config['UPLOAD_FOLDER'],
                                'uploaded_key',
                                key_filename
                                )
                            input_key_img.save(path_to_save)
                        else:
                            key_filename = ""
                        hillImgDecrypt(filename, key_filename)

                return redirect(url_for('outputImgAndKey'))  

            except InputKeyError as e:
                flash(e.message)           
    return render_template('imgalg.html', form=form)


@app.route('/encrypted-img', methods=['POST', 'GET'])
def outputImgAndKey():
    encrypted_or_decrypted = session.get("encrypted_or_decrypted", None) 

    input_img_folder = session.get("input_img_folder", None)
    input_img_filename = session.get("input_img_filename", None)

    output_img_folder = "uploads/" + encrypted_or_decrypted + "/"
    output_img_filename = input_img_filename

    if session.get("hill", None):
        key_img_folder = "uploads/" + session.get("key_img_folder", None)
        key_img_filename = session.get("key_img_filename", None)
    else:
        key_img_folder = key_img_filename = None
        result_dict = session.get("result_dict", None)

    return render_template(
        'imgoutput.html', 
        encrypted_or_decrypted=encrypted_or_decrypted,
        input_img_folder=input_img_folder,
        input_img_filename=input_img_filename,
        output_img_folder=output_img_folder,
        output_img_filename=output_img_filename,
        key_img_folder=key_img_folder,
        key_img_filename=key_img_filename
    )


if __name__ == '__main__':
    app.run(debug=True)