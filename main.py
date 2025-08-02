import csv
import random
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- DATABASE ESERCIZI v4.0 (STRUTTURA SEMPLIFICATA E OTTIMIZZATA) ---

ESERCIZI = {
    'Push': {
        'Petto': [
            'Panca Piana con Bilanciere', 'Spinte con Manubri su Panca Inclinata', 'Dip alle Parallele (focus petto)',
            'Croci ai Cavi (dal basso o dall\'alto)', 'Chest Press Machine (inclinata o piana)', 'Pectoral Machine', 'Spinte su Panca Declinata'
        ],
        'Spalle': [
            'Military Press con Bilanciere', 'Arnold Press con Manubri', 'Alzate Laterali con Manubri', 'Shoulder Press Machine',
            'Alzate Laterali al Cavo Singolo', 'Face Pull', 'Tirate al mento con bilanciere EZ'
        ],
        'Tricipiti': [
            'French Press con Bilanciere EZ','Pushdown ai Cavi con Asta', 'Pushdown ai Cavi con Corda', 'French Press con Manubri', 'Dip Machine','Kickback al cavo singolo'
        ]
    },
    'Pull': {
        'Dorso': [
            'Trazioni alla Sbarra (presa prona)', 'Stacco da Terra (convenzionale o sumo)', 'Rematore con Bilanciere (Pendlay o Yates)',
            'Lat Machine (presa larga)', 'Pulley Basso (o Seated Row Machine)', 'Rematore con Manubrio Singolo', 'High Row Machine', 'Pullover al cavo alto'
        ],
        'Bicipiti': [
            'Curl con Bilanciere', 'Curl a Martello con Manubri (Hammer Curl)', 'Curl di Concentrazione',
            'Panca Scott (con bilanciere o macchina)', 'Biceps Curl Machine', 'Curl ai Cavi dal basso con barra'
        ]
    },
    'Legs': {
        'Quadricipiti': [
            'Back Squat con Bilanciere', 'Front Squat', 'Leg Press 45°', 'Affondi bulgari', 'Leg Extension',
            'Hack Squat Machine', 'Sissy Squat (a corpo libero o assistito)'
        ],
        'Femorali/Glutei': [
            'Stacchi Rumeni con Bilanciere', 'Hip Thrust con bilanciere', 'Lying Leg Curl', 'Seated Leg Curl',
            'Glute Machine (Kickbacks)', 'Good Morning con bilanciere', 'Hyperextension (focus glutei)'
        ],
        'Polpacci': [
            'Calf Raise in piedi (Multipower o macchina)', 'Seated Calf Raise Machine', 'Calf Press alla Leg Press'
        ]
    },
    'Abs': [
        'Cable Crunch in ginocchio', 'Leg Raises alla sbarra (o parallele)', 'Plank (con sovraccarico opzionale)',
        'Russian Twist con peso', 'Woodchopper al cavo'
    ]
}

# --- PARAMETRI DI ALLENAMENTO ---
PARAMETRI_IPERTROFIA = {'serie': '3-4', 'ripetizioni': '8-12', 'recupero': '60-90s'}
PARAMETRI_ABS = {'serie': '3', 'ripetizioni': '15-20 o cedimento', 'recupero': '45-60s'}

