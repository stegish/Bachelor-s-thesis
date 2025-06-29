# Manufacturing LLM Service

This microservice provides AI-powered analytics for manufacturing data using Claude API through LangChain, with special support for CSV file analysis.

## Features

- **CSV File Analysis**: Upload and analyze single or multiple CSV files
- **CSV Comparison**: Compare multiple CSV files to identify trends and differences
- **Question & Answer**: Send questions with manufacturing data and receive AI-powered insights
- **Context-Aware Analysis**: Automatically retrieves relevant context from MongoDB
- **Batch Processing**: Analyze multiple questions in a single request
- **Interactive Chat**: Maintain conversation context for follow-up questions
- **Improvement Suggestions**: Get actionable recommendations based on metrics
- **MongoDB Integration**: Seamlessly connects to existing manufacturing database

## Prerequisites

- Docker and Docker Compose
- Anthropic API Key (Claude)
- Running MongoDB instance (can use the one from analytics service)

## Setup

1. **Create `.env` file** with your configuration:
```bash
cp .env.template .env
# Edit .env and add your ANTHROPIC_API_KEY
```

2. **Connect to existing network** (if using with analytics service):
```bash
# The docker-compose.yml is configured to use the existing manufacturing network
```

3. **Start the service**:
```bash
docker-compose up -d
```

## API Endpoints

### Health Check
```bash
GET http://localhost:5001/health
```

### CSV File Analysis
```bash
POST http://localhost:5001/analyze/csv
Content-Type: multipart/form-data

Files: (multiple CSV files)
question: "Analyze these manufacturing metrics and identify bottlenecks"
include_context: true (optional, default: true)
```

Example with curl:
```bash
curl -X POST http://localhost:5001/analyze/csv \
  -F "files=@machine_metrics.csv" \
  -F "files=@order_timeline.csv" \
  -F "question=What are the main production issues?"
```

### Compare CSV Files
```bash
POST http://localhost:5001/analyze/csv/compare
Content-Type: multipart/form-data

Files: (2 or more CSV files)
question: (optional, auto-generated if not provided)
```

Example:
```bash
curl -X POST http://localhost:5001/analyze/csv/compare \
  -F "files=@january_data.csv" \
  -F "files=@february_data.csv" \
  -F "files=@march_data.csv" \
  -F "question=Compare monthly performance trends"
```

### CSV Summary
```bash
POST http://localhost:5001/analyze/csv/summary
Content-Type: multipart/form-data

file: (single CSV file)
```

Example:
```bash
curl -X POST http://localhost:5001/analyze/csv/summary \
  -F "file=@phase_metrics.csv"
```

### Standard Analysis (JSON data)
```bash
POST http://localhost:5001/analyze
Content-Type: application/json

{
  "question": "What are the main bottlenecks in our production?",
  "data": {
    "machine_metrics": [...],
    "order_timeline": [...]
  },
  "include_context": true
}
```

### Interactive Chat
```bash
POST http://localhost:5001/chat
Content-Type: application/json

{
  "message": "Tell me more about the Taglio machine performance",
  "session_id": "user123"
}
```

### Get Suggestions
```bash
POST http://localhost:5001/suggestions
Content-Type: application/json

{
  "metrics": {
    "avg_machine_utilization": -433.67,
    "on_time_delivery_rate": 15.38,
    "bottleneck_machines": ["Taglio"]
  }
}
```

## CSV Analysis Examples

### 1. Analyze Production CSV Files
```python
import requests

# Analyze multiple related CSV files
files = [
    ('files', ('machine_metrics.csv', open('machine_metrics.csv', 'rb'), 'text/csv')),
    ('files', ('queue_analysis.csv', open('queue_analysis.csv', 'rb'), 'text/csv')),
    ('files', ('operator_performance.csv', open('operator_performance.csv', 'rb'), 'text/csv'))
]

data = {
    'question': 'Identify correlations between machine performance, queue delays, and operator efficiency'
}

response = requests.post('http://localhost:5001/analyze/csv', files=files, data=data)
print(response.json()['answer'])
```

