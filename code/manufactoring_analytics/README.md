# README.md
# Manufacturing Analytics System

A production analytics system built with FastAPI and hexagonal architecture that generates CSV reports from MongoDB manufacturing data.

## Features

- **Automated Analytics Generation**: Scheduled generation of production metrics
- **CSV Export**: All analytics data exported as CSV files for easy analysis
- **RESTful API**: FastAPI-based API with automatic documentation
- **Hexagonal Architecture**: Clean, maintainable code following SOLID principles
- **Async Operations**: High-performance async database operations

## Generated Reports

The system generates the following CSV files:

1. **phase_metrics.csv**: Detailed phase-level production data
2. **machine_metrics.csv**: Machine utilization and efficiency metrics
3. **order_timeline.csv**: Order progress tracking and delays
4. **queue_analysis.csv**: Queue patterns and bottleneck identification
5. **operator_performance.csv**: Individual operator efficiency metrics

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository
2. Create a `.env` file with your configuration
3. Run the system:

```bash
docker-compose up -d
```

4. Access the API at http://localhost:5000
5. View API documentation at http://localhost:5000/docs

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables in `.env`

3. Run the application:
```bash
python main.py
```

## API Endpoints

### Analytics
- `POST /api/v1/analytics/run` - Generate analytics manually
- `GET /api/v1/analytics/status` - Check analytics generation status
- `GET /api/v1/analytics/summary` - Get latest analytics summary

### Export
- `GET /api/v1/export/files` - List available CSV files
- `GET /api/v1/export/download/{filename}` - Download specific file
- `GET /api/v1/export/download-all` - Download all files as ZIP

### System
- `GET /health` - Health check
- `GET /api/v1/config/settings` - View current configuration

## Configuration

Key environment variables:

```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=manufacturing_db
OUTPUT_DIR=./analytics_output
SCHEDULE_INTERVAL_MINUTES=60
```

## Architecture

The system follows hexagonal architecture with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and services
- **Infrastructure Layer**: Database and file system implementations
- **Presentation Layer**: FastAPI routes and API handling

## CSV Output

All analytics are automatically exported to the `analytics_output` directory. Files are updated based on the configured schedule interval.

## MongoDB Schema

The system expects the following collections:
- `NewOrder`: Production orders with phases
- `macchinari`: Machine configurations

See `init-mongo.js` for the complete schema definition.

# deploy.sh
#!/bin/bash

# Simple deployment script for Manufacturing Analytics

set -e

echo "🏭 Manufacturing Analytics Deployment"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
MONGO_URI=mongodb://admin:password123@mongodb:27017/manufacturing_db?authSource=admin
DATABASE_NAME=manufacturing_db
PROCESS_DATABASE_NAME=process_db
OUTPUT_DIR=./analytics_output
SCHEDULE_INTERVAL_MINUTES=60
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=password123
EOF
    echo "✅ .env file created"
fi

# Create output directory
mkdir -p analytics_output

# Build and start services
echo "🔨 Building services..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Analytics API is running"
else
    echo "❌ Analytics API failed to start"
    docker-compose logs analytics_api
    exit 1
fi

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Access points:"
echo "  - API: http://localhost:5000"
echo "  - API Docs: http://localhost:5000/docs"
echo "  - MongoDB: localhost:27017"
echo ""
echo "📁 CSV files will be generated in: ./analytics_output"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Generate analytics: curl -X POST http://localhost:5000/api/v1/analytics/run"

# init-mongo.js
// MongoDB initialization script for manufacturing database

// Switch to the manufacturing database
db = db.getSiblingDB('manufacturing_db');

// Create collections with validation schemas
db.createCollection('NewOrder', {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["orderId", "orderStatus", "quantity"],
         properties: {
            orderId: {
               bsonType: "string",
               description: "must be a string and is required"
            },
            orderStatus: {
               bsonType: "object",
               description: "order status with $numberInt format"
            },
            quantity: {
               bsonType: "object", 
               description: "quantity with $numberInt format"
            },
            codiceArticolo: {
               bsonType: "string",
               description: "article code"
            },
            famigliaDiProdotto: {
               bsonType: "string",
               description: "product family"
            },
            Phases: {
               bsonType: "array",
               description: "array of manufacturing phases"
            }
         }
      }
   }
});

db.createCollection('macchinari', {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["name"],
         properties: {
            name: {
               bsonType: "string",
               description: "machine name is required"
            },
            macchinarioActive: {
               bsonType: "bool",
               description: "whether machine is active"
            },
            queueTargetTime: {
               bsonType: "object",
               description: "queue target time with $numberInt format"
            },
            tablet: {
               bsonType: "array",
               description: "tablet queue array"
            }
         }
      }
   }
});

// Create indexes for better performance
db.NewOrder.createIndex({ "orderId": 1 }, { unique: true });
db.NewOrder.createIndex({ "orderStatus.$numberInt": 1 });
db.NewOrder.createIndex({ "orderInsertDate.$date.$numberLong": 1 });
db.NewOrder.createIndex({ "orderDeadline.$date.$numberLong": 1 });

db.macchinari.createIndex({ "name": 1 }, { unique: true });
db.macchinari.createIndex({ "macchinarioActive": 1 });

// Switch to process database
db = db.getSiblingDB('process_db');

// Create macchinari collection in process_db as well
db.createCollection('macchinari', {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["name"],
         properties: {
            name: {
               bsonType: "string",
               description: "machine name is required"
            },
            macchinarioActive: {
               bsonType: "bool",
               description: "whether machine is active"
            },
            queueTargetTime: {
               bsonType: "object",
               description: "queue target time with $numberInt format"
            },
            tablet: {
               bsonType: "array",
               description: "tablet queue array"
            }
         }
      }
   }
});

// Insert sample data for testing (optional)
print("Manufacturing database initialized successfully!");
print("Collections created: NewOrder, macchinari");
print("Indexes created for optimal query performance");

