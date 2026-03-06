# 🚀 URLDownloader

Um downloader de YouTube robusto, desenvolvido em Python, focado em performance e controle total via terminal. 
Este projeto utiliza o poder do `yt-dlp` e 
um gerenciador de threads para permitir múltiplos downloads simultâneos sem travar a interface.

---
## 🎯 Objetivo do Projeto
Criar uma ferramenta de linha de comando (CLI) que permita ao usuário baixar vídeos ou apenas áudios do YouTube na máxima qualidade possível.

---
# 💡 Insights Técnicos e Arquitetura

Para garantir que este projeto seja de alto nível, aplicamos os seguintes conceitos:

### 🧵 Gerenciamento Inteligente de Threads

Utilizamos o ThreadPoolExecutor para gerenciar o ciclo de vida dos downloads.

- Vantagem: Evitamos o overhead de criar e destruir threads manualmente.

- Resiliência: O pool limita o número de downloads simultâneos (ex: 4), evitando que o seu IP seja bloqueado pelo YouTube por excesso de requisições ou que sua banda larga sofra um gargalo total.

### 🔓 O "Mito" do GIL (Global Interpreter Lock)

Muitos evitam threads em Python devido ao GIL, mas neste projeto ele não é um problema. Como o download é uma tarefa de I/O-Bound (espera de rede), as threads liberam o lock enquanto aguardam os dados, permitindo que a CPU gerencie múltiplas conexões de rede simultaneamente com eficácia quase total.

### 🪝 Progress Hooks em Tempo Real
Em vez de ler a saída do terminal (stdout) como um processo externo faria, usamos os progress_hooks nativos do yt-dlp.

Isso nos permite capturar um dicionário de dados preciso (porcentagem, velocidade, ETA) e passá-lo para atualizar as barras de progresso sem flicker (tremulação) na tela.
