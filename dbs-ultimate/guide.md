#### 1

Připojení k Postgre

```python
# Připojení k postgres

from sqlalchemy import create_engine, text

DB_USER = "postgres"
DB_PWD  = "VymrdanecLynux111"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    echo=False,          # True = vypíše SQL na stdout
    pool_pre_ping=True   # jistota, že se spojení obnoví, když „usne“
)
```

#### 2

Import

```python
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2.extras as extras
import pycountry
import psycopg2
from psycopg2 import sql
import matplotlib.pyplot as plt
```

#### 3 (2x)

1) Import dat
    1) získání tabulky stáhnutim
    2) získání tabulky přímo importem csv
3) názvy sloupců
4) přejmenování sloupců
5) výběr sloupců

```python
# Stáhnutí příslušných souborů CSV
tables = pd.read_html("https://www.kurzy.cz/svet/", na_values=["-", "–", "—"])
# Získání tabulky
df = tables[0]
df = pd.read_csv("cizinci.CSV", sep=",", encoding="utf-8-sig")
# Získání názvů sloupců
print(df1)
# Přejmenování sloupců
df1 = df1.rename(columns={
    "Stát": "country",
    "Rok": "year",
    "CZK": "GDP"
})
# Výběr sloupců, které jsou relevantní
df1 = df1[["country", "year", "GDP"]]
# kontrola dat
print(df1)
```

#### 4 (2x)

Pokud potřeba upravit hodnoty řádků (například státy)

