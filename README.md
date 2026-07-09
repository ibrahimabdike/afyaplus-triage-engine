# AfyaPlus Triage Engine

A production-ready medical triage system that processes unstructured patient messages, classifies urgency, and routes patients appropriately with automatic cloud-to-local failover.

## Overview

AfyaPlus Health is building a prototype medical sorting pipeline that processes incoming patient messages, prioritizes them by urgency, and routes them appropriately. This system supports both cloud-based inference (GPT-4o-mini) and local inference (Ollama with Llama 3.2) with automatic fallback when network connectivity degrades.

## Features

- **Dual Processing Pathways**: Cloud (GPT-4o-mini) with automatic local fallback (Ollama)
- **Defensive Prompt Engineering**: Role-based, Chain-of-Thought reasoning, and guardrails
- **Structured JSON Output**: Enforced schema for downstream integration
- **Resilient Design**: 4-second cloud timeout with local failover
- **Performance Benchmarking**: Built-in comparison of cloud vs local latency
- **Security-First**: Guardrails against prompt injection and hallucination

## Detailed Process Flow

**1. Patient Message**
- Patient sends unstructured natural language message
- Example: "I have severe chest pain and difficulty breathing"

**2. Security Check**
- Validates input against prompt injection attacks
- Sanitizes message content
- Blocks malicious attempts

**3. Cloud Inference (Primary Path)**
- GPT-4o-mini processes message
- 4-second timeout limit
- Returns structured JSON output

**4. Local Fallback (Backup Path)**
- Triggers automatically if cloud times out or fails
- Ollama with Llama 3.2 processes locally
- 60-second timeout for model inference

**5. JSON Output**
- Structured, validated output
- Contains emergency flag, symptoms, reasoning, routing

**6. Routing Decision**
- Routes to Emergency Room if critical
- Routes to Clinic Appointment for routine cases
- Routes to Home Care for minor issues

## Prerequisites

### Required Software
- Python 3.8+
- Ollama (for local inference)
- OpenAI API key (via OpenRouter)

### Python Dependencies
```bash
pip install openai python-dotenv httpx requests

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull the model
ollama pull llama3.2

# Verify installation
ollama run llama3.2 "Hello"

```

