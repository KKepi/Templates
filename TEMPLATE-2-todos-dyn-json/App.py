from flask import Flask, request, jsonify, make_response, render_template, session, redirect, url_for
import jwt
from datetime import datetime, timedelta
from functools import wraps
import json
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
staticdb = os.path.join(basedir, 'static/userdb.json')

app.config["SECRET_KEY"] = "test"

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
    
def issue_token(username):
    token = jwt.encode(
        {'user': username, 'exp': datetime.utcnow() + timedelta(minutes=30)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    resp = make_response(redirect("protected"))
    resp.set_cookie('token', token, httponly=True, secure=False)
    return resp

@app.route("/protected", methods=["GET"])
@token_required
def view_protected_site():
    return render_template("protected.html")

@app.route("/register", methods=["POST"])
def register():
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
            "todo":{
                "work":[],
                "personal":[],
                "study":[],
                "activity":[]
            }
        }
        data["users"].append(new_user)
        
        with open(staticdb, "w") as file:
            json.dump(data, file, indent=4)
        
        resp = issue_token(username)
        return resp
    
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
                return make_response(redirect("protected"))
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

@app.route("/todos", methods=["GET"])
@token_required
def show_todos():
    username = request.user
    filter_param = request.args.get("filter", "all")
    with open(staticdb, "r") as file:
        data = json.load(file)
    user = next((user for user in data["users"] if user["username"] == username), None)
    if not user:
        return render_template("failed.html")
    todos = user["todo"]
    if filter_param == "done":
        filtered_todos = {cat: [t for t in tasks if t[0] == 1] for cat, tasks in todos.items()}
    elif filter_param == "not_done":
        filtered_todos = {cat: [t for t in tasks if t[0] == 0] for cat, tasks in todos.items()}
    else:
        filtered_todos = todos
    return render_template("todos.html", todos=filtered_todos)
    
@app.route("/add", methods=["POST"])
@token_required
def add_todo():
    username = request.user
    
    todo_category = request.form.get('kategorie')
    todo = request.form.get('ukol')
    
    username = request.user

    with open(staticdb, "r") as file:
        data = json.load(file)
    
    user = next((user for user in data["users"] if user["username"] == username), None)
    
    new_todo = (0, todo)
    
    user["todo"][todo_category].append(new_todo)
    
    with open(staticdb, "w") as file:
        json.dump(data, file, indent=4)
        
    return render_template("protected.html")
    
@app.route("/mark_done", methods=["POST"])
@token_required
def mark_done():
    username = request.user
    category = request.form.get("category")
    task_text = request.form.get("task")
    with open(staticdb, "r") as file:
        data = json.load(file)
    user = next((user for user in data["users"] if user["username"] == username), None)
    if not user or category not in user["todo"]:
        return render_template("failed.html")
    for t in user["todo"][category]:
        if t[1] == task_text:
            t[0] = 1  # Označíme jako hotový
            break
    with open(staticdb, "w") as file:
        json.dump(data, file, indent=4)
    return redirect("/todos")

@app.route("/edit_task", methods=["POST"])
@token_required
def edit_task():
    username = request.user
    category = request.form.get("category")
    old_task = request.form.get("old_task")
    new_task = request.form.get("new_task")
    with open(staticdb, "r") as file:
        data = json.load(file)
    user = next((user for user in data["users"] if user["username"] == username), None)
    if not user or category not in user["todo"]:
        return render_template("failed.html")
    for t in user["todo"][category]:
        if t[1] == old_task:
            t[1] = new_task  # Aktualizace textu úkolu
            break
    with open(staticdb, "w") as file:
        json.dump(data, file, indent=4)
    return redirect("/todos")

@app.route("/delete_task", methods=["POST"])
@token_required
def delete_task():
    username = request.user
    category = request.form.get("category")
    task_text = request.form.get("task")
    with open(staticdb, "r") as file:
        data = json.load(file)
    user = next((user for user in data["users"] if user["username"] == username), None)
    if not user or category not in user["todo"]:
        return render_template("failed.html")
    tasks = user["todo"][category]
    user["todo"][category] = [t for t in tasks if t[1] != task_text]
    with open(staticdb, "w") as file:
        json.dump(data, file, indent=4)
    return redirect("/todos")



@app.route("/")
def home():
    return render_template("index.html")

with app.app_context():
    app.run(host="127.0.0.1", port=5000, debug=True)