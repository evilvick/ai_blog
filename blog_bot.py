import os
from google import genai
from datetime import datetime

# 1. Configurazione API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Errore: GEMINI_API_KEY non trovata.")
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
    # Usiamo il nome esatto trovato nei log diagnostici
    modelli_da_provare = ["gemini-3.1-flash-lite-preview", "gemini-3-flash-preview"]
    
    ultimo_errore = None
    for nome_modello in modelli_da_provare:
        try:
            print(f"Tentativo con modello: {nome_modello}...")
            prompt = f"""
            Scrivi un post per un blog su: "{titolo}".
            REGOLE:
            - Tono asciutto e professionale.
            - Solo punteggiatura italiana standard.
            - MAI usare il simbolo — (trattino lungo).
            - Formato: Markdown.
            """
            response = client.models.generate_content(model=nome_modello, contents=prompt)
            # Pulizia trattini lunghi
            return response.text.replace("—", ",").replace("–", ",")
        except Exception as e:
            print(f"Modello {nome_modello} non disponibile: {e}")
            ultimo_errore = e
            continue
    
    raise ultimo_errore

# --- Esecuzione ---
titolo_scelto = leggi_prossimo_titolo()

if titolo_scelto:
    try:
        contenuto = genera_contenuto(titolo_scelto)
        data_oggi = datetime.now().strftime("%Y-%m-%d")
        slug = titolo_scelto.replace(" ", "-").lower().replace("'", "-").replace("?", "")
        nome_file = f"{data_oggi}-{slug}.md"
        
        with open(nome_file, "w", encoding="utf-8") as f:
            f.write(f"---\nlayout: post\ntitle: \"{titolo_scelto}\"\ndate: {data_oggi}\n---\n\n")
            f.write(contenuto)
        print(f"Creato con successo: {nome_file}")
    except Exception as e:
        print(f"Fallimento totale: {e}")
        with open("topics.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{titolo_scelto}")
        exit(1)
