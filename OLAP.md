OLTP (transactional)
- databáze pro zisk dat (.csv)

OLAP (analytical)
- databáze pro analýzu

Cyklus
- OLTP (.csv) -> ETL (python) -> OLAP (postgre)


MOLAP
- Cube (předpočítané uspořádané data dle os)
  - osa x: kategorie
  - osa y: čas
  - osa z: místo

ROLAP
- hvězdice, sněhová vločka
- dimenze (normalizované tabulky)
- fakt (join tabulka normalizovaných tabulek)

hvězdice  
```
                 dim_roky
                    !
dim_produkty - fakt_objednavky - dim_uzivatele

                    !
                 dim_dopravce
```

sněhová vločka
```
              měsíce  dny
                    !
                 dim_roky
                    !
dim_produkty - fakt_objednavky - dim_uzivatele

                    !
                 dim_dopravce
```

HOLAP
- MOLAP + ROLAP

DM - data market
-> návrh OLAP struktury 
- ROLAP 'ER' diagram
- MOLAP CUBE diagram
