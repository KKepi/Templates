import tkinter as tk
from tkinter import ttk
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
import re

#### Přípojení k databázi ####
def connect_to_db():
    try:
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
        
        print("Úspěšně připojeno k databázi.")
        
        return engine

    except Exception as e:
        print(f"Chyba při připojování k databázi: {e}")
        return None

#### vytvoření potřebných tabulek ####
def create_table(engine=None):
    if engine is None:
        engine = connect_to_db()
        
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Experiment (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description VARCHAR(255) NOT NULL
            )
        """))
        conn.commit()
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Model (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                param1 FLOAT NOT NULL,
                param2 FLOAT NOT NULL,
                param3 FLOAT NOT NULL,
                experiment_id INTEGER REFERENCES Experiment(id)
            )
        """))
        conn.commit()
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Result (
                id SERIAL PRIMARY KEY,
                model_id INTEGER REFERENCES Model(id),
                experiment_id INTEGER REFERENCES Experiment(id),
                value FLOAT
            )
        """))
        conn.commit()
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS TypeModel (
                id SERIAL PRIMARY KEY,
                type VARCHAR(50) NOT NULL
            )
        """))
        conn.commit()
        
#### GUI ####

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PostgreSQL GUI")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2E2E2E")
        self.root.resizable(False, False)
        
        # Připojení k databázi
        self.engine = connect_to_db()
        
        # Vytvoření tabulky
        create_table(self.engine)
        
        self.create_tabs()
        
        self.root.mainloop()
        
    def create_tabs(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#2E2E2E', borderwidth=0)
        style.configure('TNotebook.Tab', background='#444', foreground='white')
        style.map('TNotebook.Tab', background=[('selected', '#666')])

        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both')

        # === ZÁLOŽKA 1 ===
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text='Založení experimentu')

        # Nadpis
        title = tk.Label(tab1, text="Založení experimentu", font=("Helvetica", 18, "bold"), bg="#2E2E2E", fg="white")
        title.pack(pady=(20, 5))

        subtitle = tk.Label(tab1, text="Založte experiment pro ai", font=("Helvetica", 12), bg="#2E2E2E", fg="white")
        subtitle.pack(pady=(0, 20))

        # Vstup: jméno experimentu
        experiment_name_label = tk.Label(tab1, text="Jméno experimentu:", bg="#2E2E2E", fg="white")
        experiment_name_label.pack(anchor="w", padx=20)
        self.experiment_name_entry = tk.Entry(tab1, width=40)
        self.experiment_name_entry.pack(padx=20, pady=5)

        # Vstup: popis experimentu
        experiment_desc_label = tk.Label(tab1, text="Popis experimentu:", bg="#2E2E2E", fg="white")
        experiment_desc_label.pack(anchor="w", padx=20)
        self.experiment_desc_entry = tk.Entry(tab1, width=40)
        self.experiment_desc_entry.pack(padx=20, pady=5)

        # Chybová hláška
        self.error_label = tk.Label(tab1, text="", fg="red", bg="#2E2E2E", font=("Helvetica", 10))
        self.error_label.pack(pady=(5, 10))

        # Tlačítko
        submit_btn = tk.Button(tab1, text="Založit experiment", command=self.validate_and_create)
        submit_btn.pack(pady=10)

        # === ZÁLOŽKA 2 ===
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text='Vytvořit model')
        
        title = tk.Label(tab2, text="Založení modelu", font=("Helvetica", 18, "bold"), bg="#2E2E2E", fg="white")
        title.pack(pady=(20, 5))

        subtitle = tk.Label(tab2, text="Založte model na základě poskytnutých typů modelů", font=("Helvetica", 12), bg="#2E2E2E", fg="white")
        subtitle.pack(pady=(0, 20))
        
        # Vstup: jméno modelu
        model_name_label = tk.Label(tab2, text="Jméno modelu:", bg="#2E2E2E", fg="white")
        model_name_label.pack(anchor="w", padx=20)
        self.model_name_entry = tk.Entry(tab2, width=40)
        self.model_name_entry.pack(padx=20, pady=5)
        
        # Vstup: popis modelu
        model_desc_label = tk.Label(tab2, text="Popis modelu:", bg="#2E2E2E", fg="white")
        model_desc_label.pack(anchor="w", padx=20)
        self.model_desc_entry = tk.Entry(tab2, width=40)
        self.model_desc_entry.pack(padx=20, pady=5)
        
        # Vstup: typ modelu
        model_type_label = tk.Label(tab2, text="Typ modelu:", bg="#2E2E2E", fg="white")
        model_type_label.pack(anchor="w", padx=20)
        self.model_type_entry = tk.Listbox(tab2, height=5)
        self.model_type_entry.pack(padx=20, pady=5, fill="x")
        
        # Vstup: parametry modelu
        model_param1_label = tk.Label(tab2, text="Parametr 1:", bg="#2E2E2E", fg="white")
        model_param1_label.pack(anchor="w", padx=20)
        self.model_param1_entry = tk.Entry(tab2, width=40)
        self.model_param1_entry.pack(padx=20, pady=5)
        model_param2_label = tk.Label(tab2, text="Parametr 2:", bg="#2E2E2E", fg="white")
        model_param2_label.pack(anchor="w", padx=20)
        self.model_param2_entry = tk.Entry(tab2, width=40)
        self.model_param2_entry.pack(padx=20, pady=5)
        model_param3_label = tk.Label(tab2, text="Parametr 3:", bg="#2E2E2E", fg="white")
        model_param3_label.pack(anchor="w", padx=20)
        self.model_param3_entry = tk.Entry(tab2, width=40)
        self.model_param3_entry.pack(padx=20, pady=5)
        
        # Chybová hláška
        self.model_error_label = tk.Label(tab2, text="", fg="red", bg="#2E2E2E", font=("Helvetica", 10))
        self.model_error_label.pack(pady=(5, 10))
        
        # Tlačítko
        model_submit_btn = tk.Button(tab2, text="Založit model", command=self.validate_and_create_model)
        model_submit_btn.pack(pady=10)
        
        
        model_types = self.load_model_types()
        for model_type in model_types:
            self.model_type_entry.insert(tk.END, model_type)

        # === ZÁLOŽKA 3 ===
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text='Výsledky')
        
        # Titulek
        tk.Label(tab3, text="Vyberte experiment a modely", font=("Helvetica", 14), bg="#2E2E2E", fg="white").pack(pady=(20, 10))

        # 1. Výběr experimentu
        tk.Label(tab3, text="Experiment:", bg="#2E2E2E", fg="white").pack(anchor="w", padx=20)

        self.experiment_combo = ttk.Combobox(tab3, state="readonly", width=40)
        self.experiment_combo.pack(padx=20, pady=(0, 10), fill="x")

        # Naplnění názvů experimentů
        self.load_experiments()

        # 2. Checkbuttony pro modely
        tk.Label(tab3, text="Modely:", bg="#2E2E2E", fg="white").pack(anchor="w", padx=20)

        self.model_checks = []
        self.model_vars = []

        models = self.load_models()
        for name in models:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(tab3, text=name, variable=var, bg="#2E2E2E", fg="white", selectcolor="#2E2E2E")
            chk.pack(anchor="w", padx=40)
            self.model_checks.append(chk)
            self.model_vars.append((name, var))

        # 3. Tlačítko pro spuštění
        tk.Button(tab3, text="Vygenerovat výsledek", command=self.generate_results).pack(pady=20)
        
    def load_experiments(self):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM Experiment"))
                experiment_names = [row[0] for row in result]
                self.experiment_combo['values'] = experiment_names
        except Exception as e:
            print(f"Chyba při načítání experimentů: {e}")
    
    def load_models(self):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM Model"))
                return [row[0] for row in result]
        except Exception as e:
            print(f"Chyba při načítání modelů: {e}")
            return []
    
    def generate_results(self):
        selected_exp = self.experiment_combo.get()
        selected_models = [name for name, var in self.model_vars if var.get()]

        if not selected_exp:
            print("Musíte vybrat experiment.")
            return
        if not selected_models:
            print("Musíte vybrat alespoň jeden model.")
            return

        print(f"Zvolený experiment: {selected_exp}")
        print("Vybrané modely:", selected_models)
        # Tady můžeš doplnit dotazy do DB, výpočty, atd.
        
        with self.engine.connect() as conn:
            # Získání ID experimentu
            exp_result = conn.execute(text("SELECT id FROM Experiment WHERE name = :name"), {"name": selected_exp})
            exp_id = exp_result.fetchone()[0]

            for model_name in selected_models:
                # Získání ID modelu
                model_result = conn.execute(text("SELECT id FROM Model WHERE name = :name"), {"name": model_name})
                model_id = model_result.fetchone()[0]

                # Vložení výsledku do tabulky Result
                conn.execute(
                    text("INSERT INTO Result (model_id, experiment_id, value) VALUES (:model_id, :experiment_id, :value)"),
                    {"model_id": model_id, "experiment_id": exp_id, "value": 0.0}  # Zde můžeš nastavit hodnotu
                )
            conn.commit()
        

    def validate_and_create(self):
        name = self.experiment_name_entry.get().strip()
        desc = self.experiment_desc_entry.get().strip()

        # Validace pomocí regexu – jen písmena, čísla a mezery povoleny
        pattern = r'^[A-Za-z0-9ěščřžýáíéúůĚŠČŘŽÝÁÍÉÚŮ\s]+$'

        if not name or not re.match(pattern, name):
            self.error_label.config(text="Neplatné jméno experimentu – pouze písmena, čísla a mezery.")
            return
        if not desc or not re.match(pattern, desc):
            self.error_label.config(text="Neplatný popis – pouze písmena, čísla a mezery.")
            return

        # Pokud vše OK
        self.error_label.config(text="")  # Vymaže chybovou hlášku
        self.CreateExperiment(name, desc)
    
    def validate_and_create_model(self):
        name = self.model_name_entry.get().strip()
        desc = self.model_desc_entry.get().strip()
        type = self.model_type_entry.get(tk.ACTIVE)
        param1 = self.model_param1_entry.get().strip()
        param2 = self.model_param2_entry.get().strip()
        param3 = self.model_param3_entry.get().strip()
        # Validace pomocí regexu – jen písmena, čísla a mezery povoleny
        pattern = r'^[A-Za-z0-9ěščřžýáíéúůĚŠČŘŽÝÁÍÉÚŮ\s]+$'
        pattern_float = r'^[+-]?([0-9]*[.])?[0-9]+$'
        if not name or not re.match(pattern, name):
            self.model_error_label.config(text="Neplatné jméno modelu – pouze písmena, čísla a mezery.")
            return
        if not desc or not re.match(pattern, desc):
            self.model_error_label.config(text="Neplatný popis – pouze písmena, čísla a mezery.")
            return
        if not type:
            self.model_error_label.config(text="Neplatný typ modelu – vyberte typ z nabídky.")
            return
        if not param1 or not re.match(pattern_float, param1):
            self.model_error_label.config(text="Neplatný parametr 1 – pouze čísla.")
            return
        if not param2 or not re.match(pattern_float, param2):
            self.model_error_label.config(text="Neplatný parametr 2 – pouze čísla.")
            return
        if not param3 or not re.match(pattern_float, param3):
            self.model_error_label.config(text="Neplatný parametr 3 – pouze čísla.")
            return
        # Pokud vše OK
        self.model_error_label.config(text="")
        self.CreateModel(name, desc, type, param1, param2, param3)
        
    def CreateModel(self, name, desc, type_model, param1, param2, param3):
        print(f"Založen model: {name}, popis: {desc}, typ: {type_model}, parametry: {param1}, {param2}, {param3}")
        # Tady si to můžeš napojit na databázi nebo co chceš
        
        with self.engine.connect() as conn:
            conn.execute(
                text("INSERT INTO Model (name, description, type, param1, param2, param3) VALUES (:name, :description, :type, :param1, :param2, :param3)"),
                {"name": name, "description": desc, "type": type_model, "param1": float(param1), "param2": float(param2), "param3": float(param3)}
            )
            conn.commit()

    def CreateExperiment(self, name, desc):
        print(f"Založen experiment: {name}, popis: {desc}")
        # Tady si to můžeš napojit na databázi nebo co chceš
        
        with self.engine.connect() as conn:
            conn.execute(
                text("INSERT INTO Experiment (name, description) VALUES (:name, :description)"),
                {"name": name, "description": desc}
            )
            conn.commit()
        
        
    def load_model_types(self):
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT type FROM TypeModel"))
            return [row[0] for row in result]

        
TheApp = App()