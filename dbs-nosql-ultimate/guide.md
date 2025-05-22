#### 1. 

Import

```python
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2.extras as extras
import pycountry
```

#### 2 (2x)

Stáhnout a upravit data (relevantní sloupce, přejmenovat)

```python
# Stáhnutí příslušných souborů CSV
tables = pd.read_html("https://www.kurzy.cz/svet/", na_values=["-", "–", "—"])
# Získání tabulky
df1 = tables[0]
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

#### 3 (2x)

Upravit řádky, případně datové typy

```python
#### Přejmenování

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

#### Čáry a mezery

# 1. pryč čáry a mezery
df1['GDP'] = df1['GDP'].str.replace('\xa0', '', regex=False)  # odstraní nezlomitelnou mezeru
df1['GDP'] = df1['GDP'].str.replace(' ', '', regex=False)     # odstraní běžné mezery

# 2. převod na číslo, jinak NaN
df1['GDP'] = pd.to_numeric(df1['GDP'], errors='coerce')

# Kontrola
print(df1.dtypes)

```

#### 4.

Magické spojení csv díky na základě společného sloupce (join)

```python
# načtení dat
cizinci_df = pd.read_csv('cizinci_data.csv', sep=',', encoding='utf-8')
hdp_df = pd.read_csv('gdp_data.csv', sep=',', encoding='utf-8')
# sloučení dat na základě country
merged_df = cizinci_df.merge(hdp_df, on='country', how='left')
# kontrola
missing = merged_df[merged_df['GDP'].isnull()]
print("Záznamy s chybějícím HDP:", len(missing))
# ukázka dokumentu pro mongodb
print(merged_df.head(1).to_dict(orient='records'))
print(merged_df)
```

#### 5.

Vložení jako jeden velký dokument file do Mongodb

```python
# připojení k MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['cizinci_db']
collection = db['cizinci_hdp']
# vložení dat do MongoDB
records = merged_df.to_dict(orient='records')
collection.insert_many(records)
```

#### 6. 

Možnost přidat sloupce (dobrovolné)

```
# pomocná funkce pro čištění a převod GDP na int
def parse_gdp(gdp_str):
    # pokud není řetězec, např. float nan, vrať 0
    if not isinstance(gdp_str, str):
        return 0
    # vyber jen číslice
    digits = ''.join(ch for ch in gdp_str if ch.isdigit())
    return int(digits) if digits else 0

def gdp_category(gdp):
    if gdp < 10000:
        return 'low'
    elif gdp < 30000:
        return 'medium'
    else:
        return 'high'

# aktualizace dokumentů s číselným GDP i kategorií
for doc in collection.find():
    raw = doc.get('GDP', '')
    num = parse_gdp(raw)
    category = gdp_category(num)
    collection.update_one(
        {'_id': doc['_id']},
        {'$set': {'gdp_category': category, 'gdp_numeric': num}}
    )
```

#### 7.

Vizualizace