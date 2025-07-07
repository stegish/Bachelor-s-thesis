# Panoramica del Codice della Piattaforma

Questo repository raccoglie tutti i microservizi e le utilità sviluppati per la tesi di laurea incentrata sul monitoraggio e l'ottimizzazione dei processi produttivi tramite modelli di linguaggio. L'architettura è pensata per essere modulare e facilmente estendibile: ogni servizio è contenuto nella propria directory con Dockerfile e configurazioni dedicate. La comunicazione avviene tramite HTTP e, per le operazioni critiche, attraverso il **Message Context Protocol (MCP)**.

## Architettura Generale

```
[Manufacturing Dashboard]
        │
        ▼
 [LLM Service] ─────► [MCP Server] ───► MongoDB
        ▲                  ▲
        │                  │
 [Analytics API] ─────────┘
```

1. **manufactoring_analytics** – genera report e metriche sui dati di produzione.
2. **llm_service** – elabora i CSV e fornisce analisi e suggerimenti tramite modelli LLM.
3. **mcp_server** – espone gli strumenti MCP per manipolare i dati in modo sicuro.
4. **manufacturing_dashboard** – frontend React che visualizza grafici e proposte di azioni.
5. **merge_code.py** – script di supporto per unire i sorgenti in un unico file.

### Tecnologia Principale
- Python 3.11 + FastAPI per i backend
- MongoDB con driver `motor`
- React 18 e TypeScript per il frontend
- Docker Compose per l'orchestrazione locale
- Modelli Claude di Anthropic attraverso il servizio LLM

## Scelte Architetturali

L'intero progetto segue un paradigma **a microservizi**. Ogni componente
espone API REST e viene containerizzato in modo indipendente tramite
Docker. Ciò permette di aggiornare o scalare singole parti senza
interrompere il resto dell'applicazione. Gli LLM, ad esempio, possono
richiedere più risorse rispetto alla dashboard e vengono quindi
deployati separatamente.

### Pro
- Scalabilità indipendente dei servizi più onerosi (LLM e Analytics).
- Fault isolation: un problema al dashboard non blocca la generazione dei
  report.
- Possibilità di utilizzare stack tecnologici differenti per ciascuna
  esigenza.

### Contro
- Maggior complessità di deploy e monitoraggio rispetto a un approccio
  monolitico.
- Overhead di comunicazione fra servizi (latenza HTTP, serializzazione JSON).
- La risoluzione dei bug richiede tracing distribuito.

## Dettaglio dei Microservizi

### 1. manufactoring_analytics
Directory: `code/manufactoring_analytics`

- **Struttura a strati** (`domain`, `application`, `infrastructure`, `presentation`)
- **Entità principali**: `Order`, `Phase`, `Machine` (in `src/domain/entities`)
- **Value Object**: `OrderStatus`, `PhaseStatus`, `DateRange`
- **Servizi applicativi** (in `application/services`):
  - `OrderAnalyzer`, `MachineAnalyzer`, `PhaseAnalyzer`, `BottleneckDetector`
- **Use Case** (in `application/use_cases`):
  - `GenerateAnalytics`, `GetAnalyticsStatus`, `ExportAnalytics`
- **Repository** (in `infrastructure/persistence/mongodb`):
  - `OrderRepository`, `MachineRepository`, `AnalyticsRepository`
- **API** (cartella `presentation/api`):
  - `main.py` avvia FastAPI, gestisce la dipendenza da MongoDB e schedula l'elaborazione
  - router: `routes/analytics.py`, `routes/csv_export.py`, `routes/export.py`, `routes/config.py`, `routes/health.py`
- Analisi pianificate tramite `scheduler.SchedulerService`
- **Principali endpoint**:
  - `POST /api/v1/analytics/run`
  - `GET /api/v1/analytics/status`
  - `GET /api/v1/analytics/summary`
  - `GET /api/v1/csv/list`
  - `GET /api/v1/csv/download/{nome}`
  - `GET /api/v1/csv/download-all-json`
  - `GET /api/v1/export/files`
  - `GET /api/v1/export/download/{nome}`
  - `GET /api/v1/export/download-all`
  - `GET /api/v1/config/settings`
  - `GET /api/v1/config/capabilities`
  - `GET /health`
  - `GET /ready`
  - `GET /live`


### 2. llm_service
Directory: `code/llm_service`

