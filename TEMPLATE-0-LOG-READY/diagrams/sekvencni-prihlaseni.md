Uživatel          Prohlížeč             Flask            Autentizace           Databáze
       |                  |                    |                   |                   |
       | --zadá údaje-->  |                    |                   |                   |
       |                  | ---POST /login---> |                   |                   |
       |                  |                    | --ověření údajů-> |                   |
       |                  |                    |                   | --hledání uživatele-> |
       |                  |                    |                   | <--výsledek ověření-- |
       |                  |                    |                   |                   |
       |                  |                    |                   | [if valid]        |
       |                  |                    |                   | --generování JWT  |
       |                  |                    |                   |    tokenu--       |
       |                  |                    | <--JWT token----- |                   |
       |                  | <--redirect+token  |                   |                   |
       |                  |    cookie--------- |                   |                   |
       | <--zobrazení     |                    |                   |                   |
       |    prislusne     |                    |                   |                   |
       |    page--------- |                    |                   |                   |
       |                  |                    |                   |                   |