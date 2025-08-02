import random
import sqlite3
import csv
from datetime import datetime
# Assicurati di aver installato fpdf2: pip install fpdf2
from fpdf import FPDF

# --- Database Esercizi (Definito in precedenza) ---
ESERCIZI_CON_TIPOLOGIA = {
    'Push': {
        'Petto': [
            {'nome': 'Panca Piana con Bilanciere', 'tipologia': 'Multi-articolare'},
            {'nome': 'Spinte con Manubri su Panca (piana, inclinata, declinata)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Dip alle Parallele (focus petto)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Croci ai Cavi (dal basso, altezza spalle, dall\'alto)', 'tipologia': 'Isolamento'},
            {'nome': 'Chest Press Machine (inclinata o piana)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Pectoral Machine (o Peck Deck)', 'tipologia': 'Isolamento'},
            {'nome': 'Piegamenti sulle braccia (Push-ups, anche zavorrati)', 'tipologia': 'Multi-articolare'}
        ],
        'Spalle': [
            {'nome': 'Overhead Press (con Bilanciere o Manubri)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Arnold Press con Manubri', 'tipologia': 'Multi-articolare'},
            {'nome': 'Alzate Laterali con Manubri', 'tipologia': 'Isolamento'},
            {'nome': 'Shoulder Press Machine', 'tipologia': 'Multi-articolare'},
            {'nome': 'Alzate Laterali al Cavo Singolo', 'tipologia': 'Isolamento'},
            {'nome': 'Alzate Frontali con manubri o al cavo', 'tipologia': 'Isolamento'},
            {'nome': 'Alzate a Y su panca inclinata (Y-Raises)', 'tipologia': 'Multi-articolare'}
        ],
        'Tricipiti': [
            {'nome': 'Panca Piana a Presa Stretta (Close-Grip Bench Press)', 'tipologia': 'Multi-articolare'},
            {'nome': 'French Press con Bilanciere EZ (o Skull Crusher)', 'tipologia': 'Isolamento'},
            {'nome': 'Pushdown ai Cavi (con asta o corda)', 'tipologia': 'Isolamento'},
            {'nome': 'Overhead Extension (con manubrio singolo, due mani o al cavo)', 'tipologia': 'Isolamento'},
            {'nome': 'Dip Machine', 'tipologia': 'Multi-articolare'},
            {'nome': 'Kickback al cavo singolo (o con manubrio)', 'tipologia': 'Isolamento'}
        ]
    },
    'Pull': {
        'Dorso': [
            {'nome': 'Trazioni alla Sbarra (presa prona/larga, supina/stretta, neutra)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Stacco da Terra (convenzionale o sumo)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Rematore con Bilanciere (Pendlay Row o Yates Row)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Lat Machine (con varie prese)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Pulley Basso (o Seated Row Machine)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Rematore con Manubrio Singolo', 'tipologia': 'Multi-articolare'},
            {'nome': 'High Row Machine (o Rematore a gomiti larghi)', 'tipologia': 'Multi-articolare'},
            {'nome': 'T-Bar Row', 'tipologia': 'Multi-articolare'},
            {'nome': 'Pullover (con manubrio o al cavo alto)', 'tipologia': 'Isolamento'},
            {'nome': 'Face Pull', 'tipologia': 'Multi-articolare'}
        ],
        'Bicipiti': [
            {'nome': 'Curl con Bilanciere', 'tipologia': 'Isolamento'},
            {'nome': 'Curl con Manubri (in piedi o seduto, anche alternato)', 'tipologia': 'Isolamento'},
            {'nome': 'Curl a Martello con Manubri (Hammer Curl)', 'tipologia': 'Isolamento'},
            {'nome': 'Curl di Concentrazione', 'tipologia': 'Isolamento'},
            {'nome': 'Panca Scott (con bilanciere, manubri o macchina)', 'tipologia': 'Isolamento'},
            {'nome': 'Curl ai Cavi (dal basso, con barra o corda)', 'tipologia': 'Isolamento'}
        ]
    },
    'Legs': {
        'Quadricipiti': [
            {'nome': 'Back Squat con Bilanciere', 'tipologia': 'Multi-articolare'},
            {'nome': 'Front Squat', 'tipologia': 'Multi-articolare'},
            {'nome': 'Goblet Squat', 'tipologia': 'Multi-articolare'},
            {'nome': 'Leg Press 45°', 'tipologia': 'Multi-articolare'},
            {'nome': 'Affondi (con manubri o bilanciere, statici o in camminata)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Affondi Bulgari (Bulgarian Split Squat)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Leg Extension', 'tipologia': 'Isolamento'},
            {'nome': 'Hack Squat Machine', 'tipologia': 'Multi-articolare'},
            {'nome': 'Sissy Squat', 'tipologia': 'Multi-articolare'}
        ],
        'Femorali/Glutei': [
            {'nome': 'Stacchi Rumeni (con Bilanciere o Manubri)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Hip Thrust con bilanciere', 'tipologia': 'Multi-articolare'},
            {'nome': 'Good Morning con bilanciere', 'tipologia': 'Multi-articolare'},
            {'nome': 'Lying Leg Curl', 'tipologia': 'Isolamento'},
            {'nome': 'Seated Leg Curl', 'tipologia': 'Isolamento'},
            {'nome': 'Glute Machine (o Kickbacks al cavo)', 'tipologia': 'Isolamento'},
            {'nome': 'Hyperextension (focus glutei o femorali)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Glute-Ham Raise (GHR)', 'tipologia': 'Multi-articolare'}
        ],
        'Polpacci': [
            {'nome': 'Calf Raise in piedi (Multipower o macchina specifica)', 'tipologia': 'Isolamento'},
            {'nome': 'Seated Calf Raise Machine', 'tipologia': 'Isolamento'},
            {'nome': 'Calf Press alla Leg Press', 'tipologia': 'Isolamento'}
        ]
    },
    'Core': {
        'Stabilità (Anti-Estensione/Flessione Laterale)': [
            {'nome': 'Plank (con varianti: con sovraccarico, laterale, etc.)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Ab Wheel (Ruota per addominali)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Pallof Press', 'tipologia': 'Multi-articolare'},
            {'nome': 'Farmer\'s Walk (Camminata con pesi)', 'tipologia': 'Multi-articolare'}
        ],
        'Flessione Addominale': [
            {'nome': 'Crunch a terra (con o senza sovraccarico)', 'tipologia': 'Isolamento'},
            {'nome': 'Cable Crunch in ginocchio', 'tipologia': 'Isolamento'},
            {'nome': 'Leg Raises (alla sbarra, alle parallele o a terra)', 'tipologia': 'Multi-articolare'}
        ],
        'Rotazione': [
            {'nome': 'Russian Twist con peso (eseguito lentamente)', 'tipologia': 'Multi-articolare'},
            {'nome': 'Woodchopper al cavo (dall\'alto o dal basso)', 'tipologia': 'Multi-articolare'}
        ]
    }
}


