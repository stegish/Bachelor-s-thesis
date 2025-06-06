## Manufacturing Analytics Microservice

This service analyzes production data stored in MongoDB and exports a set of
CSV reports used by Grafana dashboards. The microservice expects an external
MongoDB instance and reads the connection string from the `MONGO_URI`
environment variable.

### Required environment variables

```
MONGO_URI=<your-mongodb-uri>
DATABASE_NAME=manufacturing_db
PROCESS_DATABASE_NAME=process_db
SCHEDULE_INTERVAL_MINUTES=60
FLASK_ENV=production

# Credentials for optional local services
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=manufacturing_secure_2024
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=grafana_admin_2024
```

`PROCESS_DATABASE_NAME` should reference the database that stores the
`macchinari` collection. By default it uses the same name as `DATABASE_NAME`.

Update `MONGO_URI` to point to your MongoDB server before starting the service.
