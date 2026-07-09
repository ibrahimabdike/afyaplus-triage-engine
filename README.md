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



Installation
1. Clone the Repository
bash
git clone https://github.com/afyaplus/triage-engine.git
cd triage-engine
2. Install Dependencies
bash
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file in the project root:

bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
4. Verify Local Model
bash
ollama list
# Should show llama3.2:latest
Usage
Quick Start
bash
python app.py
Process a Specific Message
bash
python app.py "I have severe chest pain and difficulty breathing"
Run Benchmark
The benchmark runs automatically after each execution, comparing cloud vs local performance:

bash
python app.py
How It Works
1. Message Processing Pipeline
Input: Patient sends unstructured message

Security Check: Defensive prompt prevents injection attacks

Cloud Inference: GPT-4o-mini processes with 4-second timeout

Fallback: If cloud fails, local Ollama processes (up to 60 seconds)

JSON Extraction: Structured output parsed and validated

Routing Decision: Emergency or routine care routing

2. Prompt Engineering Approach
The system uses an iterative prompt engineering approach:

Version 1 (Basic): Simple role assignment
Version 2 (Structured): Added JSON schema enforcement
Version 3 (Defensive + CoT): Final production version with:

Role-based identity (triage nurse)

Chain-of-Thought reasoning (step-by-step analysis)

Defensive guardrails (no diagnoses, no fluff)

Conservative classification (err on side of emergency)

JSON Output Schema

{
  "is_critical_emergency": boolean,
  "detected_symptoms": ["string", "string"],
  "clinical_reasoning_summary": "string",
  "routing_destination": "Emergency Room | Clinic Appointment | Home Care"
}

Performance Results
Benchmark Summary
Based on 3 test scenarios:

Metric	Cloud (GPT-4o-mini)	Local (Llama 3.2)
Average Response Time	3.08s	46.90s
Success Rate	100%	100%
Speed Comparison	1x	15.2x slower
Key Findings
Cloud is 15.2x faster than local inference

Both models achieve 100% success rate on test cases

Cloud handles timeouts gracefully with automatic local fallback

Local processing is viable for offline/remote scenarios

Test Scenarios
Scenario	Cloud Time	Local Time	Emergency Classified
Mild Headache & Fever	2.75s	45.60s	No
Severe Chest Pain	2.57s	39.21s	Yes
Child with Rash & Fever	3.91s	55.88s	Yes

Business Value
For AfyaPlus Health
Reduced Response Time: Cloud processing delivers results in ~3 seconds

Reliability: Automatic failover ensures 100% uptime

Cost Optimization: Local inference saves API costs when appropriate

Offline Capability: Works in areas with poor network connectivity

Structured Output: Ready for downstream EMR integration