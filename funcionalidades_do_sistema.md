# 🤖 Modular AI Assistant (LLMinds)
## Ecossistema Multi-Agente Extensível com RAG Local, Sandboxing e Model Context Protocol (MCP)

---

## 🌟 O que é o Modular AI Assistant?

Imagine que, em vez de pagar assinaturas caras de US$ 20 (R$ 118,00) a até US$ 200 (mais de R$ 1.000,00) por mês para ter um chatbot engessado de internet que não conhece seus arquivos locais, não interage com suas pastas e não pode executar ações no seu computador, você pudesse **ter uma equipe inteira de especialistas trabalhando para você, direto da sua máquina, com controle total dos seus dados e sem mensalidades obrigatórias**.

O **Modular AI Assistant** é um ecossistema de agentes inteligentes plug-and-play projetado sob padrões rigorosos de engenharia de software (Clean Architecture, IPC Sandboxing e CI/CD). Ele combina o raciocínio dos maiores modelos de linguagem do mundo (OpenAI, Claude, Google, Meta, Nvidia) com a capacidade de executar ferramentas locais em processos isolados, consultar bases de conhecimento privadas e aprender novas habilidades sem limites.

O projeto foi disponibilizado no GitHub de forma **100% pública, aberta e reproduzível**: qualquer usuário ou desenvolvedor pode clonar o repositório, rodar em seu próprio sistema operacional (Windows, macOS ou Linux) e personalizar o comportamento da IA para qualquer contexto de negócio, estudo ou engenharia.

---

## 🎯 Os 3 Pilares Centrais da Arquitetura

### 1. Uma Equipe de Especialistas Operando em Conjunto (Microsserviços MCP)
Em vez de sobrecarregar um único modelo com todas as responsabilidades, o ecossistema adota uma arquitetura inspirada em microsserviços via **Model Context Protocol (MCP v2.x)**:
* **O Orquestrador Principal (Líder da Equipe):** Ouve a requisição do usuário, analisa as dependências lógicas, planeja o fluxo de execução e decide qual ferramenta acionar no momento exato.
* **O Operador de Arquivos (`filesystem_server.py`):** Confinado em sandbox seguro, é responsável por mapear a árvore do projeto, inspecionar código-fonte e escrever novos arquivos e diretórios de forma atômica.
* **O Pesquisador de Documentos RAG (`rag_server.py`):** Consulta a base vetorial local em busca de fragmentos semânticos de alta relevância com precisão contextual e sem alucinações.
* **O Especialista Matemático (`math_server.py`):** Executa operações e cálculos determinísticos, garantindo precisão matemática absoluta sem confiar na aritmética aproximada de redes neurais.
* **Novos Especialistas Sob Demanda:** Qualquer nova ferramenta conectada passa a integrar o arsenal da equipe automaticamente.

### 2. Extensibilidade Ilimitada: "Ensine" Novas Habilidades à IA
Se o assistente precisar se conectar a serviços externos (como GitHub, Slack, Notion, bancos SQL, planilhas ou redes sociais), o usuário não fica refém de atualizações de empresas terceiras:
* **Criação Própria em Python:** Basta escrever um script simples com o decorator `@mcp.tool()`, definindo os parâmetros esperados e a lógica desejada (conforme documentado em `docs/GUIA_CRIACAO_SKILLS.md`).
* **Instalação Automática:** O utilitário `install_skill.py` permite baixar e plugar ferramentas disponibilizadas pela comunidade global de desenvolvedores MCP diretamente no ecossistema.

### 3. Construção Autônoma de Softwares com Suas Regras e Seu Contexto
O assistente tem autorização controlada para navegar no código do projeto, criar pastas e programar sistemas completos:
* **Injeção de Guias e Padrões:** Coloque manuais de arquitetura (ex: Clean Architecture, Domain-Driven Design, guias de estilo da sua equipe) na pasta de contexto.
* **Geração Fiel ao Contexto:** A IA consulta esses materiais via busca semântica e gera código pronto para produção rigorosamente alinhado aos padrões exigidos pelo usuário.

