Uživatel          Prohlížeč            Routes           Load SQL         SQL Database       Templates
       |                  |                   |                 |                  |                |
       | --klikne na----->|                   |                 |                  |                |
       | --zobrazit------>|                   |                 |                  |                |
       | --předměty------>|                   |                 |                  |                |
       |                  |                   |                 |                  |                |
       |                  | ---GET /predmety->|                 |                  |                |
       |                  |                   |                 |                  |                |
       |                  |                   |------kontrola tokenu-------------->|                |
       |                  |                   |                 |                  |                |
       |                  |                   | --load_predmety()-->               |                |
       |                  |                   |                 |                  |                |
       |                  |                   |                 | ---SQL SELECT--->|                |
       |                  |                   |                 |                  |                |
       |                  |                   |                 | <---výsledky-----|                |
       |                  |                   |                 |                  |                |
       |                  |                   | <--pole předmětů--|                |                |
       |                  |                   |                 |                  |                |
       |                  |                   | --filter_predmety()-->             |                |
       |                  |                   |                 |                  |                |
       |                  |                   | <--filtrované předměty--|          |                |
       |                  |                   |                 |                  |                |
       |                  |                   | ---render_template('predmety.html', predmety=...)-->|
       |                  |                   |                 |                  |                |
       |                  |                   |                 |                  |                |
       |                  |                   | <--HTML stránka s předměty---------|                |
       |                  |                   |                 |                  |                |
       |                  | <--HTML stránka s předměty--|       |                  |                |
       |                  |                   |                 |                  |                |
       | <--zobrazení-----|                   |                 |                  |                |
       | --předmětů-------|                   |                 |                  |                |
       |                  |                   |                 |                  |                |