```python
# Vytvoření slovníku pro mapování českých názvů zemí na ISO kódy
# Získání unikátních jmen zemí z datasetu
country_names = df1['country'].unique()
print(f"Počet unikátních zemí v datasetu: {len(country_names)}")

# Vytvoření slovníku pro mapování českých názvů zemí na ISO kódy
country_mapping = {
    'Spojené státy americké': 'USA',
    'Čína': 'CHN',
    'Německo': 'DEU',
    'Japonsko': 'JPN',
    'Indie': 'IND',
    'Velká Británie': 'GBR',
    'Francie': 'FRA',
    'Rusko': 'RUS',
    'Brazílie': 'BRA',
    'Itálie': 'ITA',
    'Kanada': 'CAN',
    'Jižní Korea': 'KOR',
    'Austrálie': 'AUS',
    'Španělsko': 'ESP',
    'Mexiko': 'MEX',
    'Indonésie': 'IDN',
    'Nizozemsko': 'NLD',
    'Nizozemí': 'NLD',
    'Saúdská Arábie': 'SAU',
    'Švýcarsko': 'CHE',
    'Polsko': 'POL',
    'Turecko': 'TUR',
    'Švédsko': 'SWE',
    'Belgie': 'BEL',
    'Thajsko': 'THA',
    'Irsko': 'IRL',
    'Rakousko': 'AUT',
    'Norsko': 'NOR',
    'Nigérie': 'NGA',
    'Izrael': 'ISR',
    'Argentina': 'ARG',
    'Jihoafrická republika': 'ZAF',
    'Dánsko': 'DNK',
    'Singapur': 'SGP',
    'Česko': 'CZE',
    'Česká republika': 'CZE',
    'Spojené arabské emiráty': 'ARE',
    'Portugalsko': 'PRT',
    'Rumunsko': 'ROU',
    'Katar': 'QAT',
    'Peru': 'PER',
    'Řecko': 'GRC',
    'Kazachstán': 'KAZ',
    'Alžírsko': 'DZA',
    'Maďarsko': 'HUN',
    'Kuvajt': 'KWT',
    'Ukrajina': 'UKR',
    'Malajsie': 'MYS',
    'Vietnam': 'VNM',
    'Finsko': 'FIN',
    'Bangladéš': 'BGD',
    'Pákistán': 'PAK',
    'Egypt': 'EGY',
    'Chile': 'CHL',
    'Kolumbie': 'COL',
    'Filipíny': 'PHL',
    'Nový Zéland': 'NZL',
    'Slovensko': 'SVK',
    'Maroko': 'MAR',
    'Ekvádor': 'ECU',
    'Omán': 'OMN',
    'Bělorusko': 'BLR',
    'Ázerbájdžán': 'AZE',
    'Bulharsko': 'BGR',
    'Srbsko': 'SRB',
    'Guatemala': 'GTM',
    'Chorvatsko': 'HRV',
    'Lucembursko': 'LUX',
    'Dominikánská republika': 'DOM',
    'Panama': 'PAN',
    'Uruguay': 'URY',
    'Keňa': 'KEN',
    'Kostarika': 'CRI',
    'Jordánsko': 'JOR',
    'Slovinsko': 'SVN',
    'Angola': 'AGO',
    'Libanon': 'LBN',
    'Turkmenistán': 'TKM',
    'Litva': 'LTU',
    'Tádžikistán': 'TJK',
    'Tunisko': 'TUN',
    'Bolívie': 'BOL',
    'Ghana': 'GHA',
    'Bahrajn': 'BHR',
    'Uzbekistán': 'UZB',
    'Lotyšsko': 'LVA',
    'Etiopie': 'ETH',
    'Paraguay': 'PRY',
    'Trinidad a Tobago': 'TTO',
    'Honduras': 'HND',
    'Kypr': 'CYP',
    'Estonsko': 'EST',
    'Papua-Nová Guinea': 'PNG',
    'Salvador': 'SLV',
    'Venezuela': 'VEN',
    'Zambie': 'ZMB',
    'Myanmar': 'MMR',
    'Afghánistán': 'AFG',
    'Island': 'ISL',
    'Bosna a Hercegovina': 'BIH',
    'Severní Makedonie': 'MKD',
    'Malta': 'MLT',
    'Laos': 'LAO',
    'Mongolsko': 'MNG',
    'Senegal': 'SEN',
    'Gruzie': 'GEO',
    'Nikaragua': 'NIC',
    'Mauritius': 'MUS',
    'Mosambik': 'MOZ',
    'Uganda': 'UGA',
    'Kyrgyzstán': 'KGZ',
    'Botswana': 'BWA',
    'Jamajka': 'JAM',
    'Namibie': 'NAM',
    'Kambodža': 'KHM',
    'Brunej': 'BRN',
    'Kongo': 'COG',
    'Rwanda': 'RWA',
    'Haiti': 'HTI',
    'Nepál': 'NPL',
    'Čad': 'TCD',
    'Moldavsko': 'MDA',
    'Albánie': 'ALB',
    'Togo': 'TGO',
    'Arménie': 'ARM',
    'Madagaskar': 'MDG',
    'Benin': 'BEN',
    'Guyana': 'GUY',
    'Bahamy': 'BHS',
    'Černá Hora': 'MNE',
    'Maledivy': 'MDV',
    'Fidži': 'FJI',
    'Svazijsko': 'SWZ',
    'Eswatini': 'SWZ',
    'Surinam': 'SUR',
    'Bhútán': 'BTN',
    'Barbados': 'BRB',
    'Jižní Súdán': 'SSD',
    'Sierra Leone': 'SLE',
    'Džibutsko': 'DJI',
    'Rovníková Guinea': 'GNQ',
    'Maldivská republika': 'MDV',
    'Východní Timor': 'TLS',
    'Antigua a Barbuda': 'ATG',
    'Burundi': 'BDI',
    'Seychely': 'SYC',
    'Belize': 'BLZ',
    'Svatá Lucie': 'LCA',
    'Kapverdy': 'CPV',
    'Středoafrická republika': 'CAF',
    'Eritrea': 'ERI',
    'Libérie': 'LBR',
    'Somálsko': 'SOM',
    'Guinea-Bissau': 'GNB',
    'Šalamounovy ostrovy': 'SLB',
    'Guinea': 'GIN',
    'Grenada': 'GRD',
    'Lesotho': 'LSO',
    'Vanuatu': 'VUT',
    'Gambie': 'GMB',
    'Komory': 'COM',
    'Svatý Vincenc a Grenadiny': 'VCT',
    'Saint Kitts a Nevis': 'KNA',
    'Samoa': 'WSM',
    'Svatý Tomáš a Princův ostrov': 'STP',
    'Dominika': 'DMA',
    'Mikronésie': 'FSM',
    'Tonga': 'TON',
    'Palau': 'PLW',
    'Kiribati': 'KIR',
    'Marshallovy ostrovy': 'MHL',
    'Nauru': 'NRU',
    'Tuvalu': 'TUV',
    'Írán': 'IRN',
    'Hongkong': 'HKG',
    'ČR': 'CZE',
    'Irák': 'IRQ',
    'Portoriko': 'PRI',
    'Súdán': 'SDN',
    'Srí Lanka': 'LKA',
    'Kuba': 'CUB',
    'Tanzanie': 'TZA',
    'Pobřeží slonoviny': 'CIV',
    'Barma': 'MMR',
    'Kongo (Kinshasa)': 'COD',
    'Kamerun': 'CMR',
    'Bahrain': 'BHR',
    'Macao': 'MAC',
    'Libye': 'LBY',
    'Zimbabwe': 'ZWE',
    'Sýrie': 'SYR',
    'Jemen': 'YEM',
    'Mali': 'MLI',
    'Burkina Faso': 'BFA',
    'Gabon': 'GAB',
    'Stát Palestina': 'PSE',
    'Niger': 'NER',
    'Moldávie': 'MDA',
    'Kongo (Brazzaville)': 'COG',
    'Brunei': 'BRN',
    'Malawi': 'MWI',
    'Mauritánie': 'MRT',
    'Kosovo': 'XKX',
    'Monako': 'MCO',
    'Nová Kaledonie': 'NCL',
    'Bermudy': 'BMU',
    'Man (ostrov)': 'IMN',
    'Lichtejnštejnsko': 'LIE',
    'Kajmanské ostrovy': 'CYM',
    'Guam': 'GUM',
    'Francouzská Polynésie': 'PYF',
    'Americké Panenské ostrovy': 'VIR',
    'Faerské ostrovy': 'FRO',
    'Andorra': 'AND',
    'Aruba': 'ABW',
    'Grónsko': 'GRL',
    'Kapverské ostrovy': 'CPV',
    'San Marino': 'SMR',
    'Svatý Vincent': 'VCT',
    'Svatý Kryštof a Nevis': 'KNA',
    'Americká Samoa': 'ASM',
    'Sv. Tomáš a Princův ostrov': 'STP',
    'Dominica': 'DMA',
    'Federativní státy Mikronésie': 'FSM'
}

# Aplikace mapování na sloupec country
df1['country_iso'] = df1['country'].map(country_mapping)

# Kontrola, zda některé země nebyly namapovány
missing_mapping = df1[df1['country_iso'].isna()]
if len(missing_mapping) > 0:
    print(f"Počet zemí bez mapování: {len(missing_mapping)}")
    print("Seznam zemí bez mapování:")
    print(missing_mapping["country"].unique())
else:
    print("Všechny země byly úspěšně namapovány na ISO kódy!")

# Nahrazení původního sloupce country ISO kódy
df1['original_country'] = df1['country']  # Uložení původních názvů pro pozdější referenci
df1['country'] = df1['country_iso']
df1.drop('country_iso', axis=1, inplace=True)

# Zobrazení výsledku
print(df1.head(10))

# Vytvořit z df soubor csv
df1 = df1[["country", "year", "GDP"]]
# Uložení do CSV
df1.to_csv("gdp_data.csv", index=False)
```

#### 5

Navrhnout strukturu DB

#### 6 (gpt o4-mini)

Vytvořit za pochodu tabulky, které se plní daty
> "struktura", vložení .csv souborů, prompt: Na základě poskytnutých CSV bych potřeboval vytvořit tabulky přičemž bych je chtěl naplnit daty ze zmíněných csv... Pozor bude potřeba propojovat pomocí ids a proto je potřeba promyslet jaké tabulky budou první vytvořeny.

#### 7

Vizualizace na základě požadavků