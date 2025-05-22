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
staticdb = os.path.join(basedir, 'static/userdb.json')

app.config["SECRET_KEY"] = "test"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir,'app.db')}"
db = SQLAlchemy(app)

# produkty table
class Produkt(db.Model):
    __tablename__ = 'produkty'
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(100), nullable=False)
    cena = db.Column(db.Float, nullable=False)

# zasoby table
class Zasoba(db.Model):
    __tablename__ = 'zasoby'
    id = db.Column(db.Integer, primary_key=True)
    produkt_id = db.Column(db.Integer, db.ForeignKey('produkty.id'), nullable=False)
    mnozstvi = db.Column(db.Integer, default=0)
    produkt = db.relationship('Produkt', backref=db.backref('zasoby', lazy=True))

# objednavky table
class Objednavka(db.Model):
    __tablename__ = 'objednavky'
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.DateTime, default=datetime.utcnow)
    produkt_id = db.Column(db.Integer, db.ForeignKey('produkty.id'), nullable=False)
    mnozstvi = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    produkt = db.relationship('Produkt')

def token_required(func):
    """ Chrání funkci kontrolou tokenu uživatele.
    
        Parameters
        ----------
        func: funkce
            Funkce jež je chráněna kontrolou tokenu
            
        Returns
        -------
        json
            Upozornění v případě, že je token neplatný nebo neexistující.
        args, kwargs
            Pokud je token správný, spustí se chráněná funkce.
    """
        
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
    """ Vydání tokenu.

        Parameters
        ----------
        username: string
            Prvek z kterého se vytváří hash pro vytvoření tokenu. 
        
        Returns
        -------
        resp: html
            Přesměrování na zabezpečenou stránku spolu s předáním tokenu do cookies.        
    
    """
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

@app.route("/adminpanel", methods=["GET"])
@token_required
def view_admin_panel():
    """ Přesměrování na zabezpečenou stránku pro admina
    
        Returns
        -------
        render_template("adminpanel.html): html
            Zabezpečená stránka pro admina
    """
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

@app.route("/protected", methods=["GET"])
@token_required
def view_protected_site():
    """ Přesměrování na zabezpečenou stránku pro skladníka
    
        Returns
        -------
        render_template("protected.html): html
            Zabezpečená stránka
    """
    return render_template("protected.html")

@app.route("/register", methods=["POST"])
@token_required
def register():
    """ Možnost registrace běžného uživatele (pokud jste adminem)
    """
    
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

@app.route("/login", methods=["POST"])
def login():
    """ Přihlášení na základě existence tokenu či správných přihlašovacích údajů rovnou s vydáním tokenu
    
        Returns:
        render_template("failed.html"): html
            Přesměrování na stránku, která uživatele informuje o špatném zadání přihlašovacích údajů
        make_response(redirect("protected")): html
            Přesměrování pomocí API žádosti na zabezpečenou stránku, díky existenci platného tokenu
        jwt.InvalidtokenError("Token user mismatch"): pass -> vydání tokenu
        resp: html
            Vydání nového tokenu a potom přesměrování na zabezpečenou stránku.
    """
    
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

@app.route("/orders")
@token_required
def objednavky():
    vsechny_objednavky = Objednavka.query.all()
    return render_template("orders.html", order=vsechny_objednavky)

@app.route("/inventory")
@token_required
def sklad():
    vsechny_produkty = Produkt.query.all()
    
    produkty_a_mnozstvi = []
    for p in vsechny_produkty:
        pocet = sum(z.mnozstvi for z in p.zasoby)
        produkty_a_mnozstvi.append(
            {
                'produkt':p,
                'mnozstvi':pocet
            }
        )
    
    nizke_mnozstvi = 5
    return render_template("inventory.html", items=produkty_a_mnozstvi, threshold=nizke_mnozstvi)

@app.route("/inventory", methods=["POST"])
@token_required
def create_product():
    data = request.form
    nazev = str(data.get('produkt_nazev'))
    cena = int(data.get('produkt_cena'))
    mnozstvi = int(data.get('produkt_mnozstvi'))

    product = Produkt(nazev=nazev, cena=cena)
    db.session.add(product)
    db.session.commit()

    stock = Zasoba(produkt_id=product.id, mnozstvi=mnozstvi)
    db.session.add(stock)
    db.session.commit()

    return redirect("/inventory")
    
@app.route('/orders/<int:id>', methods=['GET'])
@token_required
def get_order(id):
    order = Objednavka.query.get_or_404(id)
    return render_template('order_detail.html', order=order)

@app.route('/orders', methods=['POST'])
@token_required
def create_order():
    data = request.form
    produkt_id = int(data.get('produkt_id'))
    mnozstvi = int(data.get('mnozstvi'))
    # decrement stock
    stock = Zasoba.query.filter_by(produkt_id=produkt_id).first()
    if not stock or stock.mnozstvi < mnozstvi:
        return "Insufficient stock", 400
    stock.mnozstvi -= mnozstvi
    order = Objednavka(produkt_id=produkt_id, mnozstvi=mnozstvi)
    db.session.add(order)
    db.session.commit()
    return redirect("/orders")

@app.route('/orders/<int:id>', methods=['POST'])
@token_required
def update_order(id):
    order = Objednavka.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status:
        order.status = new_status
        db.session.commit()
    return redirect(url_for('get_order', id=id))

@app.route("/")
def home():
    return render_template("index.html")

with app.app_context():
    db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=True)