# --- FUNZIONI DATABASE ---
def inizializza_db(db_name="storico_schede.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schede (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_creazione TEXT NOT NULL,
        giorni_allenamento INTEGER NOT NULL,
        tipo_split TEXT NOT NULL
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS esercizi_scheda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheda_id INTEGER NOT NULL,
        giorno_nome TEXT NOT NULL,
        esercizio_nome TEXT NOT NULL,
        serie TEXT NOT NULL,
        ripetizioni TEXT NOT NULL,
        recupero TEXT NOT NULL,
        FOREIGN KEY (scheda_id) REFERENCES schede (id)
    );
    ''')
    conn.commit()
    conn.close()

def salva_scheda_su_db(scheda, giorni, nome_split, db_name="storico_schede.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    data_ora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO schede (data_creazione, giorni_allenamento, tipo_split) VALUES (?, ?, ?)",
        (data_ora, giorni, nome_split)
    )
    scheda_id = cursor.lastrowid
    for giorno_nome, esercizi_del_giorno in scheda.items():
        for es in esercizi_del_giorno:
            cursor.execute(
                '''INSERT INTO esercizi_scheda 
                (scheda_id, giorno_nome, esercizio_nome, serie, ripetizioni, recupero) 
                VALUES (?, ?, ?, ?, ?, ?)''',
                (scheda_id, giorno_nome, es['esercizio'], es['serie'], es['ripetizioni'], es['recupero'])
            )
    conn.commit()
    conn.close()
    print(f"✅ Scheda salvata con successo nel database: {db_name} (ID Scheda: {scheda_id})")

# --- FUNZIONI CORE DEL PROGRAMMA ---
def scegli_split(giorni):
    if giorni == 2: return ['Upper', 'Lower'], "Upper/Lower"
    if giorni == 3: return ['Full Body', 'Full Body', 'Full Body'], "Full Body"
    if giorni == 4: return ['Upper', 'Lower', 'Upper', 'Lower'], "Upper/Lower"
    if giorni == 5: return ['Push', 'Pull', 'Legs', 'Upper', 'Lower'], "Push/Pull/Legs + Upper/Lower"
    if giorni == 6: return ['Push', 'Pull', 'Legs', 'Push', 'Pull', 'Legs'], "Push/Pull/Legs (x2)"
    return None, None

def genera_scheda(split_schema):
    scheda = {}
    for i, tipo_giorno in enumerate(split_schema):
        nome_giorno = f"Giorno {i+1} - {tipo_giorno}"
        scheda[nome_giorno] = []
        esercizi_scelti = set()

        # Logica di generazione
        if tipo_giorno in ["Push", "Pull", "Legs"]:
            for gruppo_muscolare, lista_esercizi in ESERCIZI[tipo_giorno].items():
                num_da_scegliere = 2 if gruppo_muscolare in ['Petto', 'Dorso', 'Quadricipiti', 'Femorali/Glutei'] else 1
                if len(lista_esercizi) >= num_da_scegliere:
                    esercizi_scelti.update(random.sample(lista_esercizi, num_da_scegliere))
        
        elif tipo_giorno == "Upper":
            # LOGICA MIGLIORATA: Pesca 1 esercizio da ogni sottogruppo di Push e Pull
            for gruppo in ESERCIZI['Push']:
                esercizi_scelti.add(random.choice(ESERCIZI['Push'][gruppo]))
            for gruppo in ESERCIZI['Pull']:
                esercizi_scelti.add(random.choice(ESERCIZI['Pull'][gruppo]))

        elif tipo_giorno == "Lower":
             # LOGICA MIGLIORATA: Pesca 1-2 esercizi dai sottogruppi di Legs
            for gruppo in ['Quadricipiti', 'Femorali/Glutei']:
                 esercizi_scelti.update(random.sample(ESERCIZI['Legs'][gruppo], 2)) # 2 esercizi per i gruppi principali
            esercizi_scelti.add(random.choice(ESERCIZI['Legs']['Polpacci']))

        elif tipo_giorno == "Full Body":
            esercizi_scelti.add(random.choice(ESERCIZI['Push']['Petto']))
            esercizi_scelti.add(random.choice(ESERCIZI['Pull']['Dorso']))
            esercizi_scelti.add(random.choice(ESERCIZI['Legs']['Quadricipiti']))
            esercizi_scelti.add(random.choice(ESERCIZI['Push']['Spalle']))
            
        # Aggiungi un esercizio per gli addominali nei giorni appropriati
        if tipo_giorno in ['Legs', 'Lower', 'Full Body']:
            esercizi_scelti.add(random.choice(ESERCIZI['Abs']))

        # Assegna serie e ripetizioni a tutti gli esercizi scelti
        for esercizio in list(esercizi_scelti):
            params = PARAMETRI_ABS if esercizio in ESERCIZI.get('Abs', []) else PARAMETRI_IPERTROFIA
            scheda[nome_giorno].append({"esercizio": esercizio, **params})
            
    return scheda

def salva_csv(scheda, filename="./tmp/scheda_allenamento.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Giorno', 'Esercizio', 'Serie', 'Ripetizioni', 'Recupero (s)'])
        for giorno, esercizi in scheda.items():
            for es_info in esercizi:
                writer.writerow([giorno, es_info['esercizio'], es_info['serie'], es_info['ripetizioni'], es_info['recupero']])
    print(f"✅ Scheda salvata con successo in formato CSV: {filename}")

def salva_pdf(scheda, nome_split, filename="./tmp/scheda_allenamento.pdf"):
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'La Tua Scheda di Allenamento', 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Split Settimanale: {nome_split}", 0, 1, 'L')
    pdf.ln(5)
    col_widths = {'esercizio': 80, 'serie': 20, 'rip': 35, 'rec': 30}
    for giorno, esercizi in scheda.items():
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, giorno, 'B', 1, 'L')
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(col_widths['esercizio'], 8, 'Esercizio', 1, 0, 'C')
        pdf.cell(col_widths['serie'], 8, 'Serie', 1, 0, 'C')
        pdf.cell(col_widths['rip'], 8, 'Ripetizioni', 1, 0, 'C')
        pdf.cell(col_widths['rec'], 8, 'Recupero', 1, 1, 'C')
        pdf.set_font('Arial', '', 9)
        for es in esercizi:
            pdf.cell(col_widths['esercizio'], 8, es['esercizio'], 1, 0, 'L')
            pdf.cell(col_widths['serie'], 8, es['serie'], 1, 0, 'C')
            pdf.cell(col_widths['rip'], 8, es['ripetizioni'], 1, 0, 'C')
            pdf.cell(col_widths['rec'], 8, es['recupero'], 1, 1, 'C')
        pdf.ln(8)
    pdf.output(filename)
    print(f"✅ Scheda salvata con successo in formato PDF: {filename}")

def main():
    DB_FILE = "storico_schede.db"
    inizializza_db(DB_FILE)
    print("--- 🏋️ Generatore di Schede di Allenamento v4.0 (Logica Dinamica) 🏋️ ---")
    while True:
        try:
            giorni_input = input("Inserisci il numero di giorni di allenamento a settimana (2-6): ")
            giorni = int(giorni_input)
            if 2 <= giorni <= 6: break
            else: print("Errore: Inserisci un numero compreso tra 2 e 6.")
        except ValueError: print("Errore: Inserisci un numero valido.")

    split_schema, nome_split = scegli_split(giorni)
    if not split_schema: return
        
    print(f"\nPerfetto! Per {giorni} giorni, lo split scelto è: **{nome_split}**.")
    print("Sto generando la tua nuova scheda con selezione dinamica degli esercizi...")
    
    scheda_generata = genera_scheda(split_schema)
    
    salva_csv(scheda_generata)
    salva_pdf(scheda_generata, nome_split)
    salva_scheda_su_db(scheda_generata, giorni, nome_split, DB_FILE)
    
    print("\nBuon allenamento! 💪")

if __name__ == "__main__":
    main()