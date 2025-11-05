# BYO Agentic Framework

> **Work in Progress** - This repository is actively evolving with new patterns and examples.

A collection of notebooks demonstrating **how to build AI agents** using **Llama Stack** with different frameworks: pure Llama Stack Responses API, LangChain, and CrewAI.

This project explores three approaches to building AI agents with tool calling and RAG (Retrieval-Augmented Generation) capabilities, all leveraging **MCP (Model Context Protocol)** for tool integration.

**What you'll learn:**
- Build agents using Llama Stack's native Responses API (no framework dependencies)
- Integrate LangChain 1.0 agents with MCP tools
- Create multi-agent RAG systems with CrewAI
- Deploy containerized MCP servers on OpenShift

To get started, jump to [installation](#install). 

## Table of contents

- [Architecture](#architecture-diagrams)
- [Requirements](#requirements)
- [Installation](#install)
- [Notebooks Overview](#notebooks-overview)

## Architecture diagrams

```
┌─────────────────────────────────────────────┐
│         Agentic Notebooks                   │
│  (3 approaches: Primitives, LangChain,      │
│   CrewAI)                                   │
└────────┬────────────────────────────────────┘
         │
         │ API Calls
         ▼
┌─────────────────┐   ┌──────────────────────┐
│  Llama Stack    │   │  MCP Tools           │
│  - vLLM Engine  │◄──┤  - Weather Service   │
│  - Vector Store │   │  - Kubernetes API    │
│  - Responses API│   │  - Yahoo Finance     │
└─────────────────┘   └──────────────────────┘
```

**Key Components:**
- **Llama Stack**: Inference engine with OpenAI-compatible API
- **MCP Servers**: Containerized tool servers (Weather, K8s, Finance)
- **Vector Stores**: Document storage and retrieval for RAG
- **Frameworks**: Optional layers (LangChain, CrewAI) for orchestration

### References

- [Llama Stack Documentation](https://llamastack.github.io/)
- [Model Context Protocol (MCP) Specification](https://modelcontextprotocol.io/)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp)
- [CrewAI Documentation](https://docs.crewai.com/)