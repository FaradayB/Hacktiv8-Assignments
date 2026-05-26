# Mini Project 5 — IT Helpdesk RAG System

A Retrieval-Augmented Generation (RAG) pipeline for automating IT helpdesk ticket responses using Azure OpenAI and Azure AI Search.

## Overview

This project takes IT helpdesk tickets, classifies them by category using a few-shot LLM classifier, then generates grounded responses using Azure AI Search as the knowledge base. Results are saved as a JSONL file for evaluation.

## Pipeline

```
query → classify_query() → category → response_generate() → save to JSONL
```

1. **classify_query** — Uses few-shot prompting to classify the issue into one of four categories: `Access`, `Network`, `Hardware`, or `Software`
2. **response_generate** — Queries Azure AI Search (filtered by category) and generates a concise, actionable response grounded in the indexed SOP documents
3. **Batch loop** — Iterates over all tickets in the CSV and saves results to `results.jsonl`

## Project Structure

```
mini_project_5/
├── mini_project_5_FaradayBarrFatahillah.ipynb  # Main notebook
├── tickets_IT_helpdesk.csv                      # Input ticket dataset
├── results.jsonl                                # Output (generated after run)
├── .env                                         # Environment variables (not committed)
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>
AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>
AZURE_OPENAI_API_VERSION=<api-version>
AZURE_OPENAI_MODEL=<classifier-model-deployment-name>
AZURE_CHAT_SEARCH=<search-enabled-model-deployment-name>
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_SEARCH_KEY=<your-azure-search-admin-key>
AZURE_SEARCH_INDEX=<your-index-name>
```

### 3. Run the notebook

Open `mini_project_5_FaradayBarrFatahillah.ipynb` and run all cells top to bottom.

## Output Format

Each line in `results.jsonl` follows this schema:

```json
{
    "query": "Cannot connect VPN from home...",
    "response": "For the VPN connection issue...",
    "context": "ticket_id\tsubject\tdescription...",
    "latency": 7.89,
    "response_length": 848
}
```

| Field | Description |
|---|---|
| `query` | Original issue text from the ticket |
| `response` | Generated answer from the model |
| `context` | Raw citations returned by Azure AI Search |
| `latency` | Time taken for the API call in seconds |
| `response_length` | Character length of the response |

## Valid Categories

| Category | Description |
|---|---|
| `Access` | Login issues, MFA, account lockouts, password resets |
| `Network` | VPN, connectivity, network configuration |
| `Hardware` | Physical device issues, peripherals |
| `Software` | Application errors, installations, software configuration |

If a query does not match any category, the system returns: `"I don't have that information."`
