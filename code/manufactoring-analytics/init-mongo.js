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

// Insert sample data for testing (optional)
print("Manufacturing database initialized successfully!");
print("Collections created: NewOrder, macchinari");
print("Indexes created for optimal query performance");