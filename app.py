from fasthtml.common import *
from main import genera_scheda, gestisci_infortuni, INFORTUNI_COMUNI, genera_esercizi_riabilitazione
import os
import tempfile

app, rt = fast_app()

@rt("/")
def get():
    return Titled("VirGym - Generatore Schede",
        Div(
            H1("🏋️ VirGym - Generatore Automatico di Schede"),
            P("Genera schede di allenamento personalizzate per l'ipertrofia muscolare"),
            
            Div(
                H2("Genera Scheda di Allenamento"),
                Form(
                    Label("Frequenza settimanale:", For="frequenza"),
                    Select(
                        Option("3 giorni (Full-Body)", value="3"),
                        Option("4 giorni (Upper-Lower)", value="4"),
                        Option("5 giorni (Push-Pull-Legs)", value="5"),
                        name="frequenza", id="frequenza", required=True
                    ),
                    Button("Genera Scheda", type="submit"),
                    action="/genera", method="post"
                ),
                style="margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px;"
            ),
            
            Div(
                H2("Gestione Infortuni"),
                Form(
                    Label("Seleziona il problema:", For="infortunio"),
                    Select(
                        *[Option(problema, value=str(num)) for num, problema in INFORTUNI_COMUNI.items()],
                        name="infortunio", id="infortunio", required=True
                    ),
                    Button("Genera Esercizi Riabilitazione", type="submit"),
                    action="/infortuni", method="post"
                ),
                style="margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px;"
            ),
            
            style="max-width: 800px; margin: 0 auto; padding: 20px;"
        )
    )

@rt("/genera", methods=["POST"])
def post(frequenza: int):
    try:
        # Crea directory temporanea per i file
        os.makedirs("./tmp", exist_ok=True)
        
        # Cattura l'output della generazione scheda
        import io
        import sys
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            genera_scheda(frequenza)
        output = f.getvalue()
        
        # Trova i file generati
        import glob
        pdf_files = glob.glob("./tmp/Scheda_*.pdf")
        csv_files = glob.glob("./tmp/Scheda_*.csv")
        
        latest_pdf = max(pdf_files, key=os.path.getctime) if pdf_files else None
        latest_csv = max(csv_files, key=os.path.getctime) if csv_files else None
        
        return Titled("Scheda Generata",
            Div(
                H1("✅ Scheda Generata con Successo!"),
                Pre(output, style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;"),
                
                Div(
                    H3("File Generati:"),
                    P(A("📄 Scarica PDF", href=f"/download/{os.path.basename(latest_pdf)}" if latest_pdf else "#")) if latest_pdf else None,
                    P(A("📊 Scarica CSV", href=f"/download/{os.path.basename(latest_csv)}" if latest_csv else "#")) if latest_csv else None,
                    style="margin: 20px 0;"
                ),
                
                A("← Torna al Menu", href="/", style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;"),
                style="max-width: 1000px; margin: 0 auto; padding: 20px;"
            )
        )
    except Exception as e:
        return Titled("Errore",
            Div(
                H1("❌ Errore nella Generazione"),
                P(f"Errore: {str(e)}"),
                A("← Torna al Menu", href="/"),
                style="max-width: 800px; margin: 0 auto; padding: 20px;"
            )
        )

@rt("/infortuni", methods=["POST"])
def post(infortunio: int):
    try:
        infortunio_nome = INFORTUNI_COMUNI[infortunio]
        
        # Cattura l'output della generazione esercizi
        import io
        import sys
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            genera_esercizi_riabilitazione(infortunio_nome)
        output = f.getvalue()
        
        # Trova il file markdown generato
        import glob
        md_files = glob.glob(f"Riabilitazione_*.md")
        latest_md = max(md_files, key=os.path.getctime) if md_files else None
        
        return Titled("Esercizi di Riabilitazione",
            Div(
                H1(f"🔧 Esercizi per {infortunio_nome}"),
                Pre(output, style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;"),
                
                Div(
                    P(A("📝 Scarica Protocollo (MD)", href=f"/download/{os.path.basename(latest_md)}" if latest_md else "#")) if latest_md else None,
                    style="margin: 20px 0;"
                ),
                
                A("← Torna al Menu", href="/", style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;"),
                style="max-width: 1000px; margin: 0 auto; padding: 20px;"
            )
        )
    except Exception as e:
        return Titled("Errore",
            Div(
                H1("❌ Errore nella Generazione"),
                P(f"Errore: {str(e)}"),
                A("← Torna al Menu", href="/"),
                style="max-width: 800px; margin: 0 auto; padding: 20px;"
            )
        )

@rt("/download/{filename}")
def get(filename: str):
    # Controlla se il file è nella directory tmp o nella root
    file_path = None
    if os.path.exists(f"./tmp/{filename}"):
        file_path = f"./tmp/{filename}"
    elif os.path.exists(filename):
        file_path = filename
    
    if file_path and os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return "File non trovato", 404

if __name__ == "__main__":
    serve()