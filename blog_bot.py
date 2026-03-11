import os
import google.generativeai as genai
from datetime import datetime

# Recupera la chiave dai segreti di GitHub
GENAI_KEY = os.getenv("GEMINI_API_KEY")

if not GENAI_KEY:
    print("Errore: Chiave API non trovata.")
    exit(1)

genai.configure(api_key=GENAI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def leggi_prossimo_titolo():
    if not os.path.exists("topics.txt"):
        return None
    with open("topics.txt", "r", encoding="utf-8") as f:
        linee = f.readlines()
    if not linee:
        return None
    titolo = linee[0].strip()
    with open("topics.txt", "w", encoding="utf-8") as f:
        f.writelines(linee[1:])
    return titolo

def genera_contenuto(titolo):
    prompt = f"""
    Scrivi un articolo per un blog tecnico su: "{titolo}".
    REGOLE: 
    - Stile asciutto e diretto.
    - NON usare mai il simbolo — (trattino lungo). Usa virgole.
    - Formato Markdown.
    """
    response = model.generate_content(prompt)
    testo = response.text
    # Pulizia forzata per i trattini lunghi (sia em-dash che en-dash)
    return testo.replace("—", ",").replace("–", ",")

titolo = leggi_prossimo_titolo()
if titolo:
    testo_ai = genera_contenuto(titolo)
    data_iso = datetime.now().strftime("%Y-%m-%d")
    slug = titolo.replace(" ", "-").lower().replace("'", "-")
    nome_file = f"{data_iso}-{slug}.md"
    
    with open(nome_file, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"layout: post\n")
        f.write(f"title: \"{titolo}\"\n")
        f.write(f"date: {data_iso}\n")
        f.write("---\n\n")
        f.write(testo_ai)
    print(f"Post '{titolo}' creato con successo.")
else:
    print("Nessun titolo trovato in topics.txt")