# --- IMPOSTAZIONI DEL PROGRAMMA ---
GOAL = 'Ipertrofia'
SERIE_IPERTROFIA, REPS_IPERTROFIA, RECUPERO_IPERTROFIA = '3-4', '8-12', '60-90s'
SERIE_FORZA, REPS_FORZA, RECUPERO_FORZA = '4-5', '3-5', '120-180s'
ESERCIZI_COMPOSTI_PER_GRUPPO, ESERCIZI_ISOLAMENTO_PER_GRUPPO = 1, 1

# --- FUNZIONI DATABASE ---
def setup_database():
    conn = sqlite3.connect('allenamenti.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schede (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_scheda TEXT NOT NULL,
            data_creazione TIMESTAMP NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS esercizi_scheda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheda_id INTEGER,
            giorno_allenamento TEXT NOT NULL,
            nome_esercizio TEXT NOT NULL,
            tipologia TEXT NOT NULL,
            serie TEXT NOT NULL,
            ripetizioni TEXT NOT NULL,
            recupero TEXT NOT NULL,
            FOREIGN KEY (scheda_id) REFERENCES schede (id)
        )
    ''')
    conn.commit()
    conn.close()

def salva_scheda_su_db(nome_scheda, data_creazione, scheda_data, params):
    conn = sqlite3.connect('allenamenti.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO schede (nome_scheda, data_creazione) VALUES (?, ?)', (nome_scheda, data_creazione))
    scheda_id = cursor.lastrowid
    
    for giorno, esercizi in scheda_data.items():
        for ex in esercizi:
            cursor.execute('''
                INSERT INTO esercizi_scheda (scheda_id, giorno_allenamento, nome_esercizio, tipologia, serie, ripetizioni, recupero)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (scheda_id, giorno, ex['nome'], ex['tipologia'], params['serie'], params['reps'], params['recupero']))
    
    conn.commit()
    conn.close()
    print(f"✅ Scheda '{nome_scheda}' salvata correttamente nel database 'allenamenti.db'.")

