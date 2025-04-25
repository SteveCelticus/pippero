# utils/decrypt.py
import requests
from bs4 import BeautifulSoup
import logging
import time

logging.basicConfig(level=logging.INFO)

def decrypt_url(url):
    logging.info(f"Decripto URL: {url}")
    try:
        # Ottieni la pagina di protezione
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Trova il form e i campi necessari
        form = soup.find('form', {'id': 'protector'})
        if not form:
            logging.error("Form 'protector' non trovato.")
            return None

        # Trova l'immagine del captcha
        captcha_img = form.find('img')
        if not captcha_img:
            logging.error("Immagine captcha non trovata.")
            return None

        captcha_url = captcha_img['src']

        # Scarica l'immagine del captcha
        captcha_response = requests.get(captcha_url, stream=True)
        captcha_response.raise_for_status()

        # Richiedi all'utente di risolvere il captcha
        captcha_text = input("Inserisci il testo del captcha: ")

        # Prepara i dati per la richiesta POST
        data = {
            'protect': captcha_text,  # Inserisci la risposta al captcha
        }
        # Aggiungi gli altri campi nascosti dal form
        for input_field in form.find_all('input', type='hidden'):
            data[input_field['name']] = input_field['value']
        time.sleep(5)
        # Invia la richiesta POST per ottenere l'URL decrittato
        decrypted_response = requests.post(url, headers={'User-Agent': 'Mozilla/5.0'}, data=data, allow_redirects=False)
        decrypted_response.raise_for_status()
        
        # Verifica se la risposta è un reindirizzamento
        if 'location' in decrypted_response.headers:
            decrypted_url = decrypted_response.headers['location']
            logging.info(f"URL decrittato: {decrypted_url}")
            return decrypted_url
        else:
            logging.error("Reindirizzamento non trovato nella risposta.")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Errore richiesta HTTP: {e}")
        return None
    except Exception as e:
        logging.error(f"Errore durante la decrittazione dell'URL: {e}")
        return None
