# client.py
import requests
import logging

TMDB_API_KEY = '8b32222ed5da2fa7ff31e7ab08c8f64d'
logging.basicConfig(level=logging.INFO)

def convert_imdb_to_tmdb(imdb_id, media_type="series"):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logging.debug(f"Risposta find IMDb: {data}")
        if media_type == "series" and data.get("tv_results"):
            if len(data["tv_results"]) > 0:
                return data["tv_results"][0]["id"]
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore conversione IMDb->TMDb: {e}")
        return None
    except Exception as e:
        logging.error(f"Errore durante la conversione IMDb->TMDb: {e}")
        return None

def search_tmdb(media_type, tmdb_id):
    logging.info(f"Cerco il titolo della serie con tmdb_id: {tmdb_id}")
    endpoint = "tv" if media_type == "series" else media_type
    search_url = f"https://api.themoviedb.org/3/{endpoint}/{tmdb_id}?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        title = data.get("name")
        logging.info(f"Titolo trovato: {title}")
        return title
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore durante la richiesta HTTP: {e}")
        return None
    except Exception as e:
        logging.error(f"Errore durante la ricerca del titolo su TMDb: {e}")
        return None