# --- FUNZIONI ESPORTAZIONE ---
def crea_pdf_scheda(nome_scheda, scheda_data, params):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, nome_scheda, 0, 1, 'C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, f"Obiettivo: {GOAL}", 0, 1, 'C')
    pdf.ln(5)

    col_widths = [85, 35, 15, 25, 20]

    for giorno, esercizi in scheda_data.items():
        if pdf.get_y() > 240: # Controllo per nuova pagina
             pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, giorno.upper(), 0, 1, 'L')
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(col_widths[0], 8, 'Esercizio', 1, 0, 'C')
        pdf.cell(col_widths[1], 8, 'Tipologia', 1, 0, 'C')
        pdf.cell(col_widths[2], 8, 'Serie', 1, 0, 'C')
        pdf.cell(col_widths[3], 8, 'Ripetizioni', 1, 0, 'C')
        pdf.cell(col_widths[4], 8, 'Recupero', 1, 1, 'C')

        pdf.set_font('Helvetica', '', 9)
        esercizi_ordinati = sorted(esercizi, key=lambda x: x['tipologia'], reverse=True)
        for ex in esercizi_ordinati:
            pdf.cell(col_widths[0], 8, ex['nome'], 1, 0)
            pdf.cell(col_widths[1], 8, ex['tipologia'], 1, 0, 'C')
            pdf.cell(col_widths[2], 8, params['serie'], 1, 0, 'C')
            pdf.cell(col_widths[3], 8, params['reps'], 1, 0, 'C')
            pdf.cell(col_widths[4], 8, params['recupero'], 1, 1, 'C')
        pdf.ln(8)
    
    nome_file_pdf = f"{nome_scheda}.pdf"
    pdf.output(nome_file_pdf)
    print(f"📄 Scheda salvata correttamente nel file PDF: '{nome_file_pdf}'.")

def crea_csv_scheda(nome_scheda, scheda_data, params):
    nome_file_csv = f"{nome_scheda}.csv"
    with open(nome_file_csv, 'w', newline='', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv)
        writer.writerow(['Giorno', 'Esercizio', 'Tipologia', 'Serie', 'Ripetizioni', 'Recupero'])
        for giorno, esercizi in scheda_data.items():
            esercizi_ordinati = sorted(esercizi, key=lambda x: x['tipologia'], reverse=True)
            for ex in esercizi_ordinati:
                writer.writerow([giorno, ex['nome'], ex['tipologia'], params['serie'], params['reps'], params['recupero']])
    print(f"📊 Scheda salvata correttamente nel file CSV: '{nome_file_csv}'.")

# --- LOGICA PRINCIPALE ---
def seleziona_esercizi(categorie, num_composti, num_isolamento):
    esercizi_selezionati = []
    lista_esercizi_completa = []
    for cat in categorie:
        lista_esercizi_completa.extend(cat)

    composti = [e for e in lista_esercizi_completa if e['tipologia'] == 'Multi-articolare']
    isolamento = [e for e in lista_esercizi_completa if e['tipologia'] == 'Isolamento']
    
    num_composti = min(num_composti, len(composti))
    num_isolamento = min(num_isolamento, len(isolamento))

    esercizi_selezionati.extend(random.sample(composti, num_composti))
    esercizi_selezionati.extend(random.sample(isolamento, num_isolamento))
    return esercizi_selezionati

