import os
import google.generativeai as genai
from datetime import datetime

# 1. Configurazione API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Errore: GEMINI_API_KEY non trovata.")
    exit(1)

genai.configure(api_key=api_key)

def leggi_prossimo_titolo():
    if not os.path.exists("topics.txt"): return None
    with open("topics.txt", "r", encoding="utf-8") as f:
        linee = f.readlines()
    if not linee: return None
    titolo = linee[0].strip()
    with open("topics.txt", "w", encoding="utf-8") as f:
        f.writelines(linee[1:])
    return titolo

def genera_contenuto(titolo):
    # Usiamo il modello Flash 1.5 che è il più stabile per le quote gratuite
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Scrivi un articolo per un blog tecnico su: "{titolo}".
    REGOLE MANDATORIE:
    1. Stile asciutto, diretto e professionale.
    2. Usa SOLO punteggiatura italiana standard.
    3. NON usare mai il simbolo — (trattino lungo). Sostituiscilo con virgole.
    4. Formato Markdown.
    """
    
    response = model.generate_content(prompt)
    testo = response.text
    # Pulizia finale per sicurezza
    return testo.replace("—", ",").replace("–", ",")

# --- Esecuzione ---
titolo = leggi_prossimo_titolo()
if titolo:
    print(f"Generazione articolo: {titolo}")
    try:
        contenuto = genera_contenuto(titolo)
        data_iso = datetime.now().strftime("%Y-%m-%d")
        slug = titolo.replace(" ", "-").lower().replace("'", "-").replace("?", "")
        nome_file = f"{data_iso}-{slug}.md"
        
        with open(nome_file, "w", encoding="utf-8") as f:
            f.write(f"---\nlayout: post\ntitle: \"{titolo}\"\ndate: {data_iso}\n---\n\n")
            f.write(contenuto)
        print(f"Successo: {nome_file} creato.")
    except Exception as e:
        print(f"Errore durante la generazione: {e}")
        # Se fallisce, rimettiamo il titolo nel file per non perderlo
        with open("topics.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{titolo}")
else:
    print("Nessun titolo in topics.txt")