---

## 💰 Custos e Modelos: Como Funciona na Prática? (Sem Pegadinhas)

Para garantir total transparência e desmistificar os custos de inteligência artificial:

1. **Modelos 100% Gratuitos (Free Tier do OpenRouter):**
   * O sistema já vem pré-configurado com suporte a modelos abertos de altíssimo desempenho cujo consumo é **gratuito** na plataforma (ex: `nvidia/nemotron-3.5-lightning:free`, `google/gemma-4-31b-it:free`).
   * Ideal para estudantes, testes, desenvolvimento contínuo e automações sem custo algum (R$ 0,00/mês).

2. **Modelos Proprietários de Topo (Pay-as-you-go):**
   * Modelos topo de linha do mercado como `openai/gpt-4o` ou `anthropic/claude-opus-5.5` não são gratuitos por parte de seus provedores.
   * No entanto, em vez de exigir assinaturas mensais fixas de US$ 20 a US$ 200 por usuário, o OpenRouter cobra estritamente por fração de token utilizado (centavos de dólar sob demanda).
   * **Resultado:** Você tem a liberdade de alternar instantaneamente entre modelos gratuitos para tarefas rotineiras e modelos pesados para desafios complexos, pagando apenas o que usar.

---

## 💡 Cenários Práticos de Uso no Mundo Real

---

### 💻 Cenário 1: O Desenvolvedor Solo Construindo um Software do Zero
> **Perfil:** Programador que precisa criar um microserviço em FastAPI conectado a banco relacional.
>
> **Como ele personaliza:**
> 1. Salva na pasta `data/raw/` as diretrizes arquiteturais de sua preferência (ex: padrões de repositório, validação com Pydantic e convenções de commit).
> 2. Executa a ingestão para vetorizar o material.
> 3. Solicita no assistente: *"Crie a estrutura completa do módulo de autenticação com `main.py`, `models.py` e `routes.py`, seguindo os padrões documentados no contexto"*.
> 4. **Ação do Sistema:** O agente consulta as diretrizes locais via RAG, cria as pastas intermediárias no disco através do `filesystem_server.py`, gera o código padronizado e entrega o microserviço estruturado e funcional.

---

### ⚖️ Cenário 2: O Consultor Jurídico ou Pesquisador de Editais Complexos
> **Perfil:** Profissional que analisa volumosos editais de licitação, contratos públicos e legislações e não pode submeter documentos confidenciais a provedores em nuvem.
>
> **Como ele personaliza:**
> 1. Deposita dezenas de arquivos PDF de leis e editais na pasta `data/raw/`.
> 2. Dispara o processador vetorial local. Os embeddings são gerados offline no próprio computador via `BAAI/bge-m3` e gravados no Qdrant embarcado.
> 3. Pergunta no chat: *"Qual é a penalidade contratual para atraso de entrega e quais dispositivos legais do edital fundamentam essa sanção?"*
> 4. **Ação do Sistema:** O `rag_server.py` recupera os trechos exatos dos PDFs locais e formula a resposta citando cláusulas e páginas literais, mantendo os documentos sob sigilo absoluto.

---

### 📢 Cenário 3: O Analista de Automação de Marketing e Redes Sociais
> **Perfil:** Profissional que precisa consolidar métricas de campanhas e gerar relatórios executivos sob demanda.
>
> **Como ele personaliza:**
> 1. Escreve uma skill em Python (`metricas_server.py`) que consome dados de uma API externa de redes sociais ou lê uma planilha de relatórios.
> 2. Registra o novo servidor no orquestrador.
> 3. Solicita: *"Analise as métricas de conversão das últimas duas semanas, identifique os pontos de queda e gere um relatório em `analise_desempenho.md` com sugestões táticas"*.
> 4. **Ação do Sistema:** O orquestrador aciona a nova skill, computa os dados e grava o arquivo de análise diretamente no projeto.

---

