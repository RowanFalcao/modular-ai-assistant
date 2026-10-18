# 🤖 Modular AI Assistant (LLMinds)

[![CI](https://github.com/RowanFalcao/modular-ai-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/RowanFalcao/modular-ai-assistant/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![Dependency Manager](https://img.shields.io/badge/dependency%20manager-poetry-blueviolet)](https://python-poetry.org/)
[![Architecture](https://img.shields.io/badge/protocol-Model%20Context%20Protocol%20(MCP)-orange)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Ecossistema Multi-Agente Orquestrado com RAG Local, Sandboxing e Model Context Protocol (MCP)**

O **Modular AI Assistant** não é apenas um chatbot, mas um framework de assistência integral operado 100% por arquitetura Plug-and-Play. Projetado sob rigorosos padrões de engenharia de software (Clean Architecture, IPC Sandboxing e CI/CD), ele permite que desenvolvedores e usuários finais construam, adaptem e estendam capacidades de IA sem esbarrar nas limitações de sistemas proprietários engessados.

---

## 🌟 Principais Diferenciais e Capacidades

Diferente de soluções fechadas do mercado, este ecossistema oferece autonomia absoluta através de três pilares:

### 1. Zero Vendor Lock-in e Gestão Inteligente de Custos (OpenRouter)
O motor de raciocínio (Cérebro) está integrado nativamente à API unificada do OpenRouter.
- **Democratização de Hardware (Cloud Compute):** O processamento pesado de inferência ocorre em nuvem. Isso permite que qualquer computador (mesmo notebooks básicos com limitação de VRAM) orquestre modelos gigantescos (como variantes do Nemotron com 70, 120 ou 550 bilhões de parâmetros), eliminando a necessidade de hardwares locais caríssimos.
- **Modelos Gratuitos (Free Tier):** O sistema já vem pré-configurado para consumir modelos abertos de ponta disponibilizados gratuitamente pela plataforma (ex: `nvidia/nemotron-3.5-lightning:free` e `google/gemma-4-31b-it:free`), reduzindo o custo operacional a zero para desenvolvimento e testes.
- **Modelos Topo de Linha sob Demanda (Pay-as-you-go):** Modelos proprietários premium (como GPT-4o ou Claude Opus) operam sem assinaturas fixas de US$ 20 a US$ 200/mês; você paga estritamente pelos centavos de tokens que consumir.
- **Hot-Swapping em Tempo Real:** A interface gráfica permite alternar com apenas um clique entre diferentes famílias de modelos (OpenAI, Anthropic, Google, Meta, Nvidia) instantaneamente durante a conversa.

### 2. Extensibilidade Ilimitada (Model Context Protocol - MCP v2.x)
O sistema não limita o que a sua IA pode fazer. Através do módulo de ação baseado em MCP rodando via `stdio`:
- **Traga suas próprias Skills:** Desenvolvedores podem escrever scripts Python simples com `@mcp.tool()` para ensinar novas habilidades à IA (ex: ler arquivos do computador, buscar na web, conectar-se a APIs externas).
- **Integração com a Comunidade:** Facilidade para acoplar skills criadas pela comunidade global (ex: integração com Notion, GitHub, Google Drive), transformando o assistente em um orquestrador de produtividade sob medida.
- **Instalador Integrado:** O script `scripts/install_skill.py` permite baixar e testar ferramentas remotas com facilidade.

### 3. Portabilidade Extrema e Segurança Nativa (Deploy Anywhere)
O sistema foi arquitetado para reprodutibilidade absoluta, dispensando configurações complexas de infraestrutura (como containers Docker).
- **Rode de um Pen Drive:** Uso estrito de caminhos de diretório relativos e persistência nativa de sessões no disco em formato JSON.
- **Banco Vetorial Serverless:** A engine de RAG (Memória) utiliza Qdrant rodando diretamente no disco local (`data/vector_db`), garantindo que seus documentos e embeddings acompanhem o projeto para qualquer lugar (Windows, macOS ou Linux).
- **FileSystem Sandboxing:** As ferramentas de leitura e escrita operam sob verificação estrutural estrita (`is_relative_to`), impedindo ataques de *Path Traversal* ou modificações fora do workspace permitido.

---

## 🏗️ Arquitetura do Sistema

O ecossistema é estritamente desacoplado, permitindo que qualquer parte seja atualizada sem quebrar o núcleo:

```
                    ┌───────────────────────────────┐
                    │  Interface (Streamlit / CLI)  │
                    └───────────────┬───────────────┘
                                    │ (AsyncBridge / stdio)
                    ┌───────────────▼───────────────┐
                    │    Orquestrador (MCPAgent)    │
                    └───────┬───────────────┬───────┘
                            │               │
            ┌───────────────▼──────┐ ┌──────▼──────────────────────┐
            │  OpenRouter Client   │ │  Servidores MCP (stdio IPC) │
            │ (GPT-4o, Claude, etc)│ ├─────────────────────────────┤
            └──────────────────────┘ │ • filesystem_server.py      │
                                     │ • rag_server.py (Qdrant)    │
                                     │ • math_server.py            │
                                     │ • skill_server.py (custom)  │
                                     └─────────────────────────────┘
```

* **Módulo A (Cérebro / Inferência):** Roteamento via cliente Assíncrono da OpenAI direcionado ao OpenRouter, com fallback resiliente para decodificação de chamadas de ferramentas.
* **Módulo B (Memória / RAG):** Pipeline local de _Two-Stage Retrieval_ com embeddings multilíngues `BGE-M3` via HuggingFace e indexação vetorial estática no Qdrant.
* **Módulo C (Ação / Skills MCP):** Servidores em subprocessos isolados que permitem execução segura de código, cálculos matemáticos e manipulação do FileSystem local comandados pelo LLM.
* **Módulo D (Orquestrador & UX):** Interface nativa em `Streamlit` (com suporte a AsyncBridge multi-threaded) que gerencia o loop multi-agente, retenção de contexto, histórico de conversas em formato JSON e troca de modelos em tempo real.

---

## 🚀 Guia de Instalação e Execução

O gerenciamento de dependências é travado deterministicamente pelo `Poetry`, evitando conflitos de bibliotecas independentemente do sistema operacional.

### 1. Pré-requisitos
* Python 3.11 ou superior
* Poetry instalado (`pip install poetry` ou via instalador oficial)

### 2. Configuração do Projeto
```bash
# Clone o repositório
git clone https://github.com/INSIRA-AQUI-SEU-USUARIO/modular-ai-assistant.git
cd modular-ai-assistant

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env e insira sua OPENROUTER_API_KEY (acesse openrouter.ai e crie uma conta para gerar uma chave gratuita)

# Instale as dependências
poetry install
```

### 3. Comandos de Operação

* **Iniciar a Interface Gráfica Web (Recomendado):**
  ```bash
  poetry run streamlit run src/ui/app.py
  ```

* **Processar Documentos no RAG Local (Opcional):**
  Insira arquivos (`.pdf`, `.txt`, `.md`) em `data/raw/` e execute o indexador:
  ```bash
  poetry run python src/rag_pipeline/rag_core.py
  ```

* **Executar via Linha de Comando (Terminal CLI):**
  ```bash
  poetry run python src/main.py
  ```

* **Instalar uma Nova Skill Remota:**
  ```bash
  poetry run python scripts/install_skill.py
  ```

---

## 📚 Documentação Complementar

Para aprofundar nos detalhes do sistema e nos padrões adotados:
* [Funcionalidades, Cenários e Inovações](file:///c:/Users/User/Desktop/modular-ai-assistant/funcionalidades_do_sistema.md): Guia didático com casos de uso detalhados, proposta de valor e manifesto para a comunidade.
* [Guia de Criação de Skills MCP](file:///c:/Users/User/Desktop/modular-ai-assistant/docs/GUIA_CRIACAO_SKILLS.md): Padrões de Clean Code, tipagem semântica e comunicação IPC para novas ferramentas.

---

## 🛡️ Contribuição e Padrões de Engenharia
Este repositório é orientado a eventos e tarefas de alto nível:
* Toda modificação obedece o **Issue-Driven Development** (rastreabilidade e vinculação em Kanban).
* Histórico mantido através de **Conventional Commits**.
* Validação de integridade via **Continuous Integration (CI / GitHub Actions)**.
* Licença **MIT** para encorajar a colaboração e a evolução aberta do ecossistema.