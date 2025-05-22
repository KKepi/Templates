+---------------------------+     +----------------------------+
|     Flask Application     |     |          Load SQL          |
+---------------------------+     +----------------------------+
| - SECRET_KEY: str         |     | + load_predmety()          | 
| - SQLALCHEMY_DATABASE_URI |-----| + save_predmety()          | 
| - db: SQLAlchemy          |     | + filter_predmety()        | 
+---------------------------+     |                            | 
| + run()                   |     |                            | 
+---------------------------+     |----------------------------|
            |                                    |
            |                                    |
            v                                    V                      +-----------------+
+---------------------------+      +---------------------------+        |   predmety SQL  |  
|      Authentication       |      |           Routes         |         +-----------------+
+---------------------------+      +---------------------------+        | - id_predmet    |
| - token: str              |<-----| + home()                 |         | - jmeno         |
+---------------------------+      | + register_user()        |         | - cena          |
| + token_required(func)    |      | + register_admin()       |         |                 |
| + issue_token(username)   |      | + view_protected_site()  |         |                 |
| + login()                 |      | + view_admin_panel()     |         |                 |
| + logout()                |      | + logout()               |         |                 |
+---------------------------+      +---------------------------+        |                 |
            |                                 |                         |                 |
            |                                 |                         |                 |
            v                                 v                         |                 |
+---------------------------+      +---------------------------+        |                 |
|   UserDB (NoSQL/JSON)     |      |        Templates          |<-------+-----------------+
+---------------------------+      +---------------------------+
| - users: [                |      | - index.html              |
|   {username: str,         |      | - protected.html          |
|    password: str,         |      | - adminpanel.html         |
|    role: str}             |      | - failed.html             |
|   ]                       |      +---------------------------+
+---------------------------+