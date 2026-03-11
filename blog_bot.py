import os
from google import genai
from datetime import datetime

# 1. Configurazione API
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Errore: GEMINI_API_KEY non trovata nei segreti del repository.")
    exit(1)

client = genai.Client(api_key=api_key)

def leggi_prossimo_titolo():
    """Legge il titolo da topics.txt e lo rimuove"""
    if not os.path.exists("topics.txt"):
        print("Errore: topics.txt non trovato.")
        return None
    
    with open("topics.txt", "r", encoding="utf-8") as f:
        linee = f.readlines()
    
    if not linee:
        print("Nessun titolo rimasto.")
        return None
    
    titolo = linee[0].strip()
    
    with open("topics.txt", "w", encoding="utf-8") as f:
        f.writelines(linee[1:])
    
    return titolo

def genera_contenuto(titolo):
    """Chiede a Gemini di scrivere l'articolo"""
    prompt = f"""
    Scrivi un articolo per un blog su: "{titolo}".
    REGOLE:
    - Stile asciutto, professionale e senza fronzoli.
    - Usa solo punteggiatura italiana standard.
    - NON usare mai il simbolo — (trattino lungo). Sostituiscilo con virgole.
    - Formato Markdown.
    """
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    
    testo = response.text
    # Pulizia anti-trattino lungo
    return testo.replace("—", ",").replace("–", ",")

# --- Esecuzione Principale ---
titolo = leggi_prossimo_titolo()

if titolo:
    testo_ai = genera_contenuto(titolo)
    
    # RIGA 66 CORRETTA:
    data_iso = datetime.now().strftime("%Y-%m-%d")
    
    slug = titolo.replace(" ", "-").lower().replace("'", "-").replace("?", "")
    nome_file = f"{data_iso}-{slug}.md"
    
    with open(nome_file, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"layout: post\n")
        f.write(f"title: \"{titolo}\"\n")
        f.write(f"date: {data_iso}\n")
        f.write("---\n\n")
        f.write(testo_ai)
    
    print(f"Articolo generato con successo: {nome_file}")
else:
    print("Operazione completata: nessun nuovo titolo da elaborare.")
