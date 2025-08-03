# AutoTrain - Generatore Automatico di Schede di Allenamento

AutoTrain è un'applicazione Python che genera automaticamente schede di allenamento personalizzate per l'ipertrofia muscolare, con valutazione AI e gestione degli infortuni.

## Funzionalità Principali

- **Generazione automatica di schede** per frequenze 3, 4 o 5 giorni settimanali
- **Valutazione AI** delle schede tramite OpenAI GPT-4
- **Gestione infortuni** con esercizi di riabilitazione personalizzati
- **Esportazione multipla** in PDF, CSV e database SQLite
- **Database completo** di esercizi categorizzati per gruppo muscolare

## Installazione

1. Clona il repository
2. Installa le dipendenze:
```bash
pip install fpdf2 openai python-dotenv
```
3. Crea un file `.env` con la tua API key OpenAI:
```
OPENAPI_KEY=your_openai_api_key_here
```

## Utilizzo

Esegui il programma:
```bash
python main.py
```

Seleziona dal menu:
1. **Genera scheda** - Crea una nuova scheda di allenamento
2. **Gestione infortuni** - Ottieni esercizi di riabilitazione
0. **Esci**

## Logica del Programma (main.py)

### Struttura Dati degli Esercizi

Il cuore del programma è il dizionario `ESERCIZI_CON_TIPOLOGIA` che organizza gli esercizi in:
- **Categorie principali**: Push, Pull, Legs, Core
- **Gruppi muscolari**: Petto, Spalle, Tricipiti, Dorso, Bicipiti, ecc.
- **Tipologie**: Multi-articolare (composti) e Isolamento

### Algoritmo di Generazione Schede

La funzione `genera_scheda(frequenza)` implementa tre split diversi:

#### 1. Full-Body (3 giorni)
- **Giorno 1 e 3**: Petto + Dorso + Quadricipiti + Core
- **Giorno 2**: Femorali/Glutei + Spalle + Dorso + Core
- Bilanciamento tra tutti i gruppi muscolari

#### 2. Upper-Lower (4 giorni)
- **Upper**: Petto + Dorso + Spalle + Bicipiti + Tricipiti
- **Lower**: Quadricipiti + Femorali/Glutei + Polpacci + Core
- Separazione parte superiore/inferiore del corpo

#### 3. Push-Pull-Legs (5 giorni)
- **Push**: Petto + Spalle + Tricipiti
- **Pull**: Dorso + Bicipiti
- **Legs**: Quadricipiti + Femorali/Glutei + Polpacci + Core

### Selezione Intelligente degli Esercizi

La funzione `seleziona_esercizi()` garantisce:
- **Priorità ai composti**: Esercizi multi-articolari prima degli isolamenti
- **Bilanciamento**: Numero controllato di esercizi per tipologia
- **Randomizzazione**: Varietà nelle schede generate

### Parametri di Allenamento

Configurazione ottimizzata per l'ipertrofia:
- **Serie**: 3-4
- **Ripetizioni**: 8-12
- **Recupero**: 60-90 secondi

### Valutazione AI

La funzione `valuta_scheda_con_llm()`:
- Invia la scheda generata a GPT-4
- Riceve feedback su bilanciamento muscolare
- Suggerisce correzioni se necessarie
- Include la valutazione nel PDF finale

### Sistema di Persistenza

**Database SQLite** (`allenamenti.db`):
- Tabella `schede`: Metadati delle schede
- Tabella `esercizi_scheda`: Dettagli degli esercizi

**Esportazione multipla**:
- **PDF**: Scheda formattata con valutazione AI
- **CSV**: Dati tabulari per analisi
- **Database**: Storico completo

### Gestione Infortuni

Il modulo infortuni include:
- **10 problemi comuni**: Spalla, gomito, schiena, ginocchio, ecc.
- **Generazione AI**: Esercizi di riabilitazione personalizzati
- **Salvataggio automatico**: File markdown con protocolli

### Architettura del Codice

```
main.py
├── Database esercizi (ESERCIZI_CON_TIPOLOGIA)
├── Configurazione parametri (GOAL, SERIE, REPS)
├── Funzioni database (setup_database, salva_scheda_su_db)
├── Funzioni esportazione (crea_pdf_scheda, crea_csv_scheda)
├── Valutazione AI (valuta_scheda_con_llm)
├── Gestione infortuni (gestisci_infortuni, genera_esercizi_riabilitazione)
├── Logica principale (seleziona_esercizi, genera_scheda)
└── Menu interattivo (menu_principale)
```

### Flusso di Esecuzione

1. **Avvio**: Caricamento configurazione e setup database
2. **Input utente**: Selezione frequenza allenamento
3. **Generazione**: Creazione scheda basata su algoritmo specifico
4. **Valutazione**: Analisi AI della scheda generata
5. **Salvataggio**: Esportazione in tutti i formati
6. **Output**: Visualizzazione risultati e percorsi file

## File Generati

- `Scheda_[TIPO]_[TIMESTAMP].pdf` - Scheda formattata
- `Scheda_[TIPO]_[TIMESTAMP].csv` - Dati esportabili
- `allenamenti.db` - Database persistente
- `Riabilitazione_[INFORTUNIO].md` - Protocolli riabilitativi

## Requisiti

- Python 3.7+
- OpenAI API key
- Librerie: fpdf2, openai, python-dotenv

## Note Tecniche

- **Randomizzazione controllata**: Garantisce varietà mantenendo qualità
- **Validazione input**: Controlli su frequenza e scelte utente
- **Gestione errori**: Try-catch per chiamate API e operazioni I/O
- **Encoding UTF-8**: Supporto completo caratteri italiani