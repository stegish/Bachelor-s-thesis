# Servizio LLM per la Produzione

Il servizio sfrutta i modelli Claude attraverso LangChain per analizzare i file CSV generati dall'analytics e i dati presenti in MongoDB. Fornisce risposte, suggerimenti e raccomandazioni utili a migliorare il processo produttivo.

## Caratteristiche
- Analisi di uno o più file CSV
- Confronto tra CSV di periodi diversi
- Endpoint di chat con gestione della sessione
- Generazione di raccomandazioni e suggerimenti
- Integrazione con il Manufacturing Control Platform (MCP)

## Avvio rapido
1. Crea il file `.env` partendo da `.env.template` e inserisci la chiave `ANTHROPIC_API_KEY`.
2. Avvia il servizio:
   ```bash
docker-compose up -d
   ```
3. Accedi alle API su `http://localhost:5001` e alla documentazione su `/docs`.

## Principali endpoint
| Metodo & Path | Descrizione |
| --- | --- |
| `POST /api/v1/analysis` | Analizza dati JSON con una domanda e opzionale `include_context` |
| `POST /api/v1/analysis/csv` | Carica uno o più CSV e ottieni l'analisi (parametri `question` e `include_context`) |
| `POST /api/v1/analysis/csv/compare` | Confronta almeno due CSV. La domanda è facoltativa |
| `POST /api/v1/chat` | Chat contestuale. Richiede `message` e `session_id` |
| `POST /api/v1/suggestions` | Restituisce suggerimenti partendo da metriche JSON |
| `POST /api/v1/recommendations/generate` | Genera una nuova raccomandazione combinando CSV e contesto MongoDB |
| `GET /api/v1/recommendations/latest` | Ultima raccomandazione salvata |
| `GET /api/v1/recommendations/history?days=7` | Storico delle raccomandazioni negli ultimi giorni |
| `GET /api/v1/recommendations/{id}` | Dettaglio di una raccomandazione |
| `POST /api/v1/mcp/execute` | Esegue un'azione MCP specificata |
| `GET /config/settings` | Configurazione corrente (senza dati sensibili) |
| `GET /config/capabilities` | Funzionalità disponibili |
| `GET /health` | Stato del servizio |

Tutte le risposte sono in JSON. I file CSV inviati vengono caricati temporaneamente nella cartella indicata da `TEMP_UPLOAD_FOLDER` nel `.env`.

## Utilizzo dal frontend
Puoi inviare i CSV prodotti dal servizio di analytics tramite `POST /api/v1/analysis/csv` e visualizzare le risposte testuali o strutturate nel tuo frontend. La chat permette inoltre di mantenere la conversazione collegata a una sessione (`session_id`).