- **Domini e Use Case** organizzati come sopra: `domain`, `application`, `infrastructure`, `presentation`
- **Entità**: `ManufacturingContext`, `ChatSession`, `ChatMessage`, `AnalysisRequest`, `AnalysisResult`, `LLMRecommendation`, `MCPAction`
- **Value Objects**: `FileData`, `SessionId`, `OrderStatus`, `PromptTemplate`
- **Interfacce** (`domain/interfaces`): definiscono i contratti per `MCPService`, `MCPClient`, `RecommendationRepository`, `ContextRepository`, `ChatRepository`, `FileProcessor`
- **Servizi Applicativi** (`application/services`):
  - `PromptBuilder`, `ContextEnricher`, `PhaseAnalyzer`
- **Use Case** (`application/use_cases`):
  - `ProcessCSV`, `GenerateRecommendation`, `Chat`, `ExecuteMCPAction`, `AnalyzeData`, `GenerateAnalytics`, `GetSuggestions`
- **Infrastructure** (`src/infrastructure`):
  - `anthropic_llm.AnthropicLLM` incapsula le API di Anthropic
  - `mcp_client.MCPClient` invia richieste MCP al server
  - `file_storage.FileStorage` gestisce l'upload temporaneo dei file
  - `mongodb_context.MongoDBContext` fornisce accesso asincrono al DB
- **API** (`presentation/api`): definita in `app.py`, con router per `analysis`, `chat`, `mcp`, `recommendations`, `suggestions`, `config` e `health`
- **CLI** (`presentation/cli`): comandi da terminale per testare il servizio
- **Principali endpoint**:
  - `POST /api/v1/analysis`
  - `POST /api/v1/analysis/csv`
  - `POST /api/v1/analysis/csv/compare`
  - `POST /api/v1/chat`
  - `POST /api/v1/suggestions`
  - `POST /api/v1/recommendations/generate`
  - `GET /api/v1/recommendations/latest`
  - `GET /api/v1/recommendations/history`
  - `GET /api/v1/recommendations/{id}`
  - `POST /api/v1/mcp/execute`
  - `GET /config/settings`
  - `GET /config/capabilities`
  - `GET /health`


### 3. mcp_server
Directory: `code/mcp_server`

- Implementa il **Message Context Protocol** in due varianti:
  - `main.py`: server FastAPI semplice che espone gli endpoint `/tools/*`
  - `mcp_server.py`: server basato su `mcp.server.stdio` con classe `ManufacturingMCPServer`
- **Componenti principali**:
  - `MongoDBRepository` (persistence)
  - `AnalyticsAPIService` (lettura dei CSV dal servizio analytics)
  - Use case: `QueryDatabaseUseCase`, `ReadCSVDataUseCase`, `GetProductionInsightsUseCase`
- **Tools MCP** registrati:
  - `query_database`, `count_documents`, `list_collections`, `get_collection_schema`
  - `list_csv_files`, `read_csv_file`, `get_all_csv_data`, `analyze_csv_file`
  - `get_production_status`
- **Endpoint principali**:
  - `GET /tools`
  - `POST /tools/query_database`
  - `POST /tools/count_documents`
  - `GET /tools/list_collections`
  - `GET /tools/get_collection_schema/{collection}`
  - `POST /tools/update_order`
  - `POST /tools/update_order_priority`
  - `POST /tools/update_machine`
  - `POST /tools/add_order_note`
  - `POST /tools/add_machine_staff`
  - `POST /tools/reschedule_machine_orders`
  - `GET /health`

- Tutte le modifiche a MongoDB passano da questo servizio garantendo validazione e tracciabilità

### 4. manufacturing_dashboard
Directory: `code/manufacturing_dashboard`

Frontend React/TypeScript che utilizza Tailwind CSS e Recharts.
Principali cartelle in `src`:
- `components/` – suddivise in `Dashboard`, `Analytics`, `Anomalies`, `Recommendations`, `common`, `layout`
- `services/` – wrapper Axios per le API backend
- `hooks/` – React hooks personalizzati
- `types/` – definizioni TypeScript
- `utils/` – funzioni di supporto (es. palette colori)

Le variabili `REACT_APP_ANALYTICS_API` e `REACT_APP_LLM_API` configurano gli endpoint. Il dashboard permette di visualizzare i grafici generati dal servizio analytics e di consultare le raccomandazioni prodotte dall'LLM. Prima di eseguire un'azione MCP, l'utente può verificarne i dettagli.

