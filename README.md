# Lucerna Intent

[![Build Status](https://github.com/lydongcanh/lucerna-intent/actions/workflows/ci.yml/badge.svg)](https://github.com/lydongcanh/lucerna-intent/actions/workflows/ci.yml)

A companion service for [Lucerna](https://github.com/lydongcanh/lucerna) that classifies user messages into feature intents. 
Designed for compliance-safe analytics, no raw text is stored, only intent labels and metadata.

## Supported intents
| Intent Name         | Description                                              | Example Output                         |
| ------------------- | -------------------------------------------------------- | -------------------------------------- |
| `category`          | The general type of product or concept being asked about | `"virtual data room"`                  |
| `feature_focus`     | The specific feature or aspect the user is focusing on   | `"access control"`                     |
| `purpose`           | The reason or goal behind the user’s question            | `"for due diligence"`                  |
| `tone`              | The sentiment or tone (optional)                         | `"curious"`                            |
| `decision_context`  | The broader context of decision-making                   | `"selecting a vendor for M&A project"` |
| `entity_primary`    | The main product or subject                              | `"CompanyA"`                           |
| `action_intent`     | What the user wants to do                                | `"compare"` or `"learn differences"`   |

## Run the app
```bash
# For development
PYTHONPATH=src fastapi dev src/service_host/main.py
```

```bash
# For production
PYTHONPATH=src fastapi run src/service_host/main.py
```

- Server started at: http://127.0.0.1:8000
- Documentation at: http://127.0.0.1:8000/docs