### 2. Compare Monthly Reports
```python
# Compare CSV files across different time periods
files = [
    ('files', ('january.csv', open('january.csv', 'rb'), 'text/csv')),
    ('files', ('february.csv', open('february.csv', 'rb'), 'text/csv')),
    ('files', ('march.csv', open('march.csv', 'rb'), 'text/csv'))
]

response = requests.post('http://localhost:5001/analyze/csv/compare', files=files)
print(response.json()['answer'])
```

### 3. Integration with Analytics Service
```python
# Download CSV from analytics service and analyze
analytics_csv = requests.get('http://localhost:5000/analytics/download/machine_metrics.csv')

files = [('files', ('machine_metrics.csv', analytics_csv.content, 'text/csv'))]
data = {'question': 'Which machines need immediate maintenance?'}

response = requests.post('http://localhost:5001/analyze/csv', files=files, data=data)
print(response.json()['answer'])
```

## CSV File Requirements

- **File Format**: Standard CSV with headers
- **Encoding**: UTF-8, Latin-1, ISO-8859-1, or CP1252
- **Size Limit**: 50MB per file
- **Multiple Files**: Can upload multiple CSV files for comparative analysis

## Integration with Analytics Service

This service is designed to work alongside the manufacturing analytics service:

1. **Shared MongoDB**: Uses the same MongoDB instance
2. **Network Integration**: Connects to the same Docker network
3. **CSV Flow**: Can directly analyze CSV outputs from analytics service

### Workflow Example:

```bash
# 1. Generate analytics CSVs
curl -X POST http://localhost:5000/analytics/run

# 2. List available CSV files
curl http://localhost:5000/analytics/files

# 3. Download and analyze specific CSV
curl http://localhost:5000/analytics/download/machine_metrics.csv -o machine_metrics.csv
curl -X POST http://localhost:5001/analyze/csv \
  -F "files=@machine_metrics.csv" \
  -F "question=What maintenance is needed?"
```

## Configuration Options

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Claude API key (required)
- `MODEL_NAME`: Claude model to use (default: claude-3-sonnet-20240229)
- `MAX_TOKENS`: Maximum response tokens (default: 4096)
- `TEMPERATURE`: Response creativity (0-1, default: 0.7)
- `MONGO_URI`: MongoDB connection string
- `DATABASE_NAME`: MongoDB database name

### Available Models

- `claude-3-opus-20240229`: Most capable, best for complex analysis
- `claude-3-sonnet-20240229`: Balanced performance (default)
- `claude-3-haiku-20240307`: Fastest, good for simple queries

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_key_here
export MONGO_URI=mongodb://localhost:27017/

# Run the service
python llm_service.py
```

### Adding Custom CSV Analysis

Extend the `ManufacturingLLMService` class:

```python
def analyze_custom_metrics(self, csv_data: pd.DataFrame) -> Dict[str, Any]:
    """Add custom CSV analysis logic"""
    # Custom processing here
    return analysis_results
```

## Performance Considerations

### For Large CSV Files

1. The service automatically limits DataFrame display to 100 rows for LLM context
2. For very large files, consider:
   - Splitting into smaller chunks
   - Pre-aggregating data
   - Asking specific, focused questions

### Optimization Tips

- Use specific questions to focus the analysis
- Upload only relevant columns if possible
- Consider pre-processing very large datasets

## Monitoring

- Check logs: `docker logs manufacturing_llm`
- Health endpoint: `http://localhost:5001/health`
- Monitor file uploads in `/tmp/llm_uploads`

## Security Considerations

1. **API Key**: Store securely, never commit to version control
2. **File Upload**: Only CSV files are allowed, max 50MB
3. **Network**: Service runs on internal Docker network
4. **User**: Runs as non-root user in container
5. **Data**: Be mindful of sensitive manufacturing data in CSV files

## Troubleshooting

### CSV Upload Issues
- Check file encoding (UTF-8 preferred)
- Verify CSV has headers
- Ensure file size < 50MB
- Check for special characters in headers

### Service won't start
- Check API key is set correctly
- Verify MongoDB is accessible
- Check logs: `docker logs manufacturing_llm`

### Slow responses
- Large CSV files take longer to process
- Consider using claude-3-haiku model for faster responses
- Reduce number of rows in CSV if possible

### Memory issues
- For very large CSV files, consider splitting them
- Monitor Docker container memory usage
- Increase container memory limits if needed