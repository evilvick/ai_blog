import os
import google.generativeai as genai
from datetime import datetime

# 1. Configurazione API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Errore: GEMINI_API_KEY mancante nei Secrets di GitHub.")
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
    # Passiamo al modello 2.0 che risulta disponibile nei tuoi log
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    Scrivi un articolo per un blog tecnico su: "{titolo}".
    REGOLE MANDATORIE:
    - Stile asciutto, diretto e professionale.
    - Usa SOLO punteggiatura italiana standard.
    - NON usare mai il simbolo — (trattino lungo). Sostituiscilo con virgole.
    - Formato Markdown.
    """
    
    response = model.generate_content(prompt)
    testo = response.text
    # Pulizia finale anti-trattino lungo per sicurezza
    return testo.replace("—", ",").replace("–", ",")

# --- Esecuzione ---
titolo = leggi_prossimo_titolo()
if titolo:
    print(f"Generazione articolo in corso per: {titolo}...")
    try:
        contenuto = genera_contenuto(titolo)
        data_iso = datetime.now().strftime("%Y-%m-%d")
        slug = titolo.replace(" ", "-").lower().replace("'", "-").replace("?", "")
        nome_file = f"{data_iso}-{slug}.md"
        
        with open(nome_file, "w", encoding="utf-8") as f:
            f.write(f"---\nlayout: post\ntitle: \"{titolo}\"\ndate: {data_iso}\n---\n\n")
            f.write(contenuto)
        print(f"Successo: creato il file {nome_file}")
    except Exception as e:
        print(f"Errore durante la generazione: {e}")
        # Recupero del titolo in caso di fallimento
        with open("topics.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{titolo}")
        exit(1)
else:
    print("Nessun titolo trovato in topics.txt")
