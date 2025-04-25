# scraper.py
import requests
from bs4 import BeautifulSoup
from lxml import html
import logging
import re

logging.basicConfig(level=logging.INFO)

def normalize_title(title):
    return re.sub(r'[^a-z0-9]+', ' ', title.lower()).strip()

def title_match(search_title, candidate_title):
    search_words = normalize_title(search_title).split()
    candidate_words = normalize_title(candidate_title).split()
    return all(word in candidate_words for word in search_words)

def find_series_page_url(series_title):
    logging.info(f"Cerco pagina serie per: {series_title}")
    search_url = "https://eurostreaming.phd/?s=" + series_title.replace(" ", "+")
    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Utilizza un selettore CSS più robusto
        serie_links = soup.select('div.post-content > h2 > a')

        if serie_links:
            for link in serie_links:  # Itera su tutti i link trovati
                candidate_title = link.text.strip()
                if title_match(series_title, candidate_title):
                    serie_url = link['href']
                    logging.info(f"Trovata pagina serie: {serie_url} (titolo: {candidate_title})")
                    return serie_url

            logging.warning(f"Nessuna pagina compatibile trovata per: {series_title}")
            return None
        else:
            logging.warning(f"Nessuna pagina trovata per: {series_title}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Errore richiesta HTTP: {e}")
        return None
    except Exception as e:
        logging.error(f"Errore durante la ricerca della pagina serie: {e}")
        return None