### 5. merge_code.py
Script Python che concatena tutti i sorgenti sotto `code/` in un unico file `merge.txt`. Utile per consultare velocemente l'intero progetto.

## Comunicazione tra i Servizi

Le interazioni avvengono quasi esclusivamente tramite chiamate HTTP REST.
Di seguito una panoramica dei flussi principali:

1. **Dashboard ➜ Analytics API**
   - Richiede lo stato delle analisi e scarica i CSV generati.
2. **Dashboard ➜ LLM Service**
   - Invia i dati raccolti dall'utente (CSV o domande dirette) e riceve
     risposte testuali o strutturate.
3. **LLM Service ➜ MCP Server**
   - Quando il modello suggerisce un'azione (ad esempio, aggiornare la
     priorità di un ordine) il servizio invia una richiesta al MCP
     specificando il *tool* da eseguire.
4. **MCP Server ➜ MongoDB / Analytics API**
   - Il server valida l'azione e interagisce con il database o con
     l'API di analytics per ottenere i dati necessari.

Tutti i servizi espongono endpoint di health check (`/health`) così da
potersi integrare facilmente con Docker Compose o con strumenti di
monitoraggio esterni.

## Message Context Protocol (MCP)

Il MCP definisce una serie di **tool** che possono essere richiamati da agenti LLM per effettuare operazioni sul database o sui file in modo sicuro e controllato. Ogni tool espone uno schema d'ingresso e un output in formato `mcp.types`. Il servizio `llm_service` integra un `MCPClient` che invoca tali tool e restituisce la risposta all'agente LLM. In questo modo si evitano chiamate arbitrarie al database e si mantengono registri dettagliati di ogni modifica.

### Struttura dei messaggi

Una richiesta MCP segue lo schema:

```json
{
  "tool": "update_order_priority",
  "arguments": {
    "order_id": "ORD123",
    "priority": 2
  }
}
```

Il server restituisce un JSON con l'esito dell'operazione, ad esempio:

```json
{
  "success": true,
  "modified_count": 1,
  "order_id": "ORD123",
  "new_priority": 2
}
```

Tutti i tool sono documentati tramite lo schema OpenAPI esposto dal `mcp_server`. Il `llm_service` utilizza queste specifiche per validare i parametri prima dell'invio.

#### Perché usare MCP
- **Sicurezza**: impedisce chiamate dirette al database e valida gli
  argomenti prima dell'esecuzione.
- **Audit**: ogni azione viene loggata e rende tracciabili le modifiche ai dati.
- **Astrazione**: le LLM operano su un insieme di comandi standardizzati
  senza conoscere i dettagli di implementazione.

Esempio di flusso:
1. L'utente richiede un'analisi o un suggerimento tramite la dashboard
2. `llm_service` recupera i dati dal servizio analytics e costruisce il prompt
3. Se nelle risposte sono presenti azioni (es. aggiornare una priorità ordine) queste vengono inviate a `mcp_server`
4. Il server verifica e applica l'azione su MongoDB, restituendo l'esito
5. La dashboard mostra il risultato all'utente

## Avvio dell'ambiente

Ogni servizio dispone di un proprio `docker-compose.yml`, ma è possibile avviare l'intero stack tramite il compose nella cartella del frontend:

```bash
cd code/manufacturing_dashboard
docker-compose up -d
```

Le porte principali sono:
- Analytics API: `5000`
- MCP Server: `5002`
- LLM Service: `5001`
- Frontend: `3000`

Assicurarsi di compilare i file `.env` con `MONGO_URI`, `ANTHROPIC_API_KEY` e gli altri parametri richiesti.

## Struttura del repository

```
code/
├── manufactoring_analytics/   # Microservizio di analisi (FastAPI)
├── llm_service/               # Microservizio LLM e orchestrazione MCP
├── mcp_server/                # Server MCP per operazioni sicure su MongoDB
├── manufacturing_dashboard/   # Frontend React
└── merge_code.py              # Script di utilità
```

Questa panoramica dettagliata illustra come i vari componenti interagiscono fra loro per abilitare l'analisi dei dati e l'esecuzione controllata di azioni proposte dagli LLM attraverso il Message Context Protocol.
