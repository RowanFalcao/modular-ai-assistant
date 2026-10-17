# 🤖 Modular AI Assistant (LLMinds)

> **Ecossistema Multi-Agente Orquestrado com RAG Local e Model Context Protocol (MCP)**

O **Modular AI Assistant** não é apenas um chatbot, mas um framework de assistência integral operado 100% por arquitetura Plug-and-Play. Projetado sob rigorosos padrões de engenharia de software (Clean Code, IPC Sandboxing e CI/CD), ele permite que desenvolvedores e usuários finais construam, adaptem e estendam capacidades de IA sem esbarrar nas limitações de sistemas proprietários engessados.

## 🌟 Principais Diferenciais e Capacidades (Versão 1.0)

Diferente de soluções fechadas do mercado, este ecossistema oferece autonomia absoluta através de três pilares:

### 1. Zero Vendor Lock-in, Democratização de Hardware e Economia (OpenRouter)
O motor de raciocínio (Cérebro) está integrado nativamente à API do OpenRouter. 
- **Democratização de Hardware (Cloud Compute):** O processamento pesado de inferência ocorre em nuvem. Isso permite que qualquer computador (mesmo notebooks básicos com limitação de VRAM) orquestre modelos gigantescos (como variantes do Nemotron com centenas de bilhões de parâmetros), eliminando a necessidade de hardwares locais caríssimos.
- **Acesso a Modelos Gratuitos (Free Tier):** O sistema já vem pré-configurado para consumir modelos abertos de ponta disponibilizados gratuitamente pela plataforma, reduzindo o custo operacional a zero para desenvolvimento e testes.
- **Hot-Swapping e Eficiência:** A interface gráfica permite alternar com apenas um clique entre a família OpenAI (GPT-4o), Anthropic (Claude), Google (Gemma) e Meta (Llama). Sem assinaturas fixas caras, você paga (se decidir usar modelos premium) apenas pelo que consumir.

### 2. Extensibilidade Ilimitada (Model Context Protocol)
O sistema não limita o que a sua IA pode fazer. Através do módulo de ação baseado em MCP (v2.x) rodando via `stdio`:
- **Traga suas próprias Skills:** Desenvolvedores podem escrever scripts Python simples para ensinar novas habilidades à IA (ex: ler arquivos do computador, buscar na web, conectar-se a APIs externas).
- **Integração com a Comunidade:** Facilidade para acoplar skills criadas pela comunidade global (ex: integração com Notion, GitHub, Google Drive), transformando o assistente em um orquestrador de produtividade sob medida.

### 3. Portabilidade Extrema (Deploy Anywhere)
O sistema foi arquitetado para reprodutibilidade absoluta, dispensando configurações complexas de infraestrutura (como Docker).
- **Rode de um Pen Drive:** Uso estrito de caminhos de diretório relativos e persistência nativa de sessões no disco.
- **Banco Vetorial Serverless:** A engine de RAG (Memória) utiliza Qdrant rodando diretamente no disco local (`data/vector_db`), garantindo que seus documentos e embeddings acompanhem o projeto para qualquer lugar (Windows, macOS ou Linux).

---

## 🏗️ Arquitetura do Sistema

O ecossistema é estritamente desacoplado, permitindo que qualquer parte seja atualizada sem quebrar o núcleo:

*   **Módulo A (Cérebro / Inferência):** Roteamento via cliente Assíncrono da OpenAI direcionado ao OpenRouter. *(Nota técnica: A orquestração autônoma de ferramentas e blindagem de sintaxe JSON encontra-se otimizada e homologada prioritariamente para modelos da família OpenAI nesta versão 1.0).*
*   **Módulo B (Memória / RAG):** Pipeline local de _Two-Stage Retrieval_ com modelos de embedding `BGE-M3` via HuggingFace e indexação vetorial estática.
*   **Módulo C (Ação / Skills MCP):** Servidores em processos isolados que permitem execução segura de código, cálculos matemáticos e manipulação do FileSystem local, comandados pelo LLM.
*   **Módulo D (Orquestrador & UX):** Interface nativa em `Streamlit` (com suporte a AsyncBridge) que gerencia o loop multi-agente, retenção de contexto, histórico de conversas em formato JSON e troca de modelos em tempo real.

---

## 🚀 Guia de Instalação Rápida

O gerenciamento de dependências é travado deterministicamente pelo `Poetry`, evitando conflitos de bibliotecas independentemente do sistema operacional.

**1. Crie sua conta e gere sua API Key:**
* Acesse [OpenRouter.ai](https://openrouter.ai/) e crie uma conta gratuita.
* Vá em "Keys" e gere uma nova chave de API.

**2. Clone o repositório:**
```bash
git clone https://github.com/SEU-USUARIO/modular-ai-assistant.git
cd modular-ai-assistant
```

**3. Configure suas credenciais:**
Copie o template de ambiente e insira sua chave do OpenRouter que você acabou de gerar:
```bash
cp .env.example .env
```

**4. Instale o ecossistema:**
```bash
poetry install
```

**5. Inicialize a Interface do Assistente:**
```bash
poetry run python src/ui/app.py
```

## 🛡️ Contribuição e Padrões de Engenharia
Este repositório é orientado a eventos e tarefas de alto nível:
* Toda modificação obedece o **Issue-Driven Development** (rastreabilidade e vinculação em Kanban).
* Histórico mantido através de **Conventional Commits**.
* Validação de integridade via **Continuous Integration (CI / GitHub Actions)**.