def genera_scheda(frequenza):
    scheda = {}
    
    params = {
        'serie': SERIE_IPERTROFIA if GOAL == 'Ipertrofia' else SERIE_FORZA,
        'reps': REPS_IPERTROFIA if GOAL == 'Ipertrofia' else REPS_FORZA,
        'recupero': RECUPERO_IPERTROFIA if GOAL == 'Ipertrofia' else RECUPERO_FORZA
    }

    split_type = ""
    
    if frequenza == 3:
        split_type = "Full-Body"
        giorni = ['Giorno 1 (Full Body A)', 'Giorno 2 (Full Body B)', 'Giorno 3 (Full Body A)']
        for i, giorno in enumerate(giorni):
            esercizi_giorno = []
            if i == 0 or i == 2:
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Petto']], 1, 0))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Pull']['Dorso']], 1, 0))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Quadricipiti']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Core']['Flessione Addominale']], 1, 0))
            else:
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Femorali/Glutei']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Spalle']], 1, 0))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Pull']['Dorso']], 1, 0))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Core']['Stabilità (Anti-Estensione/Flessione Laterale)']], 1, 0))
            scheda[giorno] = esercizi_giorno

    elif frequenza == 4:
        split_type = "Upper-Lower"
        giorni = ['Giorno 1 (Upper)', 'Giorno 2 (Lower)', 'Giorno 3 (Upper)', 'Giorno 4 (Lower)']
        for i, giorno in enumerate(giorni):
            esercizi_giorno = []
            if 'Upper' in giorno:
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Petto']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Pull']['Dorso']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Spalle']], 1, 0))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Pull']['Bicipiti']], 0, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Tricipiti']], 0, 1))
            else: # Lower
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Quadricipiti']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Femorali/Glutei']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Polpacci']], 0, 1))
                esercizi_giorno.extend(seleziona_esercizi([random.choice(list(ESERCIZI_CON_TIPOLOGIA['Core'].values()))], 1, 0))
            scheda[giorno] = esercizi_giorno

    elif frequenza == 5:
        split_type = "Push-Pull-Legs"
        giorni = ['Giorno 1 (Push)', 'Giorno 2 (Pull)', 'Giorno 3 (Legs)', 'Giorno 4 (Push)', 'Giorno 5 (Pull)']
        for i, giorno in enumerate(giorni):
            esercizi_giorno = []
            if 'Push' in giorno:
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Petto']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Spalle']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Push']['Tricipiti']], 0, 2))
            elif 'Pull' in giorno:
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Pull']['Dorso']], 2, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Pull']['Bicipiti']], 0, 2))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Pull']['Dorso']], 1, 0)) 
            else: # Legs
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Quadricipiti']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Femorali/Glutei']], 1, 1))
                esercizi_giorno.extend(seleziona_esercizi([ESERCIZI_CON_TIPOLOGIA['Legs']['Polpacci']], 0, 2))
                esercizi_giorno.extend(seleziona_esercizi([random.choice(list(ESERCIZI_CON_TIPOLOGIA['Core'].values()))], 1, 0))
            scheda[giorno] = esercizi_giorno
    
    else:
        # Questa parte non verrà eseguita grazie al controllo nell'__main__
        return

    # Stampa a schermo
    print(f"--- SCHEDA DI ALLENAMENTO GENERATA (Obiettivo: {GOAL}) ---\n")
    for giorno, esercizi in scheda.items():
        print(f"========== {giorno.upper()} ==========")
        print(f"{'Esercizio':<60} | {'Tipologia':<20} | {'Serie':<10} | {'Ripetizioni':<12} | {'Recupero':<10}")
        print("-" * 120)
        esercizi_ordinati = sorted(esercizi, key=lambda x: x['tipologia'], reverse=True)
        for ex in esercizi_ordinati:
            print(f"{ex['nome']:<60} | {ex['tipologia']:<20} | {params['serie']:<10} | {params['reps']:<12} | {params['recupero']:<10}")
        print("\n")


    # --- SALVATAGGIO SU FILE E DB ---
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    nome_scheda_file = f"./tmp/Scheda_{split_type}_{timestamp}"
    
    print("\n--- INIZIO SALVATAGGIO ---")
    setup_database()
    salva_scheda_su_db(nome_scheda_file, now, scheda, params)
    crea_pdf_scheda(nome_scheda_file, scheda, params)
    crea_csv_scheda(nome_scheda_file, scheda, params)
    print("--- SALVATAGGIO COMPLETATO ---")


# --- ESECUZIONE SCRIPT ---
if __name__ == '__main__':
    try:
        frequenza_scelta = int(input("Inserisci la frequenza di allenamento settimanale (3, 4 o 5): "))
        if frequenza_scelta in [3, 4, 5]:
            genera_scheda(frequenza_scelta)
        else:
            print("Valore non valido. Scegli tra 3, 4 o 5.")
    except ValueError:
        print("Input non valido. Per favore inserisci un numero.")