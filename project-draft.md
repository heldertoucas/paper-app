# Paperclip Project Draft

Consolidated brainstorming and product requirements for the Paperclip capture system.

---

## Document Index

1. [PRD1: Desktop Application](#prd1-desktop-application)
2. [PRD2: Web/PWA Application](#prd2-webpwa-application)
3. [PRD3: Technical Specifications](#prd3-technical-specifications)
4. [Tutorial: Web App User Guide](#tutorial-web-app-user-guide)

---

# PRD1: Desktop Application

## Product Requirement Document (PRD) · Versão Expandida

## Project Paperclip: Ultra-lightweight Desktop Scratchpad

---

## 1. Vision & Purpose

### 1.1. Contexto Académico e Profissional

O Project Paperclip nasce da necessidade de alinhar a recolha quotidiana de informação com os princípios fundamentais da literacia digital e da cidadania crítica. A tecnologia deve funcionar estritamente como um meio invisível de capacitação e nunca como um fim em si mesma. Num ecossistema assente em curadoria de conhecimento, a retenção de ideias e o registo de dados não podem ser travados por burocracias de interface ou por processos de formatação complexos.

### 1.2. Objetivos Estratégicos

O utilitário foi concebido especificamente para um ecossistema de gestão de conhecimento pessoal (PKM) assente em repositórios locais e operado por interfaces de linha de comando (CLI), como o cliente Claude Code. O Paperclip resolve o dilema da fricção de captura através da separação total de responsabilidades:

* **O Frontend (Paperclip):** Atua como um terminal de captura puro, minimalista e instantâneo, otimizado para o fluxo de consciência do utilizador.
* **O Middleware (PocketBase):** Funciona como um colchão de amortecimento assíncrono na nuvem, isolando o repositório principal e eliminando a necessidade de gerir desfasamentos no histórico do Git (*non-fast-forward*) ou resolver conflitos de branches entre múltiplas máquinas físicas (PC Windows e Mac).
* **O Backend (Agente de IA):** Absorve os ficheiros em bruto injetados na pasta `00-inbox/`, assumindo a responsabilidade exclusiva de categorizar, aplicar taxonomia, criar ligações bidirecionais e validar o frontmatter através do fluxo de automatização matinal (`ai-start`).

---

## 2. System Architecture & Ecosystem Topology

### 2.1. Fluxo de Dados e Topologia de Redes

A arquitetura do sistema adota uma postura híbrida (*Local-First com Persistência Cloud Assíncrona*). O sistema garante que nenhuma nota é perdida por falhas na ligação à internet ou por latências na resposta de servidores remotos.

```
+────────────────────────────────────────────────────────┐
│             Desktop Paperclip App (Python)              │
+───────────────────────────┬────────────────────────────┘
                            │ (Escrita Síncrona < 5ms)
                            ▼
               +──────────────────────────┐
               │ Local Cache (SQLite3)    │
               +────────────┬─────────────┘
                            │ (Operação Assíncrona via Worker Thread)
                            ▼
+────────────────────────────────────────────────────────┐
│             PocketBase Cloud (Fly.io / Zeabur)         │
+───────────────────────────┬────────────────────────────┘
                            │ (Disparado via CLI: 'ai-start')
                            ▼
               +──────────────────────────┐
               │ Script: pull_pocketbase  │
               +────────────┬─────────────┘
                            │ (Geração de Ficheiros Físicos .md)
                            ▼
+────────────────────────────────────────────────────────┐
│            obsidian-ht/00-inbox/                       │
+────────────────────────────────────────────────────────┘

```

### 2.2. Robustez e Tratamento de Exceções Criptográficas

* **Isolamento do Repositório Git:** A aplicação local e os clientes móveis nunca comunicam com a API do GitHub. O repositório central `obsidian-ht` permanece fechado e imune a commits automáticos fragmentados.
* **Mecânica de Concorrência:** O PocketBase gera identificadores de registo únicos (IDs baseados em strings aleatórias de alta entropia), o que impede a sobreposição de notas criadas no mesmo segundo a partir de dispositivos distintos.
* **Segurança de Trânsito e Repouso:** Os dados que viajam do Paperclip para o PocketBase são empacotados com cifragem simétrica AES-GCM. Mesmo em caso de quebra de segurança na infraestrutura da cloud, as notas candidas permanecem ilegíveis para terceiros.

---

## 3. Functional Specifications & Feature Requirements

### 3.1. Keyboard-First Interface & Window Lifecycle

* **Atalho de Invocação Global:** A aplicação mantém-se oculta na barra de tarefas (system tray), consumindo recursos mínimos. É ativada globalmente através das combinações de teclas `Ctrl + Shift + Space` (Windows) ou `Cmd + Shift + Space` (macOS).
* **Foco e Captura de Cursor:** Ao abrir, a janela ignora animações de renderização do sistema operativo, força o posicionamento em primeiro plano (Always on Top) e foca o cursor no campo de texto imediatamente.
* **Ciclo de Vida de Janela:**
  * `Esc`: Miniminiza e oculta a aplicação instantaneamente para a barra de tarefas. O texto inserido permanece retido no buffer local como rascunho temporário, permitindo retomar a nota mais tarde se a janela for reaberta.
  * `Ctrl + Esc` / `Cmd + Esc`: Limpa o buffer por completo e oculta a janela.
  * `Ctrl + Enter` / `Cmd + Enter`: Tranca o texto, inicia o processo de gravação e esconde a interface em menos de 50 milissegundos.

### 3.2. Contextual Tab Architecture & Dynamic Routing

A zona superior da interface possui um alinhamento horizontal de separadores estruturados em conformidade com as áreas de manutenção contínua e projetos core do utilizador.

```
┌───────────────────────────────────────────────────────────────────────────┐
│ [1] Inbox    [2] Família    [3] Passaporte    [4] Futuro    [5] Freelance │
└───────────────────────────────────────────────────────────────────────────┘

```

* **Atalhos Rápidos de Seleção:** A navegação faz-se através de clique ou pelos comandos `Cmd + [1-5]` / `Ctrl + [1-5]`.
* **Roteamento Dinâmico de Metadados:** Cada separador injeta um rótulo estrito no payload de envio que será interpretado pelo script de extração local para preenchimento automático do domínio no YAML:
  1. `Inbox` -> mapeia para o domínio `system`. Destinado a triagem geral e notas de sistema técnico.
  2. `Família` -> mapeia para o domínio `pessoal`. Destinado ao núcleo familiar e responsabilidades privadas.
  3. `Passaporte` -> mapeia para o domínio `cmlisboa`. Destinado a notas do programa de inclusão e literacia digital (PASS).
  4. `Futuro Digital` -> mapeia para o domínio `cmlisboa`. Destinado a dados do programa de capacitação (FUTURO).
  5. `Freelance` -> mapeia para o domínio `freelance`. Destinado a consultoria autónoma externa.

### 3.3. Arquitetura Local-First e Sincronização Concorrente

* **A Base de Dados Local (SQLite3):** A aplicação grava as notas localmente num ficheiro SQLite3 em disco de forma síncrona. Esta operação é executada localmente para garantir que o utilizador nunca fica dependente de latências de rede para ver a janela fechar.
* **O Worker de Sincronização:** Uma thread paralela e não obstrutiva acorda a cada 60 segundos ou imediatamente após um comando bem-sucedido de fecho de nota. Esta rotina verifica a presença de internet através de um pedido ping ultra-leve para a API do PocketBase.
* **Estratégia de Envio:** Se detetar rede, as notas guardadas na SQLite local são enviadas sequencialmente via HTTP `POST` num formato JSON cifrado. O servidor do PocketBase responde com `HTTP 201 Created`. Após validação da resposta, o worker local elimina de forma segura os registos correspondentes da SQLite local para manter o disco limpo.

### 3.4. Local Clipboard Integration

* **Inspeção Passiva de Entrada:** Ao abrir a janela, a aplicação lê o formato dos dados presentes na área de transferência do sistema operativo.
* **Atalho de Anexação Direta:** Caso seja detetado um link web (iniciado por `http` ou `https`) ou um bloco de texto contínuo, a barra de estado inferior ativa um elemento gráfico com o rótulo `[Tab] Colar Link`.
* **Comportamento da Tecla Tab:** Ao premir `Tab`, a aplicação insere o link formatado em notação Markdown no fim da última linha de texto do utilizador, libertando-o da necessidade de fazer `Ctrl + V` manualmente e gerir espaços.

### 3.5. Pipeline de Transcrição de Áudio (Whisper + VAD)

* **Ativação Toggle por Atalho:** O comando de gravação de voz é acionado ao premir `Ctrl + R` ou `Cmd + R`. O utilizador não precisa de manter as teclas premidas durante o discurso.
* **Mutações Visuais de Estado:** O editor de texto altera a folha de estilo da interface: as bordas ganham uma moldura pulsante em ciano e o fundo do campo de entrada passa para um carmesim escuro profundo (`#2a1414`).
* **Deteção de Atividade de Voz (VAD Local):** A aplicação integra a biblioteca leve `webrtcvad`. Se o sistema detetar uma ausência de fala contínua superior a 2.5 segundos, o Paperclip assume que a nota foi concluída. A gravação é encerrada de forma automática, emitindo um sinal sonoro discreto de sistema.
* **Processamento Assíncrono via API:** O ficheiro de áudio temporário é comprimido em formato `.wav` mono a 16kHz e despachado de imediato via pedido HTTP multipart para a API da Groq (executando o modelo Whisper-Large-v3). A resposta com o texto transcrito em Português de Portugal substitui o estado visual de gravação e injeta o bloco de texto formatado na posição atual do cursor do utilizador.

---

## 4. Visual & Interface Design Guidelines

A interface do Paperclip é orientada pela ausência de ruído visual. O design deve ser completamente plano, sem gradientes ou decorações tridimensionais, integrando-se nativamente em ambientes de trabalho de estética minimalista e focados em produtividade por teclado.

### 4.1. Arquitetura de Janela e Comportamento Geométrico

* **Frameless & Borderless:** A aplicação utiliza uma janela sem moldura nativa do sistema operativo (`Qt.FramelessWindowHint`). O recorte dos cantos arredondados com um raio de 12px é processado via máscara gráfica (`QRegion`), evitando artefactos de renderização nos cantos do ecrã.
* **Dimensões Fixas:** A janela possui uma dimensão estática de 580px de largura por 400px de altura, posicionada por predefinição no centro do monitor ativo onde o cursor do rato se encontra no momento da invocação.

### 4.2. Especificações de Estilo e Folha de Estilo Completa (PySide6 QSS)

Abaixo encontra-se a folha de estilo formal que rege todos os elementos gráficos da aplicação, aplicando as variáveis de cor e tipografia em total conformidade com a paleta escura do ecossistema:

```css
/* Definição do Contentor Principal */
QWidget#MainWindow {
    background-color: #101010;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
}

/* Barra Superior de Separadores (Tab Bar) */
QTabBar {
    background-color: #121212;
    border-bottom: 1px solid #2a2a2a;
    qproperty-drawBase: 0;
}

QTabBar::tab {
    background: transparent;
    color: #707070;
    font-family: 'SF Pro Display', -apple-system, sans-serif;
    font-size: 12px;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}

QTabBar::tab:hover {
    color: #b0b0b0;
    background-color: #1a1a1a;
}

QTabBar::tab:selected {
    color: #22d3ee;
    background-color: #161616;
    border-left: 1px solid #2a2a2a;
    border-right: 1px solid #2a2a2a;
    border-top: 1px solid #2a2a2a;
    font-weight: 500;
}

/* Campo de Entrada de Texto (Editor) */
QTextEdit#Editor {
    background-color: #161616;
    border: none;
    color: #e0e0e0;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 14px;
    line-height: 160%;
    padding: 24px;
}

/* Estados Dinâmicos de Gravação de Áudio (Injetados via Código) */
QTextEdit#Editor[recording="true"] {
    background-color: #2a1414;
    border: 1px solid #ef4444;
}

/* Barra de Estado Inferior (Footer) */
QStatusBar {
    background-color: #101010;
    border-top: 1px solid #2a2a2a;
    color: #606060;
    font-family: 'SF Pro Display', sans-serif;
    font-size: 11px;
}

/* Indicadores de Atalho no Rodapé */
QLabel#HotkeyIndicator {
    color: #a0a0a0;
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: monospace;
}

```

---

## 5. System Integration & Second Brain Alignment

### 5.1. Segurança, Cifragem Simétrica e Autenticação Cloud

A proteção da privacidade dos dados efémeros que transitam fora da rede local é um requisito crítico de arquitetura. O sistema implementa um fluxo de segurança em três camadas:

1. **Autenticação por Token Estático:** A instância do PocketBase na cloud (Fly.io/Zeabur) rejeita qualquer pedido HTTP que não inclua um cabeçalho `Authorization: Bearer <JWT_SECRET>`. As regras de coleção da base de dados (`API Rules`) são definidas como `@request.headers.auth = "true"` tanto para operações de escrita como de eliminação.
2. **Cifragem AES-GCM Local:** O Paperclip não envia o texto plano da nota. Antes da transmissão, o payload é cifrado em memória através de uma biblioteca Python nativa (`cryptography.hazmat`) recorrendo ao algoritmo **AES-256-GCM**. A chave de cifragem simétrica é guardada exclusivamente de forma local no Mac e no Windows, configurada nas variáveis de ambiente das respetivas máquinas.
3. **Payload Ofuscado:** O PocketBase armazena apenas um bloco hexadecimal contendo o vetor de inicialização (IV), a tag de autenticação e o texto cifrado. Qualquer interceção ou fuga de dados no servidor remoto preserva a confidencialidade absoluta das notas.

### 5.2. Pipeline do Script de Ingestão Local (`pull_pocketbase.py`)

O script que efetua a ponte entre a nuvem e o repositório físico local é desenhado para ser atómico e idempotente. Este script é invocado na inicialização da CLI através do comando de entrada do utilizador.

```python
import os
import re
import sys
import json
import requests
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Diretórios e Variáveis de Ambiente Estritas
INBOX_DIR = os.path.expanduser("~/path/to/obsidian-ht/00-inbox/")
SECRET_KEY = os.environ.get("MONOLITH_CRYPTO_KEY")
PB_ENDPOINT = "https://api.monolith-pb.internal/api/collections/notas_inbox/records"
PB_TOKEN = os.environ.get("MONOLITH_PB_TOKEN")

def sanitize_filename(text):
    """Garante a conformidade rigorosa com a Regra 5 de nomenclatura do manual"""
    text = text.lower()
    text = re.sub(r'[áàãâä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[íìîï]', 'i', text)
    text = re.sub(r'[óòõôö]', 'o', text)
    text = re.sub(r'[úùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9_\- ]', '', text)
    text = text.replace(' ', '-')
    return text[:40].strip('-')

def to_sentence_case(text):
    """Formata o título estritamente em Sentence case conforme as regras do utilizador"""
    text = text.strip().capitalize()
    return text

def process_inbox():
    headers = {"Authorization": f"Bearer {PB_TOKEN}"}
    try:
        response = requests.get(PB_ENDPOINT, headers=headers, timeout=10)
        if response.status_code != 200:
            sys.exit(1)
            
        records = response.json().get("items", [])
        if not records:
            return

        aesgcm = AESGCM(bytes.fromhex(SECRET_KEY))

        for record in records:
            # Desempacotamento do payload criptográfico
            iv = bytes.fromhex(record["iv"])
            ciphertext = bytes.fromhex(record["encrypted_data"])
            aba_dominio = record["contexto_aba"]
            
            # Decifragem em memória
            decrypted_text = aesgcm.decrypt(iv, ciphertext, None).decode('utf-8')
            
            # Extração da primeira linha para o título da nota
            lines = [l for l in decrypted_text.split('\n') if l.strip()]
            raw_title = lines[0] if lines else "Nota sem titulo"
            clean_title = to_sentence_case(raw_title)
            
            # Construção do nome do ficheiro (Regra 5)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            safe_title_slug = sanitize_filename(raw_title)
            filename = f"web-{aba_dominio}-{safe_title_slug}-{timestamp}.md"
            
            # Montagem estruturada do Bloco YAML Frontmatter
            yaml_block = (
                "---\n"
                f'title: "{clean_title}"\n'
                "type: source\n"
                f"domain: {aba_dominio}\n"
                "status: draft\n"
                f"created: {datetime.today().strftime('%Y-%m-%d')}\n"
                "---\n\n"
            )
            
            # Escrita física e atómica no disco local
            target_path = os.path.join(INBOX_DIR, filename)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(yaml_block + decrypted_text)
                
            # Limpeza imediata do registo na cloud (Garante idempotência)
            requests.delete(f"{PB_ENDPOINT}/{record['id']}", headers=headers, timeout=5)

    except Exception as e:
        sys.stderr.write(f"Erro no pipeline de ingestão: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    process_inbox()

```

---

## 6. Non-Functional Requirements & Performance Targets

### 6.1. Métricas de Desempenho e Alocação de Recursos

* **Memory Footprint Permanente:** O processo em segundo plano, gerido via PySide6 e alojado na barra de tarefas do sistema operativo, não pode exceder o teto máximo de **40 MB de memória RAM consumida** quando em estado de repouso (*idle*).
* **Eficiência de CPU:** A execução de ciclos de CPU deve ler rigorosamente **0.0%** de forma contínua enquanto a aplicação estiver oculta, não interferindo com tarefas pesadas de compilação ou execução de agentes no terminal.
* **Perceção de Latência Humana:** O tempo decorrido entre a pressão do atalho global de invocação e a renderização completa da janela com foco total do cursor deve ser inferior a **50 milissegundos**. A escrita síncrona na base de dados SQLite3 local após o fecho da nota deve ser executada em menos de **5 milissegundos**.

### 6.2. Robustez de Rede e Estratégia de Tolerância a Falhas

A aplicação adota um modelo de tolerância a falhas assente no princípio da autonomia local:

* **Persistência Local-First Resiliente:** Em cenários de quebra total de rede ou indisponibilidade temporária da infraestrutura Cloud (Fly.io/Zeabur), a aplicação principal não emite janelas de erro pop-up nem bloqueia a introdução de dados. As notas são acumuladas sem limite na base de dados SQLite3 local.
* **Estratégia de Retry com Backoff:** O *worker thread* de sincronização utiliza um algoritmo de reativação exponencial. Se um envio falhar por erro de rede, o sistema aguarda 30 segundos para a tentativa seguinte, duplicando o intervalo sequencialmente até um teto máximo de 15 minutos entre tentativas, poupando a bateria do hardware móvel e ciclos desnecessários de CPU no desktop.

---

# PRD2: Web/PWA Application

## Product Requirement Document (PRD)

## Project Paperclip Web: Cloud-Based Mobile & Browser Capture Endpoint

---

## 1. Vision & Purpose

### 1.1. Contexto de Mobilidade e Acessibilidade Universal

O Project Paperclip Web expande a capacidade de captura do ecossistema do Second Brain (`obsidian-ht`) para cenários onde a aplicação nativa de ambiente de trabalho não está disponível. Ele visa dotar o telemóvel Android e navegadores secundários de um ponto de entrada rápido, esteticamente idêntico e funcionalmente agnóstico ao dispositivo.

Seguindo os princípios de autonomia e espírito crítico no uso da tecnologia, esta aplicação web recusa converter-se num editor complexo ou num gestor de ficheiros em nuvem. A sua existência serve uma única métrica: **reduzir o tempo entre a conceção de um pensamento cândido e a sua persistência segura na base de dados temporária**.

### 1.2. Objetivos Estratégicos

* **Unificação de Código:** Fornecer uma interface universal baseada em tecnologias web padrão que se adapta instantaneamente ao ecrã de um telemóvel Android ou a uma aba de navegador desktop (Mac/Windows).
* **Compatibilidade Progressive Web App (PWA):** Permitir a instalação no Android com um clique, transformando a aba do browser numa aplicação com ícone no ecrã principal, sem as molduras e barras de navegação do Chrome.
* **Isolamento de Concorrência:** Encaminhar as notas diretamente para o PocketBase Cloud via APIs cifradas, garantindo que a captura em mobilidade não interfere com o repositório Git local e previne conflitos de sincronização.

---

## 2. System Architecture & Ecosystem Topology

A versão web opera na nuvem através da infraestrutura da Vercel para o fornecimento do Frontend e execução de funções Serverless intermédias, comunicando diretamente com o motor PocketBase.

```
+────────────────────────────────────────────────────────┐
│   Telemóvel Android (PWA) / Aba Browser Desktop        │
+───────────────────────────┬────────────────────────────┘
                            │ (Captura de Texto / Gravação de Áudio Nativa)
                            ▼
+────────────────────────────────────────────────────────┐
│   Vercel Edge Network (Next.js / HTML5 App)            │
+───────────────────────────┬────────────────────────────┘
                            │ (Processamento de Áudio via Serverless Route)
                            ├─► [ Groq API / Whisper Cloud ]
                            │ (Envio do JSON Cifrado via HTTPS)
                            ▼
+────────────────────────────────────────────────────────┐
│   PocketBase Cloud (Fly.io / Zeabur)                   │
+────────────────────────────────────────────────────────┘

```

### 2.1. Mitigação de Limitações Serverless

Para contornar o limite de tempo de execução (*timeout* de 10 a 15 segundos) do plano gratuito da Vercel Hobby, a gravação de áudio é otimizada na origem:

* O browser faz a compressão imediata do áudio em blocos leves antes do envio.
* A rota Serverless limita-se a fazer o reencaminhamento direto por *stream* para a API da Groq, garantindo tempos de resposta globais inferiores a 2 segundos para notas de voz curtas.

---

## 3. Functional Specifications & Feature Requirements

### 3.1. Interface Web Progressiva (PWA) e Responsividade

* **Design Altamente Responsivo:** O layout adapta-se de forma fluida entre o formato fixo de desktop (580px centralizado) e a totalidade do ecrã vertical de um dispositivo Android.
* **Manifest & Service Workers:** A aplicação inclui um ficheiro `manifest.json` e configurações de Service Worker. Quando acedida pelo Google Chrome no Android, exibe o botão "Adicionar ao ecrã principal". Uma vez instalada, abre em modo `standalone` (sem barra de URL, ocultando os controlos do browser).
* **Retenção de Estado Local:** Se o utilizador fechar a aba acidentalmente a meio de uma nota, o texto é preservado no `localStorage` do browser e restaurado automaticamente na abertura seguinte.

### 3.2. Menu Superior de Abas e Atalhos Touch/Teclado

A barra de navegação superior mimetiza com precisão a estrutura de domínios do ecossistema:

1. `Inbox` (domínio `system`)
2. `Família` (domínio `pessoal`)
3. `Passaporte` (domínio `cmlisboa`)
4. `Futuro Digital` (domínio `cmlisboa`)
5. `Freelance` (domínio `freelance`)

* **Comportamento Touch:** No Android, a alternância faz-se por toque direto nos botões em formato de pílulas horizontais com scroll lateral deslizante caso o ecrã seja estreito.
* **Comportamento Desktop:** Mantém o suporte aos atalhos de teclado `Cmd + [1-5]` ou `Ctrl + [1-5]`.

### 3.3. Integração com Clipboard do Android/Browser

* **Botão de Colagem Rápida:** Devido às restrições de segurança de leitura automática de clipboard nos browsers, a interface disponibiliza um botão visual discreto chamado "Anexar Link" se detetar que a API do clipboard tem dados válidos disponíveis após autorização expressa do utilizador.

### 3.4. Captura de Voz Nativa (Web Audio API + Whisper Cloud)

* **Interface de Gravação Nativa:** O utilizador inicia e termina a gravação através de um toque simples (mecanismo *Toggle*) num botão flutuante de microfone ou pelo atalho `Ctrl + R` no PC.
* **Processamento de Áudio:** Utiliza a API `MediaRecorder` do browser para capturar áudio do microfone do telemóvel, codificando-o nativamente em formato `audio/webm` ou `audio/ogg` para reduzir o consumo de dados móveis.
* **Deteção de Silêncio no Browser:** A aplicação web monitoriza os decibéis do microfone através de um nó de análise de áudio (`AnalyserNode`). Se o utilizador parar de falar por mais de 3 segundos, a aplicação encerra a gravação de forma automática e inicia o envio para transcrição.

---

## 4. Visual & Interface Design Guidelines

O visual respeita o minimalismo estrito e a paleta escura monocrática exigida pelo utilizador.

### 4.1. Código Completo de Estilo e Layout (HTML + CSS Incorporado)

Este código representa a especificação visual e estrutural exata da aplicação web, pronta a ser implementada na Vercel:

```html
<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Paperclip Web</title>
    <style>
        :root {
            --bg-main: #101010;
            --bg-editor: #161616;
            --text-primary: #e0e0e0;
            --text-secondary: #606060;
            --accent-cyan: #22d3ee;
            --accent-red: #ef4444;
            --border-color: #2a2a2a;
            --font-mono: 'SF Mono', 'Fira Code', 'Consolas', monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 16px;
        }

        /* Contentor Adaptável (Desktop vs Mobile) */
        .web-scratchpad {
            width: 100%;
            max-width: 580px;
            height: 400px;
            background-color: var(--bg-main);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
        }

        @media (max-width: 600px) {
            body { padding: 0; }
            .web-scratchpad {
                height: 100vh;
                border-radius: 0;
                border: none;
            }
        }

        /* Barra de Separadores Horizontal */
        .tab-bar {
            display: flex;
            background-color: #121212;
            border-bottom: 1px solid var(--border-color);
            overflow-x: auto;
            white-space: nowrap;
            scrollbar-width: none; /* Esconde scroll no Firefox */
        }
        .tab-bar::-webkit-scrollbar { display: none; } /* Esconde scroll no Chrome */

        .tab {
            background: transparent;
            border: none;
            color: #707070;
            padding: 12px 18px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .tab:hover { color: #b0b0b0; }

        .tab.active {
            color: var(--accent-cyan);
            background-color: var(--bg-editor);
            border-bottom: 2px solid var(--accent-cyan);
            font-weight: 500;
        }

        /* Área de Texto */
        .editor-container {
            flex-grow: 1;
            position: relative;
            background-color: var(--bg-editor);
        }

        textarea {
            width: 100%;
            height: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-primary);
            font-family: var(--font-mono);
            font-size: 15px;
            line-height: 1.6;
            padding: 20px;
            resize: none;
        }

        /* Estado de Gravação Ativa */
        .web-scratchpad.recording .editor-container {
            background-color: #2a1414;
            border: 1px solid var(--accent-red);
        }

        /* Rodapé de Estado */
        .footer {
            height: 44px;
            padding: 0 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-color);
            font-size: 12px;
            color: var(--text-secondary);
            background-color: var(--bg-main);
        }

        .btn-action {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 12px;
        }
        .btn-action:hover { color: var(--text-primary); }
    </style>
</head>
<body>

    <div class="web-scratchpad" id="scratchpad">
        <div class="tab-bar">
            <button class="tab active">Inbox</button>
            <button class="tab">Família</button>
            <button class="tab">Passaporte</button>
            <button class="tab">Futuro Digital</button>
            <button class="tab">Freelance</button>
        </div>
        <div class="editor-container">
            <textarea placeholder="Escreva ou grave uma nota cândida..."></textarea>
        </div>
        <div class="footer">
            <button class="btn-action" id="btn-paste">[Tab] Anexar Link</button>
            <span id="status-text">Ligado à Cloud</span>
        </div>
    </div>

</body>
</html>

```

---

## 5. System Integration & Second Brain Alignment

### 5.1. Protocolo de Segurança Web e Envio Cifrado

A fim de manter a conformidade com as exigências de privacidade, a aplicação web replica a lógica de criptografia usada na versão desktop:

1. **Cifragem via Web Crypto API:** O browser do telemóvel ou PC utiliza a API nativa do navegador (`crypto.subtle`) para cifrar o texto escrito com o algoritmo **AES-GCM de 256 bits** antes de qualquer transmissão.
2. **Distribuição da Chave:** A chave secreta simétrica é inserida pelo utilizador uma única vez nas configurações da aplicação web e armazenada de forma segura no `localStorage` privado do seu navegador. A chave nunca é transmitida para os servidores da Vercel ou do PocketBase.
3. **Persistência Limpa:** O PocketBase recebe apenas o metadado da aba em texto limpo (para permitir a triagem pelo script Python local) e o corpo da nota completamente ofuscado em formato binário/hexadecimal.

### 5.2. Integração com o Script de Ingestão Matinal

As notas enviadas pela versão web entram na mesma tabela `notas_inbox` do PocketBase Cloud. O script local `pull_pocketbase.py` (detalhado no PRD da app desktop) descarrega estes registos indiscriminadamente, decifra-os com a chave local idêntica e coloca-os em formato `.md` na pasta `00-inbox/` local. O processo web torna-se, assim, inteiramente invisível para o repositório Git principal.

---

## 6. Non-Functional Requirements & Performance Targets

### 6.1. Otimização de Recursos e Carregamento na Vercel

* **Zero Overhead de Servidor:** O frontend da aplicação é composto por ficheiros estáticos gerados no deploy. O consumo de CPU nos servidores da Vercel limita-se aos milissegundos necessários para reencaminhar o ficheiro de áudio para a API do Whisper.
* **Lightweight Bundle:** O tamanho total dos ficheiros enviados para o browser do telemóvel não ultrapassa os **150 KB** (incluindo o script de criptografia e estilos), garantindo um carregamento instantâneo mesmo sob redes móveis 3G ou 4G instáveis.
* **Performance de Resposta:** O atraso visual entre o toque no botão de guardar e o fecho ou limpeza da interface não excede os **100 milissegundos**.

### 6.2. Modelo de Resiliência Offline para Mobilidade

Como as redes móveis são propensas a quebras de sinal, o Paperclip Web implementa uma política estrita de persistência local temporária:

* **Fila de Espera no IndexedDB:** Se um pedido de envio para o PocketBase falhar por falta de rede (`Network Error`), a nota cifrada é guardada automaticamente no **IndexedDB** do browser do telemóvel.
* **Sincronização Silenciosa em Background:** Um mecanismo de sincronização monitoriza o evento `online` do navegador. Assim que a rede for restabelecida, a aplicação esvazia a fila do IndexedDB, enviando as notas acumuladas de forma silenciosa para o PocketBase, sem que o utilizador tenha de reintroduzir os dados ou manter a aplicação aberta em primeiro plano.

---

# PRD3: Technical Specifications

## Architecture Options and Technical Decisions

Criar uma ferramenta de captura rápida com atrito quase nulo é a única forma de garantir a sua sustentabilidade a longo prazo. Para alcançar um consumo de recursos mínimo e evitar o peso de estruturas tradicionais, a arquitetura deve ser focada em eventos nativos do sistema operativo.

### Abordagens para a aplicação

Para que o utilitário corra em segundo plano sem impactar o desempenho, existem duas abordagens estruturais recomendadas.

#### Opções de desenvolvimento

**Hammerspoon (se utilizar macOS):** Esta é uma das opções mais eficientes para automação leve. Funciona através de scripts em Lua que comunicam diretamente com as APIs do sistema operativo. O consumo de memória é insignificante e a ferramenta possui capacidades nativas para monitorizar a aplicação em primeiro plano, ler o clipboard e criar pequenas zonas de receção de ficheiros. Para ambientes Windows, o AutoHotkey oferece uma flexibilidade semelhante na gestão de janelas e automação de texto.

**Tauri:** Caso pretenda uma interface visual mais estruturada e independente do sistema operativo, esta tecnologia utiliza Rust no núcleo e delega a interface para o motor web nativo do sistema. O resultado são aplicações que iniciam instantaneamente, ocupam poucos megabytes em disco e apresentam um consumo de memória RAM muito reduzido, frequentemente abaixo dos 30 MB.

### Estratégias para reduzir a fricção

A simplicidade de utilização depende da capacidade da aplicação em antecipar as intenções do utilizador e automatizar a recolha de dados de contexto.

**Invocação instantânea e fecho automático:** A aplicação deve surgir através de um atalho global do teclado, posicionando o cursor imediatamente no campo de texto. Assim que perde o foco ou o utilizador prime a tecla de escape, a janela deve ocultar-se instantaneamente, assegurando o arquivo automático do conteúdo.

**Captura inteligente do clipboard:** No momento em que a aplicação é invocada, o sistema pode verificar se o conteúdo do clipboard mudou nos últimos segundos. Se detetar um URL ou um bloco de texto recente, pode sugerir a sua anexação imediata com um único clique ou comando numérico.

**Zonas de largada dinâmicas:** O comportamento de arrastar e largar deve ser intercetado para extrair apenas os metadados necessários. Quando um ficheiro é largado na interface, a aplicação deve registar o caminho absoluto do ficheiro no disco ou o URL de origem se o elemento vier de um navegador de internet, evitando o processamento pesado do ficheiro em si.

**Deteção proativa do ecossistema:** Através de escutas ativas de eventos do sistema, o utilitário consegue identificar qual a aplicação que estava ativa imediatamente antes da sua invocação. Isto permite categorizar de forma automática se a nota provém de um cliente de correio eletrónico, de um editor de código ou de uma página web específica, preenchendo as etiquetas de contexto sem intervenção manual.

### Funcionalidades de captura estruturada

A separação clara entre o utilitário de captura e o motor de processamento garante a leveza da aplicação. Para que o Obsidian e os agentes de IA trabalhem com dados estruturados, o utilitário deve focar-se na padronização imediata da recolha.

**Escrita atómica em Markdown:** Cada interação deve gerar um ficheiro individual na pasta de entrada do Obsidian, utilizando a data e hora como nome do ficheiro. Ficheiros pequenos e isolados facilitam a indexação e a leitura por parte de agentes como o Claude Code.

**Injeção automatizada de metadados em YAML:** O utilitário deve escrever um bloco de metadados padronizado no início de cada nota. Este bloco deve registar a aplicação de origem, o título da janela ativa, o URL ou o caminho absoluto do ficheiro e a data exata. Os agentes de IA utilizam os metadados para classificar e interligar a informação posteriormente.

**Deduplicação no clipboard:** Caso o utilizador capture o mesmo conteúdo repetidamente, a aplicação deve atualizar os metadados do ficheiro existente ou anexar a nova observação no mesmo documento, reduzindo o ruído na base de dados.

**Criação de referências por caminhos absolutos:** Ao arrastar um ficheiro para o utilitário, a aplicação regista apenas o caminho local absoluto no formato de ligação do Obsidian. Este método permite que o Claude Code aceda ao ficheiro original diretamente no disco quando for necessário.

### Captura contextual por aplicação

O utilitário deve comportar-se de forma diferente com base na janela que se encontra em primeiro plano no momento da ativação.

**Terminal Warp:** Ao registar uma nota com o terminal ativo, o utilitário lê o título da janela (que expõe a diretoria atual ou o repositório Git) para injetar essas etiquetas no ficheiro Markdown. Esta ação permite associar notas de desenvolvimento diretamente ao projeto em execução.

**Figma e navegadores (SharePoint, Google Drive, Forms, Power Automate):** A aplicação obtém o URL ativo através das APIs de acessibilidade do sistema operativo. Ao arrastar um elemento do Figma ou uma folha de cálculo do SharePoint, o utilitário converte o endereço numa ligação direta no formato do Obsidian, poupando passos de cópia manual.

**Teams e Outlook:** A monitorização do título da janela extrai o assunto do correio eletrónico ou o nome do canal de conversação, preenchendo automaticamente o campo de contexto na nota atómica.

### Especificações técnicas do utilitário de captura

#### Arquitetura e desempenho
- Desenvolvimento multiplataforma com base na tecnologia Tauri (Rust) ou através de scripts nativos por sistema operativo (Hammerspoon e AutoHotkey).
- Consumo reduzido de memória RAM (alvo inferior a 30 MB) com execução contínua em segundo plano.
- Escrita direta no sistema de ficheiros local na pasta do Obsidian, dispensando a necessidade de bases de dados intermédias.

#### Mecanismos de captura e redução de fricção
- Invocação imediata por atalho de teclado global com foco automático no campo de introdução de texto.
- Ocultação automática da interface após a confirmação da nota ou sempre que a janela perde o foco do utilizador.
- Avaliação do histórico recente da área de transferência para sugestão de anotação inteligente de texto ou links.
- Zona de receção por arrastamento que converte ficheiros e elementos em caminhos absolutos ou em endereços de internet.

#### Integrações de contexto e ecossistema
- Extração automática do título da janela ativa e do nome do processo que se encontra em primeiro plano.
- Identificação de projetos e repositórios de desenvolvimento a partir do título do terminal Warp.
- Recolha de endereços web através de APIs de acessibilidade no Figma e navegadores (SharePoint, Google Drive, Forms, Power Automate).
- Mapeamento de assuntos de mensagens e nomes de canais de conversação no Outlook e Microsoft Teams.

#### Compatibilidade com o segundo cérebro
- Geração de notas atómicas em formato Markdown, criando um ficheiro independente por cada captura realizada.
- Atribuição de nomes de ficheiros com base na marca temporal da interação (registo de data e hora).
- Injeção automatizada de metadados estruturados em blocos YAML para posterior consumo por agentes de inteligência artificial (como o Claude Code).
- Processo automático de deduplicação para evitar a criação de ruído em registos idênticos e consecutivos.

### Decisão estratégica sobre stack tecnológico

**Requisitos:**
- A app deve ser levíssima
- Deve ser capaz de capturar informação do sistema
- Deve ser escrita de modo a funcionar em Windows e Mac
- A App vai ser desenvolvida com assistência da IA, por isso o stack deve usar linguagens e plataformas nas quais as IAs têm sucesso e bons resultados

#### Python com PySide6 ou Flet

Esta opção prioriza a facilidade de desenvolvimento assistido por inteligência artificial, utilizando uma linguagem interpretada altamente documentada.

**Desempenho:** O consumo de recursos é superior, situando-se geralmente acima dos 60 MB de memória RAM, uma vez que requer o empacotamento do interpretador Python para distribuição em Windows e Mac.

**Captura de dados:** É o ambiente com maior diversidade de bibliotecas prontas para interagir com o sistema operativo (como pyobjc para Mac ou pywin32 para Windows). A IA consegue escrever scripts autónomos que acedem a manipuladores de janelas com facilidade.

**Eficiência com IA:** Esta linguagem regista a maior taxa de sucesso na geração de código por assistentes virtuais. Os modelos possuem um histórico vasto de treino com estas bibliotecas, minimizando erros de compilação ou problemas de tipagem complexos.

**Decisão estratégica:** Se o foco principal for o consumo mínimo de recursos em segundo plano, a arquitetura híbrida do Tauri é a escolha certa, exigindo apenas maior detalhe nas instruções dadas à IA para a componente Rust. Caso pretenda rapidez de desenvolvimento e menor probabilidade de erros na captura do sistema, o Python mitiga os riscos de programação.

### Recursos necessários para o utilitário

Para estruturar esta aplicação em Python mantendo o foco na leveza e na eficácia da geração de código por inteligência artificial, os recursos dividem-se entre módulos nativos e pacotes especializados.

#### Interface e controlo em segundo plano
- **pystray:** Permite criar o ícone na barra de tarefas (Windows) ou na barra de menus (macOS), garantindo que a aplicação corre de forma oculta sem necessidade de uma janela principal aberta permanentemente.
- **CustomTkinter:** Fornece uma interface visual moderna, esguia e de carregamento rápido. Utiliza o motor nativo do sistema operativo, evitando o consumo excessivo de memória de outras soluções visuais mais pesadas.
- **pynput:** Biblioteca responsável pela escuta global do teclado, permitindo configurar o atalho que invoca ou oculta a interface instantaneamente a partir de qualquer aplicação.

#### Captura de dados e contexto
A recolha do ambiente de trabalho exige bibliotecas específicas por plataforma para interagir diretamente com o sistema operativo.

- **pywin32 (exclusivo para Windows):** Fornece acesso às APIs nativas da Microsoft (Win32 e UI Automation), necessárias para extrair o título da janela ativa, identificar o processo em execução e recolher URLs do Outlook ou de navegadores de internet.
- **pyobjc (exclusivo para macOS):** Estabelece a ponte com a estrutura Cocoa e com as APIs de acessibilidade da Apple, permitindo ler os metadados das aplicações ativas no Mac.
- **pyperclip ou pandas (apenas a componente de clipboard):** Garante a leitura e validação do texto guardado na área de transferência de forma multiplataforma.

#### Persistência e distribuição
- **pathlib:** Módulo nativo do Python que faz a gestão de caminhos de ficheiros de forma agnóstica, assegurando que a escrita de ficheiros Markdown e blocos YAML funciona de igual modo em Windows e Mac.
- **PyInstaller:** Ferramenta utilizada para compilar o código final num ficheiro executável independente (.exe ou .app), permitindo a execução do utilitário sem necessidade de instalar o interpretador Python na máquina de trabalho.

---

# Tutorial: Web App User Guide

## 1. Configuração Inicial e Instalação (Fricção Zero)

Como o sistema foi desenhado sob a arquitetura **PWA (Progressive Web App)** hospedada na Vercel, não precisa de descarregar ficheiros `.apk` ou usar a Play Store.

1. Abra o **Google Chrome** no seu dispositivo Android.
2. Aceda ao URL privado da sua aplicação (ex: `https://o-seu-monolith.vercel.app`).
3. Introduza a sua chave simétrica de cifragem (`MONOLITH_CRYPTO_KEY`) no painel de configuração inicial. Esta chave fica guardada no `localStorage` seguro do seu browser.
4. Clique na barra de notificações inferior do Chrome que diz **"Adicionar Paperclip ao ecrã principal"** (ou aceda ao menu de três pontos do Chrome e selecione essa opção).
5. O ícone da aplicação surgirá no ecrã do seu telemóvel. Feche o Chrome.

---

## 2. O Fluxo Diário de Captura de Texto

1. Toque no ícone do **Paperclip** no ecrã principal do seu Android. A aplicação abre instantaneamente em modo de ecrã inteiro, ocultando a barra de endereço do navegador.
2. O cursor foca-se imediatamente no editor de texto.
3. **Selecione o Contexto:** Deslize horizontalmente o menu de pílulas no topo e selecione o tema da nota (ex: toque em **Futuro Digital**).
4. Escreva a sua nota cândida ou pensamento efémero.
5. **Colagem Rápida:** Se acabou de copiar um link de um email ou documento, toque no botão discreto **`[Tab] Anexar Link`** no rodapé para injetar o URL formatado em Markdown no fim do texto.
6. Toque no botão **Guardar**. A interface limpa o texto e emite uma vibração curta (*haptic feedback*) confirmando o envio. Pode fechar a aplicação de imediato.

---

## 3. O Fluxo de Captura por Voz (Mãos Livres)

Ideal para quando está a caminhar ou precisa de registar um pensamento sem usar o teclado do telemóvel.

1. Abra a aplicação e selecione a aba pretendida (ex: **Família**).
2. Toque no atalho de microfone (ou utilize o botão flutuante de gravação).
3. A interface adota o tom carmesim escuro e as bordas pulsam, confirmando que o microfone do Android está ativo.
4. **Fale candidamente:** *"Comprar o processador AMD Ryzen 5 para o computador do Daniel esta semana"*.
5. **Encerramento Inteligente (VAD):** Não precisa de tocar em nada para parar. Assim que parar de falar durante mais de 2.5 segundos, o algoritmo local deteta o silêncio, encerra a gravação e envia o ficheiro de áudio comprimido para a API do Whisper.
6. O texto em Português de Portugal surge transcrito no ecrã com a pontuação correta.
7. Reveja rapidamente e toque em **Guardar**.

---

## 4. Comportamento Offline (Gestão de Redes Móveis Instáveis)

Se estiver numa zona sem cobertura de rede ou em "Modo de Avião", o sistema adapta-se automaticamente:

* Ao clicar em Guardar, a aplicação deteta a falha de rede (`Network Error`).
* O texto cifrado é desviado de forma invisível para o **IndexedDB** do Android.
* O utilizador recebe a confirmação de que a nota foi guardada localmente em segurança.
* **Sincronização Invisível:** Assim que o seu telemóvel recuperar o sinal de dados móveis ou se ligar a uma rede Wi-Fi, o Service Worker do Android deteta o estado `online`, esvazia a fila do IndexedDB em background e injeta as notas no PocketBase Cloud. Não precisa de reabrir a aplicação para que isto aconteça.

---

## 5. O Ciclo de Ingestão no PC/Mac (A Ligação ao Second Brain)

As notas acumuladas durante o seu dia através do Android encontram-se cifradas na cloud. Para as processar no seu computador:

1. Ao sentar-se na secretária, abra o seu terminal de eleição (como o Warp).
2. Execute o seu comando padrão de abertura de sessão: `obsidian-sync ai-start`.
3. O script automático `pull_pocketbase.py` entra em ação:
   * Saca os payloads do PocketBase.
   * Decifra o texto com a chave local.
   * Transforma a primeira linha em título formatado em *Sentence case*.
   * Sanitiza os nomes dos ficheiros em conformidade com a sua **Regra 5** (sem acentos ou caracteres especiais).
   * Deposita os ficheiros `.md` limpos com o bloco YAML correto diretamente na sua pasta física `00-inbox/`.

4. O seu agente de IA (como o Claude Code) assume o controlo a partir daqui, lendo a pasta de inbox, aplicando a taxonomia *Johnny.Decimal* e distribuindo as notas pelas pastas finais, sem qualquer risco de conflito com o repositório Git central.

---

## Summary

The **Paperclip** system is a multi-platform quick capture system for the obsidian-ht Second Brain ecosystem:

- **Desktop App (PRD1):** Python/PySide6 native app with local SQLite, system tray integration, global hotkeys, and audio transcription
- **Web/PWA App (PRD2):** Next.js on Vercel for mobile/browser access with offline support via IndexedDB
- **Backend:** PocketBase Cloud for async sync, AES-256-GCM encryption, and ingestion into obsidian-ht/00-inbox/
- **Key Features:** Zero-friction capture, contextual tabs (Inbox/Família/Passaporte/Futuro/Freelance), clipboard integration, voice transcription (Whisper), offline-first architecture
