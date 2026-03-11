import os
from google import genai
from datetime import datetime

# 1. Configurazione API
# Recupera la chiave dai Secrets di GitHub
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Errore: GEMINI_API_KEY non trovata nei segreti del repository.")
    exit(1)

# Inizializzazione del client Google GenAI (Versione 2026)
client = genai.Client(api_key=api_key)

def leggi_prossimo_titolo():
    """Legge il primo titolo disponibile in topics.txt e lo rimuove dalla lista"""
    if not os.path.exists("topics.txt"):
        print("Errore: file topics.txt non trovato.")
        return None
    
    with open("topics.txt", "r", encoding="utf-8") as f:
        linee = f.readlines()
    
    if not linee:
        print("La lista dei titoli è vuota.")
        return None
    
    # Prende il primo titolo e pulisce gli spazi
    titolo = linee[0].strip()
    
    # Riscrive il file senza il titolo appena preso
    with open("topics.txt", "w", encoding="utf-8") as f:
        f.writelines(linee[1:])
    
    return titolo

def genera_contenuto(titolo):
    """Genera l'articolo usando il modello con quota sbloccata (3.1 Flash Lite)"""
    
    # Modello identificato dalla diagnostica come funzionante con 500 RPD
    nome_modello = "gemini-3.1-flash-lite"
    
    prompt = f"""
    Scrivi un articolo per un blog su questo argomento: "{titolo}".
    
    REGOLE DI SCRITTURA (DA RISPETTARE RIGOROSAMENTE):
    1. Stile asciutto, professionale e senza giri di parole.
    2. Usa esclusivamente la punteggiatura italiana standard.
    3. NON utilizzare mai il simbolo — (trattino lungo). Sostituiscilo con virgole o parentesi.
    4. Formato: Markdown pulito.
    """
    
    response = client.models.generate_content(
        model=nome_modello,
        contents=prompt
    )
    
    testo = response.text
    
    # Filtro di sicurezza finale per rimuovere eventuali trattini lunghi "scappati" all'AI
    return testo.replace("—", ",").replace("–", ",")

# --- ESECUZIONE ---
titolo_da_scrivere = leggi_prossimo_titolo()

if titolo_da_scrivere:
    print(f"Sto generando il post per: {titolo_da_scrivere}...")
    try:
        contenuto_post = genera_contenuto(titolo_da_scrivere)
        
        data_iso = datetime.now().strftime("%Y-%m-%d")
        # Crea uno slug pulito per il nome del file
        slug = titolo_da_scrivere.replace(" ", "-").lower().replace("'", "-").replace("?", "")
        nome_file = f"{data_iso}-{slug}.md"
        
        # Scrittura del file con intestazione Front Matter per Jekyll/GitHub Pages
        with open(nome_file, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"layout: post\n")
            f.write(f"title: \"{titolo_da_scrivere}\"\n")
            f.write(f"date: {data_iso}\n")
            f.write("---\n\n")
            f.write(contenuto_post)
            
        print(f"Missione compiuta! Creato il file: {nome_file}")
        
    except Exception as e:
        print(f"Errore critico durante la generazione: {e}")
        # Se fallisce, rimettiamo il titolo nel file per non perderlo
        with open("topics.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{titolo_da_scrivere}")
        exit(1)
else:
    print("Niente da fare: aggiungi dei titoli a topics.txt.")
