from flask import Flask, request, jsonify, make_response, render_template, session, redirect, url_for
import jwt
from datetime import datetime, timedelta
from functools import wraps
import json
import os
from flask_sqlalchemy import SQLAlchemy
from os import environ
import jinja2

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# NoSQL databáze pro uživatele
staticdb = os.path.join(basedir, 'static/user_db.json')

# heslo pro jwt tokeny
app.config["SECRET_KEY"] = "test"

# SQL databáze pro předměty
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir,'app.db')}"
db = SQLAlchemy(app)

#### SQL / tables

####

##########################################################################################
#### wrapper pro kontrolu tokenu

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token") or request.headers.get("Authorization")
        if not token:
            return jsonify({"Alert!":"You don't have a token"}), 403
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.user = payload['user']  # Save the username to the request
        except jwt.ExpiredSignatureError:
            return jsonify({'Alert!': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'Alert!': 'Invalid token'}), 403

        return func(*args, **kwargs)
    return decorated

#### předání tokenu - username + role
def issue_token(username):
    with open(staticdb, "r") as file:
        data = json.load(file)
    
    user = next((user for user in data["users"] if user["username"]==username), None)
    
    if user["role"] == "admin":
        token = jwt.encode(
        {'user': username, 'role': user["role"], 'exp': datetime.utcnow() + timedelta(minutes=30)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
        )
        
        resp = make_response(redirect("adminpanel"))
        resp.set_cookie('token', token, httponly=True, secure=False)
        return resp
    
    else:
        token = jwt.encode(
            {'user': username, 'role': user["role"], 'exp': datetime.utcnow() + timedelta(minutes=30)},
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        resp = make_response(redirect("protected"))
        resp.set_cookie('token', token, httponly=True, secure=False)
        return resp

#### registrace (provádí admin!)
@app.route("/admin/register", methods=["POST"])
@token_required
def register_admin():
    
    token = request.cookies.get("token") or request.headers.get("Authorization")
    if token.startswith("Bearer "):
            token = token.split(" ")[1]
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        role = payload['role']
    except jwt.ExpiredSignatureError:
        return jsonify({'Alert!': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'Alert!': 'Invalid token'}), 403
    
    if role == "admin":
        pass
    else:
        return render_template("protected.html")
    
    username = request.form.get('rusername')
    password = request.form.get('rpassword')
    role = request.form.get("rrole")
    
    with open(staticdb, "r") as file:
        data = json.load(file)
    
    user = next((user for user in data["users"] if user["username"]==username), None)
    if user:
        return render_template("failed.html")
    else:
        new_user = {
            "username":username,
            "password":password,
            "role":role
            }
        data["users"].append(new_user)
        
        with open(staticdb, "w") as file:
            json.dump(data, file, indent=4)
    return render_template("index.html")

#### registrace (provádí uživatel) + předání tokenu
@app.route("/user/register", methods=["POST"])
def register_user():
    username = request.form.get('rusername')
    password = request.form.get('rpassword')
    
    with open(staticdb, "r") as file:
        data = json.load(file)
    
    user = next((user for user in data["users"] if user["username"]==username), None)
    if user:
        return render_template("failed.html")
    else:
        new_user = {
            "username":username,
            "password":password,
            "role":"skladnik"
            }
        data["users"].append(new_user)
        
        with open(staticdb, "w") as file:
            json.dump(data, file, indent=4)
    return render_template("index.html")

#### přihlášení do existujícího účtu (nahrazuje token pokud existuje)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("lusername")
    password = request.form.get("lpassword")
    
    with open(staticdb, "r") as file:
        data = json.load(file)
        
    # Ověření uživatele podle přihlašovacích údajů
    user = next((user for user in data["users"] if user["username"] == username and user["password"] == password), None)
    if not user:
        return render_template("failed.html")
    
    # Získáme token z cookie nebo hlavičky, pokud existuje
    token = request.cookies.get("token") or request.headers.get("Authorization")
    if token:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            # Kontrola, zda token patří právě přihlašovanému uživateli
            if payload.get("user") == username:
                # Pokud ano, můžeme pokračovat bez vydání nového tokenu
                if payload.get("role") != "admin":
                    return make_response(redirect("protected"))
                else:
                    # toto teoreticky neni potreba, protoze se o to stara uz /protected - ktera kontroluje zda uzivatel neni nahodou admin, ale i tak neni spatny to zde mit
                    return make_response(redirect("adminpanel"))
            else:
                # Token patří jinému uživateli – vyvoláme výjimku, která nás donutí vydat nový token
                raise jwt.InvalidTokenError("Token user mismatch")
        except jwt.ExpiredSignatureError:
            # Token expiroval – budeme vydávat nový
            pass
        except jwt.InvalidTokenError:
            # Token je neplatný nebo patří jinému uživateli – budeme vydávat nový
            pass

    # Vydání nového tokenu pro přihlašovaného uživatele
    resp = issue_token(username)
    return resp

#### obrazovka pro bezneho usera - kontroluje roli z tokenu (admin nema co delat v obrazovce pro bezneho usera)
@app.route("/protected", methods=["GET"])
@token_required
def view_protected_site():
    token = request.cookies.get("token") or request.headers.get("Authorization")
    if token.startswith("Bearer "):
            token = token.split(" ")[1]
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        role = payload['role']
    except jwt.ExpiredSignatureError:
        return jsonify({'Alert!': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'Alert!': 'Invalid token'}), 403
    
    if role == "admin":
        pass
    else:
        return render_template("protected.html")
    
    return render_template("adminpanel.html")

#### obrazovka pro admina - kontroluje roli z tokenu
@app.route("/adminpanel", methods=["GET"])
@token_required
def view_admin_panel():
    token = request.cookies.get("token") or request.headers.get("Authorization")
    if token.startswith("Bearer "):
            token = token.split(" ")[1]
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        role = payload['role']
    except jwt.ExpiredSignatureError:
        return jsonify({'Alert!': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'Alert!': 'Invalid token'}), 403
    
    if role == "admin":
        pass
    else:
        resp = make_response(redirect("/protected"))
        return resp
    
    return render_template("adminpanel.html")

#### moznost odhlasit se a resetovat token - tato funkce by mela byt mozna volana kazdou html strankou
@app.route("/logout", methods=["POST"])
@token_required
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie('token')
    return resp
    
#### hlavni obrazovka
@app.route("/")
def home():
    
    return render_template("index.html")

with app.app_context():
    db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=True)