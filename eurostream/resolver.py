import requests
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.INFO)

def extract_streams_from_page(serie_page_url, season=None, episode=None):
    logging.info(f"Estraggo stream da {serie_page_url}, season={season}, episode={episode}")
    streams = []
    try:
        response = requests.get(serie_page_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Seleziona i contenitori che presumibilmente contengono gli episodi
        containers = soup.select(".su-spoiler-content.su-u-clearfix.su-u-trim")

        for container in containers:
            # Estrai tutti i blocchi di testo che contengono link e il codice dell'episodio
            episode_blocks = container.find_all(string=re.compile(r'(\d+×\d+)'))

            for block in episode_blocks:
                # Estrai il codice dell'episodio e il titolo dal blocco di testo
                match = re.search(r'(\d+)×(\d+)\s*([^-]+)\s*–', block, re.IGNORECASE)
                if match:
                    ep_season = int(match.group(1))
                    ep_episode = int(match.group(2))
                    ep_title = match.group(3).strip()

                    # Filtra per stagione ed episodio richiesti
                    if season and episode and (int(season) != ep_season or int(episode) != ep_episode):
                        continue

                    # Trova tutti i link nel blocco di testo corrente
                    links = []
                    next_element = block.find_next()
                    while next_element and next_element.name == 'a':
                        links.append(next_element)
                        next_element = next_element.find_next()
                    for link in links:
                        url = link['href'].strip()
                        if url and any(host in url for host in ["clicka.cc/mix", "uprot.net/msf", "clicka.cc/delta"]):
                            title = link.text.strip() or "Stream"
                            stream_title = f"S{ep_season}E{ep_episode} - {ep_title} - {title}"
                            streams.append({"title": stream_title, "url": url})
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore richiesta HTTP: {e}")
    except Exception as e:
        logging.error(f"Errore durante l'estrazione degli stream: {e}")

    return streams
