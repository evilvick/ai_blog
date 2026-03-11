import os
from google import genai
from datetime import datetime

# 1. Configurazione - Recupero la chiave dai segreti di GitHub
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Errore: GEMINI_API_KEY non trovata nei segreti del repository.")
    exit(1)

# Inizializzazione del nuovo client Google GenAI (versione 2026)
client = genai.Client(api_key=api_key)

def leggi_prossimo_titolo():
    """Prende il primo titolo e aggiorna il file topics.txt"""
    if not os.path.exists("topics.txt"):
        print("Errore: topics.txt non trovato.")
        return None
    
    with open("topics.txt", "r", encoding="utf-8") as f:
        linee = f.readlines()
    
    if not linee:
        print("Nessun titolo rimasto in lista.")
        return None
    
    titolo = linee[0].strip()
    
    # Riscrive il file togliendo la riga appena usata
    with open("topics.txt", "w", encoding="utf-8") as f:
        f.writelines(linee[1:])
    
    return titolo

def genera_contenuto(titolo):
    """Genera il post rispettando rigorosamente lo stile richiesto"""
    prompt = f"""
    Scrivi un articolo per un blog su: "{titolo}".
    
    REGOLE MANDATORIE DI STILE:
    - Tono asciutto, professionale e senza fronzoli.
    - Usa SOLO la punteggiatura italiana standard.
    - NON usare mai il simbolo — (trattino lungo). Sostituiscilo con virgole.
    - Formato: Markdown.
    """
    
    # Utilizziamo 1.5-flash per evitare i limiti di quota della 2.0
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    
    testo = response.text
    
    # Pulizia finale forzata: se Gemini scivola, noi correggiamo.
    return testo.replace("—", ",").replace("–", ",")

# --- Esecuzione ---
titolo_articolo = leggi_prossimo_titolo()

if titolo_articolo:
    print(f"Lavoro sul titolo: {titolo_articolo}")
    contenuto_ai = genera_contenuto(titolo_articolo)
    
    data_iso = datetime.now().strftime("%Y-%m-%d
