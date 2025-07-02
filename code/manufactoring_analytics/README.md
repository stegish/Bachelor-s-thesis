# Servizio Manufacturing Analytics

Questo microservizio analizza i dati di produzione memorizzati su MongoDB e genera automaticamente file CSV con le principali metriche di produzione. Le API, basate su FastAPI, permettono di avviare l'elaborazione e scaricare i report in modo semplice.

## Caratteristiche
- Generazione programmata o manuale delle analisi
- Esportazione dei risultati in CSV o ZIP
- Architettura esagonale con componenti asincroni
- Documentazione automatica disponibile su `/docs`

## Avvio rapido
1. Configura il file `.env` partendo da `.env.template`.
2. Avvia il servizio con Docker Compose:
   ```bash
docker-compose up -d
   ```
3. L'API sarà disponibile su `http://localhost:5000`.

## Principali endpoint
| Metodo & Path | Descrizione |
| --- | --- |
| `POST /api/v1/analytics/run` | Avvia la generazione dei CSV (`force=true` per rigenerarli) |
| `GET /api/v1/analytics/status` | Restituisce lo stato dell'ultima elaborazione |
| `GET /api/v1/analytics/summary` | Riepilogo dell'ultimo set di metriche |
| `GET /api/v1/csv/list` | Elenco dei file CSV prodotti |
| `GET /api/v1/csv/download/{nome}` | Scarica un singolo CSV |
| `GET /api/v1/csv/download-all-json` | Tutti i CSV convertiti in JSON |
| `GET /api/v1/export/files` | Elenco completo dei file nella cartella di output |
| `GET /api/v1/export/download/{nome}` | Scarica qualsiasi file di output |
| `GET /api/v1/export/download-all` | Comprime e scarica tutti i file |
| `GET /api/v1/config/settings` | Impostazioni correnti del servizio |
| `GET /api/v1/config/capabilities` | Funzionalità supportate |
| `GET /health` | Verifica lo stato del servizio |
| `GET /ready` & `GET /live` | Endpoint per orchestratori |

Tutti gli endpoint restituiscono JSON; quelli di download inviano file. I CSV vengono salvati di default nella cartella `analytics_output`, configurabile nel file `.env`.

## Utilizzo dal frontend
Dopo aver generato i report (`POST /api/v1/analytics/run`), puoi elencare i file disponibili e scaricarli per mostrarli sul frontend. Per esempio, una richiesta `GET /api/v1/csv/download-all-json` restituisce tutti i dati già in formato JSON pronto da consumare.
