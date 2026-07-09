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

## System Architecture
- **Patient Message → Security Check → Cloud Inference (GPT-4o-mini)
- **↓ (if timeout/error)
- **Local Fallback (Ollama)
- **↓
- **JSON Output → Routing Decision