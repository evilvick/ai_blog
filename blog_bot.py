import os
import google.generativeai as genai
import requests

# Configurazione chiavi dai segreti di GitHub
GENAI_KEY = os.getenv("GEMINI_API_KEY")
MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN")
MEDIUM_USER_ID = os.getenv("MEDIUM_USER_ID")

genai.configure(api_key=GENAI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
    response = model.generate_content(prompt)
    testo = response.text
    # Pulizia di sicurezza per la punteggiatura
    return testo.replace("—", ",").replace("–", ",")

def pubblica(titolo, testo):
    url = f"https://api.medium.com/v1/users/{MEDIUM_USER_ID}/posts"
    headers = {"Authorization": f"Bearer {MEDIUM_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "title": titolo,
        "contentFormat": "markdown",
        "content": f"# {titolo}\n\n{testo}",
        "publishStatus": "draft" # Resta in bozza per tua sicurezza
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.status_code == 201

titolo = leggi_prossimo_titolo()
if titolo:
    testo_ai = genera_contenuto(titolo)
    if pubblica(titolo, testo_ai):
        print(f"Post '{titolo}' inviato con successo alle bozze di Medium!")
