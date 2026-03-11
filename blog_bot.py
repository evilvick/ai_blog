import os
import google.generativeai as genai
from datetime import datetime

# 1. Configurazione API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Errore: GEMINI_API_KEY mancante.")
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
    # Proviamo il modello standard per il 2026
    # Se gemini-1.5-flash dà 404, prova con gemini-pro o gemini-1.5-flash-8b
    nome_modello = 'gemini-1.5-flash'
    
    try:
        model = genai.GenerativeModel(nome_modello)
        prompt = f"""
        Scrivi un articolo per un blog tecnico su: "{titolo}".
        REGOLE:
        - Stile asciutto e diretto.
        - Usa solo punteggiatura italiana standard.
        - NON usare mai il simbolo — (trattino lungo). Sostituiscilo con virgole.
        - Formato Markdown.
        """
        response = model.generate_content(prompt)
        return response.text.replace("—", ",").replace("–", ",")
    except Exception as e:
        print(f"Errore con {nome_modello}: {e}")
        print("Controllo modelli disponibili...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Modello disponibile: {m.name}")
        raise e

# --- Esecuzione ---
titolo = leggi_prossimo_titolo()
if titolo:
    try:
        contenuto = genera_contenuto(titolo)
        data_iso = datetime.now().strftime("%Y-%m-%d")
        slug = titolo.replace(" ", "-").lower().replace("'", "-").replace("?", "")
        nome_file = f"{data_iso}-{slug}.md"
        
        with open(nome_file, "w", encoding="utf-8") as f:
            f.write(f"---\nlayout: post\ntitle: \"{titolo}\"\ndate: {data_iso}\n---\n\n")
            f.write(contenuto)
        print(f"OK: Creato {nome_file}")
    except Exception as e:
        # Se fallisce, rimettiamo il titolo nel file
        with open("topics.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{titolo}")
        print("Generazione fallita. Titolo recuperato.")
        exit(1) # Ora forziamo il semaforo ROSSO se fallisce, così lo vediamo subito
