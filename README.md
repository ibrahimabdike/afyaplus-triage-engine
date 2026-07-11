# AfyaPlus Triage Engine

A production-ready medical triage system that processes unstructured patient messages, classifies urgency, and routes patients appropriately with automatic cloud-to-local failover.

## Overview

AfyaPlus Health is building a prototype medical sorting pipeline that processes incoming patient messages, prioritizes them by urgency, and routes them appropriately. This system supports both cloud-based inference (GPT-4o-mini) and local inference (Ollama with Llama 3.2) with automatic fallback when network connectivity degrades.

**The Problem:** Patients send unstructured, conversational messages. Backend systems need structured, machine-readable inputs. Current AI models suffer from conversational fluff, clinical hallucinations, and crashes during network outages.

**Our Solution:** A production-ready Python inference engine that applies structured prompting, forces JSON output, compares local vs cloud performance, and safely handles network exceptions.

## Features

- Dual Processing Pathways: Cloud (GPT-4o-mini) with automatic local fallback (Ollama)
- Defensive Prompt Engineering: Role-based, Chain-of-Thought reasoning, and guardrails
- Structured JSON Output: Enforced schema for downstream integration
- Resilient Design: 4-second cloud timeout with local failover
- Performance Benchmarking: Built-in comparison of cloud vs local latency
- Security-First: Guardrails against prompt injection and hallucination

## System Architecture

```
Patient Message
       ↓
Security Check
       ↓
Cloud Inference (GPT-4o-mini)
       ↓ (if timeout/error)
Local Fallback (Ollama)
       ↓
JSON Output
       ↓
Routing Decision
```

## Prerequisites

- Python 3.8+
- Ollama (for local inference)
- OpenAI API key (via OpenRouter)

## Installation

```bash
git clone https://github.com/ibrahimabdike/afyaplus-triage-engine.git
cd afyaplus-triage-engine
pip install openai python-dotenv httpx requests
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3.2
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

## Usage

```bash
python app.py
python app.py "I have severe chest pain and difficulty breathing"
```

## Example Output

```
AFYAPLUS TRIAGE ENGINE
======================================================================
PATIENT: I'm 7 months pregnant with severe headache and swollen feet
======================================================================
Cloud... OK (3.09s)

RESULTS:
--------------------------------------------------
EMERGENCY: YES
SYMPTOMS: severe headache, swollen feet
REASONING: Severe headache and swollen feet in a pregnant patient may indicate potential complications that require immediate evaluation.
ROUTE: Emergency Room
SOURCE: CLOUD
TIME: 3.09s

ACTION: IMMEDIATE EMERGENCY ROUTING
======================================================================
```

## Performance Results

| Metric | Cloud (GPT-4o-mini) | Local (Llama 3.2) |
|--------|-------------------|-------------------|
| Average Response Time | 3.08s | 46.90s |
| Success Rate | 100% | 100% |
| Speed Comparison | 1x | 15.2x slower |

| Scenario | Cloud Time | Local Time | Emergency Classified |
|----------|-----------|------------|---------------------|
| Mild Headache & Fever | 2.75s | 45.60s | No |
| Severe Chest Pain | 2.57s | 39.21s | Yes |
| Child with Rash & Fever | 3.91s | 55.88s | Yes |

- Key Findings: Cloud is 15.2x faster than local inference.
- Both models achieve 100% success rate.
- Cloud handles timeouts gracefully with automatic local fallback.
- Local processing is viable for offline/remote scenarios.

## Business Value

- Reduced Response Time: Cloud processing delivers results in ~3 seconds
- Reliability: Automatic failover ensures 100% uptime
- Cost Optimization: Local inference saves API costs when appropriate
- Offline Capability: Works in areas with poor network connectivity
- Structured Output: Ready for downstream EMR integration

## Troubleshooting

```bash
ps aux | grep ollama  # Check if running
ollama serve          # Restart service
ollama list           # Check available models
ollama pull llama3.2  # Pull model if missing
```

## File Structure

```
triage-engine/
├── app.py
├── requirements.txt
├── .env
└── README.md
```

requirements.txt:
```
openai>=1.0.0
python-dotenv>=1.0.0
httpx>=0.25.0
requests>=2.31.0
```