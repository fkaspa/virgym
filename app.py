from fasthtml.common import *
from main import genera_scheda, gestisci_infortuni, INFORTUNI_COMUNI, genera_esercizi_riabilitazione, ESERCIZI_CON_TIPOLOGIA
import os
import tempfile
import json

app, rt = fast_app(live=True)

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
                H2("Selezione Gruppi Muscolari"),
                P("Clicca sui gruppi muscolari che vuoi allenare:"),
                Div(
                    Div(
                        Button("Fronte", id="front-btn", onclick="showFront()", style="margin-right: 10px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px;"),
                        Button("Retro", id="back-btn", onclick="showBack()", style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px;"),
                        create_body_diagram(),
                        style="text-align: center; margin: 20px 0;"
                    ),
                    Div(
                        H4("Gruppi Selezionati:"),
                        Div(id="selected-muscles", style="min-height: 40px; padding: 10px; background: #f8f9fa; border-radius: 5px; margin: 10px 0;"),
                        Button("Salva Selezione", id="save-selection", onclick="saveSelection()", style="margin-right: 10px;"),
                        Button("Reset", onclick="resetSelection()"),
                        style="margin-top: 20px;"
                    )
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
            
            muscle_selection_script(),
            
            style="max-width: 1000px; margin: 0 auto; padding: 20px;"
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

@rt("/save-muscles", methods=["POST"])
def post(muscles: list):
    try:
        # Save muscle selection (you can extend this to generate custom workouts)
        print(f"Gruppi muscolari selezionati: {muscles}")
        
        # Here you could integrate with your existing workout generation logic
        # For example, filter exercises based on selected muscle groups
        
        return {"status": "success", "message": f"Selezione salvata: {', '.join(muscles)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

def create_body_diagram():
    return Div(
        # Front View
        Div(
            NotStr('''
            <svg id="front-view" width="350" height="600" viewBox="0 0 350 600" style="border: 1px solid #ccc; border-radius: 10px;">
                <!-- Head -->
                <ellipse cx="175" cy="50" rx="30" ry="35" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Neck -->
                <rect x="160" y="80" width="30" height="25" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Torso -->
                <path d="M120 105 Q175 100 230 105 L240 200 Q175 210 110 200 Z" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Chest (Petto) -->
                <ellipse cx="150" cy="140" rx="25" ry="20" fill="#e8f4fd" stroke="#007bff" stroke-width="2" 
                         class="muscle-group" data-muscle="Petto" style="cursor: pointer;"/>
                <ellipse cx="200" cy="140" rx="25" ry="20" fill="#e8f4fd" stroke="#007bff" stroke-width="2" 
                         class="muscle-group" data-muscle="Petto" style="cursor: pointer;"/>
                <text x="175" y="145" text-anchor="middle" font-size="12" font-weight="bold">PETTO</text>
                
                <!-- Shoulders (Spalle) -->
                <ellipse cx="105" cy="125" rx="25" ry="20" fill="#fff3cd" stroke="#ffc107" stroke-width="2" 
                         class="muscle-group" data-muscle="Spalle" style="cursor: pointer;"/>
                <ellipse cx="245" cy="125" rx="25" ry="20" fill="#fff3cd" stroke="#ffc107" stroke-width="2" 
                         class="muscle-group" data-muscle="Spalle" style="cursor: pointer;"/>
                <text x="105" y="130" text-anchor="middle" font-size="10" font-weight="bold">SPALLE</text>
                <text x="245" y="130" text-anchor="middle" font-size="10" font-weight="bold">SPALLE</text>
                
                <!-- Abs (Core) -->
                <rect x="150" y="170" width="50" height="60" rx="8" fill="#f8d7da" stroke="#dc3545" stroke-width="2" 
                      class="muscle-group" data-muscle="Core" style="cursor: pointer;"/>
                <line x1="160" y1="185" x2="190" y2="185" stroke="#dc3545" stroke-width="1"/>
                <line x1="160" y1="200" x2="190" y2="200" stroke="#dc3545" stroke-width="1"/>
                <line x1="160" y1="215" x2="190" y2="215" stroke="#dc3545" stroke-width="1"/>
                <text x="175" y="205" text-anchor="middle" font-size="12" font-weight="bold">ABS</text>
                
                <!-- Arms -->
                <ellipse cx="80" cy="150" rx="15" ry="40" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="270" cy="150" rx="15" ry="40" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Biceps -->
                <ellipse cx="80" cy="135" rx="12" ry="18" fill="#d4edda" stroke="#28a745" stroke-width="2" 
                         class="muscle-group" data-muscle="Bicipiti" style="cursor: pointer;"/>
                <ellipse cx="270" cy="135" rx="12" ry="18" fill="#d4edda" stroke="#28a745" stroke-width="2" 
                         class="muscle-group" data-muscle="Bicipiti" style="cursor: pointer;"/>
                <text x="80" y="140" text-anchor="middle" font-size="8" font-weight="bold">BIC</text>
                <text x="270" y="140" text-anchor="middle" font-size="8" font-weight="bold">BIC</text>
                
                <!-- Forearms -->
                <ellipse cx="75" cy="200" rx="12" ry="35" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="275" cy="200" rx="12" ry="35" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Legs -->
                <ellipse cx="155" cy="280" rx="20" ry="60" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="195" cy="280" rx="20" ry="60" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Quadriceps -->
                <ellipse cx="155" cy="260" rx="18" ry="35" fill="#e2e3e5" stroke="#6c757d" stroke-width="2" 
                         class="muscle-group" data-muscle="Quadricipiti" style="cursor: pointer;"/>
                <ellipse cx="195" cy="260" rx="18" ry="35" fill="#e2e3e5" stroke="#6c757d" stroke-width="2" 
                         class="muscle-group" data-muscle="Quadricipiti" style="cursor: pointer;"/>
                <text x="175" y="265" text-anchor="middle" font-size="10" font-weight="bold">QUAD</text>
                
                <!-- Lower legs -->
                <ellipse cx="155" cy="380" rx="15" ry="50" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="195" cy="380" rx="15" ry="50" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Calves -->
                <ellipse cx="155" cy="370" rx="12" ry="30" fill="#fff2cc" stroke="#d6b656" stroke-width="2" 
                         class="muscle-group" data-muscle="Polpacci" style="cursor: pointer;"/>
                <ellipse cx="195" cy="370" rx="12" ry="30" fill="#fff2cc" stroke="#d6b656" stroke-width="2" 
                         class="muscle-group" data-muscle="Polpacci" style="cursor: pointer;"/>
                <text x="175" y="375" text-anchor="middle" font-size="10" font-weight="bold">POLPACCI</text>
            </svg>
            '''),
            id="front-view"
        ),
        
        # Back View
        Div(
            NotStr('''
            <svg id="back-view" width="350" height="600" viewBox="0 0 350 600" style="border: 1px solid #ccc; border-radius: 10px; display: none;">
                <!-- Head -->
                <ellipse cx="175" cy="50" rx="30" ry="35" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Neck -->
                <rect x="160" y="80" width="30" height="25" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Torso -->
                <path d="M120 105 Q175 100 230 105 L240 200 Q175 210 110 200 Z" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Upper Back (Dorso) -->
                <ellipse cx="175" cy="140" rx="45" ry="30" fill="#d1ecf1" stroke="#17a2b8" stroke-width="2" 
                         class="muscle-group" data-muscle="Dorso" style="cursor: pointer;"/>
                <text x="175" y="145" text-anchor="middle" font-size="12" font-weight="bold">DORSO</text>
                
                <!-- Shoulders (Spalle) -->
                <ellipse cx="105" cy="125" rx="25" ry="20" fill="#fff3cd" stroke="#ffc107" stroke-width="2" 
                         class="muscle-group" data-muscle="Spalle" style="cursor: pointer;"/>
                <ellipse cx="245" cy="125" rx="25" ry="20" fill="#fff3cd" stroke="#ffc107" stroke-width="2" 
                         class="muscle-group" data-muscle="Spalle" style="cursor: pointer;"/>
                <text x="105" y="130" text-anchor="middle" font-size="10" font-weight="bold">SPALLE</text>
                <text x="245" y="130" text-anchor="middle" font-size="10" font-weight="bold">SPALLE</text>
                
                <!-- Lower Back -->
                <rect x="150" y="170" width="50" height="40" rx="8" fill="#d1ecf1" stroke="#17a2b8" stroke-width="2" 
                      class="muscle-group" data-muscle="Dorso" style="cursor: pointer;"/>
                
                <!-- Arms -->
                <ellipse cx="80" cy="150" rx="15" ry="40" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="270" cy="150" rx="15" ry="40" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Triceps -->
                <ellipse cx="80" cy="160" rx="10" ry="20" fill="#ffeaa7" stroke="#fdcb6e" stroke-width="2" 
                         class="muscle-group" data-muscle="Tricipiti" style="cursor: pointer;"/>
                <ellipse cx="270" cy="160" rx="10" ry="20" fill="#ffeaa7" stroke="#fdcb6e" stroke-width="2" 
                         class="muscle-group" data-muscle="Tricipiti" style="cursor: pointer;"/>
                <text x="80" y="165" text-anchor="middle" font-size="8" font-weight="bold">TRI</text>
                <text x="270" y="165" text-anchor="middle" font-size="8" font-weight="bold">TRI</text>
                
                <!-- Forearms -->
                <ellipse cx="75" cy="200" rx="12" ry="35" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="275" cy="200" rx="12" ry="35" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Glutes -->
                <ellipse cx="155" cy="240" rx="20" ry="25" fill="#f1c0e8" stroke="#e83e8c" stroke-width="2" 
                         class="muscle-group" data-muscle="Femorali/Glutei" style="cursor: pointer;"/>
                <ellipse cx="195" cy="240" rx="20" ry="25" fill="#f1c0e8" stroke="#e83e8c" stroke-width="2" 
                         class="muscle-group" data-muscle="Femorali/Glutei" style="cursor: pointer;"/>
                <text x="175" y="245" text-anchor="middle" font-size="10" font-weight="bold">GLUTEI</text>
                
                <!-- Legs -->
                <ellipse cx="155" cy="300" rx="20" ry="50" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="195" cy="300" rx="20" ry="50" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Hamstrings -->
                <ellipse cx="155" cy="290" rx="18" ry="30" fill="#f1c0e8" stroke="#e83e8c" stroke-width="2" 
                         class="muscle-group" data-muscle="Femorali/Glutei" style="cursor: pointer;"/>
                <ellipse cx="195" cy="290" rx="18" ry="30" fill="#f1c0e8" stroke="#e83e8c" stroke-width="2" 
                         class="muscle-group" data-muscle="Femorali/Glutei" style="cursor: pointer;"/>
                <text x="175" y="295" text-anchor="middle" font-size="9" font-weight="bold">FEMORALI</text>
                
                <!-- Lower legs -->
                <ellipse cx="155" cy="380" rx="15" ry="50" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                <ellipse cx="195" cy="380" rx="15" ry="50" fill="#fdbcb4" stroke="#333" stroke-width="2"/>
                
                <!-- Calves -->
                <ellipse cx="155" cy="370" rx="12" ry="30" fill="#fff2cc" stroke="#d6b656" stroke-width="2" 
                         class="muscle-group" data-muscle="Polpacci" style="cursor: pointer;"/>
                <ellipse cx="195" cy="370" rx="12" ry="30" fill="#fff2cc" stroke="#d6b656" stroke-width="2" 
                         class="muscle-group" data-muscle="Polpacci" style="cursor: pointer;"/>
                <text x="175" y="375" text-anchor="middle" font-size="10" font-weight="bold">POLPACCI</text>
            </svg>
            '''),
            id="back-view", style="display: none;"
        )
    )

def muscle_selection_script():
    return Script('''
        let selectedMuscles = new Set();
        
        // Load saved selection from localStorage
        function loadSelection() {
            const saved = localStorage.getItem('selectedMuscles');
            if (saved) {
                selectedMuscles = new Set(JSON.parse(saved));
                updateDisplay();
                highlightSelected();
            }
        }
        
        // Save selection to localStorage
        function saveToStorage() {
            localStorage.setItem('selectedMuscles', JSON.stringify([...selectedMuscles]));
        }
        
        // Update the display of selected muscles
        function updateDisplay() {
            const display = document.getElementById('selected-muscles');
            if (selectedMuscles.size === 0) {
                display.innerHTML = '<em>Nessun gruppo muscolare selezionato</em>';
            } else {
                const muscleList = [...selectedMuscles].map(muscle => 
                    `<span style="background: #007bff; color: white; padding: 4px 8px; margin: 2px; border-radius: 4px; display: inline-block;">${muscle}</span>`
                ).join(' ');
                display.innerHTML = muscleList;
            }
        }
        
        // Highlight selected muscles in the diagram
        function highlightSelected() {
            document.querySelectorAll('.muscle-group').forEach(element => {
                const muscle = element.getAttribute('data-muscle');
                if (selectedMuscles.has(muscle)) {
                    element.style.filter = 'brightness(0.7)';
                    element.style.strokeWidth = '3';
                } else {
                    element.style.filter = 'brightness(1)';
                    element.style.strokeWidth = '2';
                }
            });
        }
        
        // Toggle muscle selection
        function toggleMuscle(muscle) {
            if (selectedMuscles.has(muscle)) {
                selectedMuscles.delete(muscle);
            } else {
                selectedMuscles.add(muscle);
            }
            updateDisplay();
            highlightSelected();
            saveToStorage();
        }
        
        // Save selection and send to backend
        async function saveSelection() {
            if (selectedMuscles.size === 0) {
                alert('Seleziona almeno un gruppo muscolare!');
                return;
            }
            
            try {
                const response = await fetch('/save-muscles', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({muscles: [...selectedMuscles]})
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    alert(`✅ ${result.message}`);
                } else {
                    alert(`❌ Errore: ${result.message}`);
                }
            } catch (error) {
                alert(`❌ Errore di connessione: ${error.message}`);
            }
        }
        
        // Reset selection
        function resetSelection() {
            selectedMuscles.clear();
            updateDisplay();
            highlightSelected();
            saveToStorage();
        }
        
        // Toggle between front and back view
        function showFront() {
            document.getElementById('front-view').style.display = 'block';
            document.getElementById('back-view').style.display = 'none';
            document.getElementById('front-btn').style.background = '#007bff';
            document.getElementById('back-btn').style.background = '#6c757d';
        }
        
        function showBack() {
            document.getElementById('front-view').style.display = 'none';
            document.getElementById('back-view').style.display = 'block';
            document.getElementById('front-btn').style.background = '#6c757d';
            document.getElementById('back-btn').style.background = '#007bff';
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers to muscle groups
            document.querySelectorAll('.muscle-group').forEach(element => {
                element.addEventListener('click', function() {
                    const muscle = this.getAttribute('data-muscle');
                    toggleMuscle(muscle);
                });
                
                // Add hover effect
                element.addEventListener('mouseenter', function() {
                    this.style.opacity = '0.8';
                });
                
                element.addEventListener('mouseleave', function() {
                    this.style.opacity = '1';
                });
            });
            
            // Load saved selection
            loadSelection();
        });
    ''')

if __name__ == "__main__":
    serve()