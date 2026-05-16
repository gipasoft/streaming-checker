# streaming-checker

Piccolo container Python per controllare se film/serie mancanti in Radarr/Sonarr sono disponibili in streaming in Italia tramite TMDB Watch Providers, e applicare tag automatici.

## Cosa fa

- Legge Radarr e/o Sonarr via API.
- Considera solo contenuti `monitored` e mancanti.
- Interroga TMDB Watch Providers per `COUNTRY=IT`.
- Aggiunge tag tipo:
  - `available-streaming`
  - `streaming-netflix`
  - `streaming-prime-video`
  - `streaming-disney-plus`
- Normalizza alias e nomi rumorosi dei provider TMDB prima di creare tag/statistiche.
- Rimuove i tag gestiti quando il contenuto non risulta più disponibile, se `REMOVE_STALE_TAGS=true`.
- Salva cronologia scansioni, cache disponibilità e storico notifiche in SQLite.
- Può inviare notifiche ntfy quando cambiano i provider disponibili.
- Di default è in `DRY_RUN=true`, quindi non modifica nulla.

## Requisiti

- API key Radarr
- API key Sonarr, opzionale
- TMDB API Bearer Token

Su TMDB: Settings → API → API Read Access Token.

## Avvio rapido

Copia `.env.example` in `.env` e modifica i valori.

```bash
docker compose up -d
```

La UI web è disponibile su:

```text
http://localhost:8080
```

Per applicare davvero i tag:

```env
DRY_RUN=false
```

## Variabili principali

```env
RADARR_URL=http://radarr:7878
RADARR_API_KEY=xxx

SONARR_URL=http://sonarr:8989
SONARR_API_KEY=xxx

TMDB_BEARER_TOKEN=xxx
COUNTRY=IT

DRY_RUN=true
REMOVE_STALE_TAGS=true
TAG_GENERIC=true
TAG_PROVIDERS=true
GENERIC_TAG=available-streaming
DATABASE_PATH=/data/streaming_checker.sqlite
SCAN_INTERVAL_HOURS=12
RUN_SCAN_ON_STARTUP=true

NTFY_URL=https://ntfy.sh
NTFY_TOPIC=streaming-alerts
NTFY_PRIORITY=default
NTFY_TAGS=tv,streaming
```

## Persistenza SQLite

All'avvio vengono create automaticamente le tabelle SQLite, se mancanti:

- `availability_cache`
- `notification_history`
- `scan_history`

La cache confronta i provider dell'ultima scansione con quelli già noti per ogni contenuto e registra una voce di storico solo per stati non già notificati.

## Scheduler interno

Quando avviato come container web, `streaming-checker` resta in esecuzione e lancia scansioni automatiche con APScheduler.

```env
SCAN_INTERVAL_HOURS=12
RUN_SCAN_ON_STARTUP=true
```

La UI mostra stato scheduler, prossima scansione e ultima scansione. Il bottone manuale resta disponibile e usa lo stesso lock delle scansioni automatiche, quindi due scansioni non si sovrappongono.

## Normalizzazione provider

I provider TMDB vengono normalizzati in nomi canonici prima di tag, cache, statistiche e UI. Alcuni esempi:

- `Amazon Prime Video with Ads` -> `Amazon Prime Video`
- `Prime Video` -> `Amazon Prime Video`
- `Apple TV Amazon Channel` -> `Apple TV+`
- `Paramount+ Amazon Channel` -> `Paramount+`
- `Crunchyroll Amazon Channel` -> `Crunchyroll`

La UI mantiene anche i nomi originali TMDB come dettaglio di debug quando differiscono dal nome canonico.

## Notifiche ntfy

Le notifiche sono opzionali. Vengono inviate solo quando i provider cambiano rispetto alla cache SQLite già nota; la prima scansione crea la baseline e non notifica.

Per ntfy.sh o un server self-hosted:

```env
NTFY_URL=https://ntfy.example.com
NTFY_TOPIC=streaming-alerts
NTFY_PRIORITY=high
NTFY_TAGS=tv,streaming
```

Se il server richiede autenticazione puoi usare un bearer token:

```env
NTFY_TOKEN=xxx
```

oppure basic auth:

```env
NTFY_USERNAME=utente
NTFY_PASSWORD=password
```

## Note

Per Radarr viene usato `tmdbId` già presente nella movie entity.

Per Sonarr:
- se la serie ha `tmdbId`, usa quello;
- altrimenti prova `tvdbId` tramite endpoint TMDB `/find/{tvdbId}?external_source=tvdb_id`.

## Primo test consigliato

1. Lascia `DRY_RUN=true`.
2. Avvia il container.
3. Controlla i log.
4. Solo dopo metti `DRY_RUN=false`.

## Sviluppo

Il codice applicativo vive nel package `streaming_checker`.

```bash
python -m unittest discover -s tests
```

La CLI resta disponibile con:

```bash
python -m streaming_checker
```

Nel container puoi eseguire una scansione CLI con:

```bash
docker compose run --rm streaming-checker python -m streaming_checker
```