### 🎓 Cenário 4: O Estudante ou Pesquisador Acadêmico com Orçamento Zero
> **Perfil:** Universitário com hardware modesto (computador sem GPU dedicada) precisando de auxílio em revisões bibliográficas.
>
> **Como ele personaliza:**
> 1. Seleciona na interface gráfica o modelo gratuito `nvidia/nemotron-3.5-lightning:free`.
> 2. Indexa artigos científicos em PDF na base local.
> 3. Usa o sistema para cruzar conclusões entre artigos, validar formulações matemáticas e traduzir termos complexos.
> 4. **Custo:** R$ 0,00 de mensalidade e processamento leve para o computador host.

---

## 🛠️ Guia Operacional: Comandos e Execução de Serviços

O ecossistema é modular, permitindo rodar serviços de forma independente conforme a necessidade:

### 1. Inicialização e Instalação do Ambiente
```bash
# Clone o repositório
git clone https://github.com/INSIRA-AQUI-SEU-USUARIO/modular-ai-assistant.git
cd modular-ai-assistant

# Configuração de variáveis de ambiente
cp .env.example .env
# Abra o .env e adicione sua OPENROUTER_API_KEY (pode ser conta gratuita)

# Instalação determinística de dependências via Poetry
poetry install
```

### 2. Ingestão e Vetorização de Documentos (RAG Local)
Sempre que você adicionar ou atualizar arquivos (`.pdf`, `.txt`, `.md`) na pasta `data/raw/`, execute o pipeline de vetorização para alimentar o banco vetorial local:
```bash
poetry run python src/rag_pipeline/rag_core.py
```
> *Esse comando processa os textos, calcula os embeddings com `BAAI/bge-m3` e grava a coleção vetorial no diretório local `data/vector_db/`.*

### 3. Execução da Interface Gráfica Web (Streamlit)
Para utilizar o assistente visual no navegador, com histórico de conversas, seletor de modelos e monitor de ferramentas em tempo real:
```bash
poetry run streamlit run src/ui/app.py
```

### 4. Execução da Interface de Terminal (CLI)
Para ambientes headless, servidores remotos ou desenvolvedores que preferem operar no console:
```bash
poetry run python src/main.py
```

### 5. Instalação de Novas Skills de Terceiros
Para baixar e acoplar scripts de ferramentas remotas no ecossistema:
```bash
poetry run python scripts/install_skill.py
```

---

## 🛡️ Fundações Técnicas e Diferenciais de Engenharia

* **Isolamento de Processos (IPC Sandboxing):** Cada servidor MCP opera em um processo filho próprio (`stdio`), comunicando-se estritamente via JSON-RPC. Todos os logs operacionais são canalizados para `stderr`, preservando a integridade dos canais de dados.
* **Segurança Anti-Traversal no FileSystem:** O `filesystem_server.py` implementa verificação estrutural via `Path.is_relative_to()`. Qualquer tentativa da IA de ler ou alterar caminhos fora da pasta do projeto é sumariamente abortada com `PermissionError`.
* **Two-Stage RAG Serverless:** Combina indexação vetorial densa com Qdrant embarcado no disco e capacidade de Re-Ranking sem necessidade de infraestrutura pesada em containers Docker.
* **AsyncBridge para Streamlit:** Arquitetura multi-threaded que isola o loop reativo do Streamlit do loop de eventos assíncronos do MCP e do cliente assíncrono da OpenAI, viabilizando streaming fluido de eventos de ferramentas.
* **Adapter Híbrido de Fallback de Tool Calling:** Detecta e converte representações em tags XML emitidas por modelos open-source menores para objetos de chamada compatíveis com o padrão nativo de Function Calling, mantendo a estabilidade operacional do fluxo.

---

## 📌 Considerações Finais e Governança

O **Modular AI Assistant** estabelece um padrão de arquitetura desacoplada, demonstrando como integrar modelos de linguagem de fronteira a ferramentas de execução real de forma segura, portável e sustentável. 

Ao adotar padrões abertos como o **Model Context Protocol (MCP)** e armazenamento vetorial serverless com **Qdrant**, o ecossistema garante que os desenvolvedores mantenham soberania sobre seus dados, seus fluxos de trabalho e suas opções de infraestrutura.

