import os
from google import genai
from datetime import datetime

# Recupera la chiave dai segreti di GitHub
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Errore: GEMINI_API_KEY non configurata.")
    exit(1)

client = genai.Client(api_key=api_key)

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
    prompt = f"""
    Scrivi un articolo per un blog su: "{titolo}".
    REGOLE MANDATORIE:
    1. Stile asciutto, diretto, professionale.
    2. Usa SOLO punteggiatura italiana standard.
    3. NON usare mai il simbolo — (trattino lungo). Sostituiscilo con virgole.
    4. Formato Markdown.
    """
    # Usiamo il modello più aggiornato del 2026
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    testo = response.text
    # Pulizia di sicurezza finale
    return testo.replace("—", ",").replace("–", ",")

titolo = leggi_prossimo_titolo()
if titolo:
    testo_ai = genera_contenuto(titolo)
    data_str = datetime.now().strftime("%Y-%m-%d")
    slug = titolo.replace(" ", "-").lower().replace("'", "-")
    nome_file = f"{data_str}-{slug}.md"
    
    with open(nome_file, "w", encoding="utf-8") as f:
        f.write(f"---\nlayout: post\ntitle: \"{titolo}\"\ndate: {data_str}\n---\n\n")
        f.write(testo_ai)
    print(f"Creato: {nome_file}")
