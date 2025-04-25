# addon.py
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import re
from eurostream.scraper import find_series_page_url
from eurostream.resolver import extract_streams_from_page
from tmdb.client import search_tmdb, convert_imdb_to_tmdb

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

@app.route('/manifest.json')
def manifest():
    logging.info("Manifest richiesto")
    return jsonify({
        "id": "com.eurostream.search",
        "version": "1.0.1",
        "name": "EuroStreaming Addon",
        "resources": ["stream"],
        "types": ["series"],
        "idPrefixes": ["tt"]
    })

@app.route('/stream/<media_type>/<tmdb_id>.json')
def stream(media_type, tmdb_id):
    logging.info(f"Richiesta stream per type={media_type}, tmdb_id={tmdb_id}")

    if media_type != "series":
        logging.warning(f"Tipo non supportato: {media_type}")
        return jsonify({"streams": []})

    match = re.match(r'^(tt\d+)(?::(\d+):(\d+))?$', tmdb_id)
    if not match:
        logging.error(f"tmdb_id non valido: {tmdb_id}")
        return jsonify({"streams": []})

    imdb_id = match.group(1)
    season = match.group(2)
    episode = match.group(3)

    logging.info(f"ID IMDb estratto: {imdb_id}, stagione: {season}, episodio: {episode}")

    tmdb_numeric_id = convert_imdb_to_tmdb(imdb_id, media_type="series")
    if not tmdb_numeric_id:
        logging.error(f"Conversione IMDb->TMDb fallita per {imdb_id}")
        return jsonify({"streams": []})

    series_title = search_tmdb("series", tmdb_numeric_id)
    if not series_title:
        logging.error("Titolo serie non trovato su TMDb")
        return jsonify({"streams": []})

    serie_page_url = find_series_page_url(series_title)
    if not serie_page_url:
        logging.error("Pagina serie non trovata su EuroStreaming")
        return jsonify({"streams": []})

    streams = extract_streams_from_page(serie_page_url, season=season, episode=episode)
    logging.info(f"Streams trovati: {len(streams)}")

    return jsonify({"streams": streams})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
