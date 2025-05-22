```python
@app.route("/protected", methods=["GET"])
@token_required
def view_protected_site():
    # Z tokenu získáte username a role
    token = request.cookies.get("token")
    payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    username = payload['user']
    role = payload['role']
    
    # Dotaz na databázi podle username
    if role == "admin":
        # Admin vidí všechny předměty
        predmety = db.session.query(Predmet).all()
    else:
        # Skladník vidí jen své předměty
        predmety = db.session.query(Predmet).filter_by(username=username).all()
    
    # Předání dat do šablony
    return render_template("protected.html", predmety=predmety)
```

```html
<!-- V souboru protected.html -->
<h1>Seznam předmětů</h1>
<table>
    <tr>
        <th>ID</th>
        <th>Název</th>
        <th>Cena</th>
    </tr>
    {% for predmet in predmety %}
    <tr>
        <td>{{ predmet.id_predmet }}</td>
        <td>{{ predmet.jmeno }}</td>
        <td>{{ predmet.cena }}</td>
    </tr>
    {% endfor %}
</table>
```