# Lucerna Intent

A companion service for [Lucerna](https://github.com/lydongcanh/lucerna) that classifies user messages into feature intents. 
Designed for compliance-safe analytics: no raw text is stored, only intent labels and metadata.

## Run the app
```bash
# For development
fastapi dev src/service_host/main.py
```

```bash
# For production
fastapi run src/service_host/main.py
```

- Server started at: http://127.0.0.1:8000
- Documentation at: http://127.0.0.1:8000/docs