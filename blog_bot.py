import os
from google import genai
from datetime import datetime

# 1. Configurazione - Recupero la chiave dai segreti di GitHub
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Errore: GEMINI_API_KEY non trovata.")
    exit(1)

# Inizializzazione del client moderno (2026)
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
    # Usiamo il modello 'Lite' che ha molta più disponibilità gratuita
    nome_modello = "gemini-2.0-flash-lite"
    
    prompt = f"""
    Scrivi un post per un blog su: "{titolo}".
    
    VINCOLI STILISTICI (MANDATORI):
    - Tono asciutto, autentico e professionale.
    - Usa solo la punteggiatura italiana standard.
    - NON usare mai il simbolo — (trattino lungo). Sostituiscilo con virgole.
    - Formato di uscita: Markdown.
    """
    
    response = client.models.generate_content(
        model=nome_modello,
        contents=prompt
    )
    
    # Pulizia finale anti-trattino lungo
    return response.text.replace("—", ",").replace("–", ",")

# --- Esecuzione ---
titolo_scelto = leggi_prossimo_titolo()

if titolo_scelto:
    print(f"Generazione in corso per: {titolo_scelto}")
    try:
        contenuto_ai = genera_contenuto(titolo_scelto)
        data_oggi = datetime.now().strftime("%Y-%m-%d")
        
        # Pulizia slug per il nome file
        slug = titolo_scelto.replace(" ", "-").lower().replace("'", "-").replace("?", "")
        nome_file = f"{data_oggi}-{slug}.md"
        
        with open(nome_file, "w", encoding="utf-8") as f:
            f.write(f"---\nlayout: post\ntitle: \"{titolo_scelto}\"\ndate: {data_oggi}\n---\n\n")
            f.write(contenuto_ai)
        print(f"Successo: creato {nome_file}")
        
    except Exception as e:
        print(f"Errore: {e}")
        # Rimettiamo il titolo nel file per non perderlo
        with open("topics.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{titolo_scelto}")
        exit(1)
else:
    print("Nessun titolo trovato.")
