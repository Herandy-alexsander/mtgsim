# 🎴 Jogo de Cartas Multiplayer – Pygame (Formato Commander)

## 📌 Visão Geral
Este projeto é um **jogo de cartas digital**, desenvolvido em **Python com Pygame**, inspirado no formato **Commander**, com suporte planejado para **até 4 jogadores online**.

O projeto é estruturado para evoluir de um **protótipo offline** para um **jogo multiplayer online**, utilizando uma arquitetura **client–server autoritativa**.

---

## 🎯 Objetivo do Projeto
Criar um jogo de cartas que:
- Utilize **Pygame** como base gráfica.
- Funcione inicialmente em modo **offline**.
- Evolua para **multiplayer online**.
- Possua sistema de cartas **baseado em dados** (JSON).
- Seja escalável, organizado e seguro.

---

## 🧠 Conceito do Jogo
- **Partidas:** Por turnos.
- **Jogadores:** Até 4 jogadores.
- **Deck:** Cada jogador utiliza um deck próprio.
- **Identidade:** Um comandante define as cores e regras do deck.
- **Regras:** Inspiradas em Commander (EDH), porém **simplificadas** para fluidez digital.
- **Foco:** Forte interação política e estratégica entre jogadores.

---

## 🧱 Estrutura do Projeto

Abaixo segue a estrutura de pastas sugerida para manter a organização entre Cliente e Servidor:

```text
mtgsim/
├── client/
│   ├── main.py
│   ├── ui/
│   │   ├── menu.py
│   │   ├── game_screen.py
│   │   └── hud.py
│   ├── gameplay/
│   │   ├── card.py
│   │   ├── deck.py
│   │   ├── player.py
│   │   └── turn_manager.py
│   └── network/
│       └── client_socket.py
│
├── server/
│   ├── server.py
│   ├── core/
│   │   ├── game_state.py
│   │   └── rules.py
│   ├── match/
│   │   ├── lobby.py
│   │   └── match_manager.py
│   └── network/
│       └── server_socket.py
│
├── GameData/
│   ├── Cards/
│   │   ├── fireball.json
│   │   ├── heal.json
│   │   └── commander_01.json
│   ├── Decks/
│   │   └── starter_deck.json
│   └── Rules/
│       └── rules.json
│
└── docs/
    ├── GDD.md
    ├── CardSystem.md
    └── NetworkFlow.md

```

 ## 🐍 Tecnologias Utilizadas

### Cliente
- **Python**
- **Pygame**
- Comunicação via sockets

### Servidor
- **Python**
- Servidor autoritativo
- Validação de regras e ações

### Banco de Dados (planejado)
- SQLite (protótipo)
- PostgreSQL (produção)
- Redis (estado temporário das partidas)

---

## 🃏 Sistema de Cartas

As cartas são definidas por **arquivos JSON**, permitindo fácil criação, balanceamento e expansão.

### Exemplo de carta:
```json
{
  "id": "fireball_01",
  "name": "Fireball",
  "cost": 2,
  "type": "spell",
  "effect": "damage",
  "target": "player",
  "value": 3
}
```

## 🏆 Benefícios do Sistema
A arquitetura foi pensada para flexibilidade e manutenção a longo prazo:

* **Cartas Driven-Data:** As cartas não possuem lógica *hardcoded* no código-fonte; seus atributos e efeitos vêm de arquivos JSON.
* **Balanceamento Rápido:** Ajustar o custo ou dano de uma carta requer apenas a edição de um arquivo de texto.
* **Escalabilidade:** Fácil adição de novas cartas e coleções sem recompilar o jogo.
* **Redução de Bugs:** Ao separar dados de lógica, diminui-se o risco de quebrar o jogo ao adicionar conteúdo novo.

---

## 🔁 Sistema de Turnos
O jogo segue uma estrutura rígida de fases para garantir a sincronia:

* **Turnos Sequenciais:** A ordem dos jogadores é fixa.
* **Controle Centralizado:** O servidor dita quem é o jogador ativo; o cliente apenas obedece.
* **Timer:** Tempo limite por turno para evitar estagnação (planejado).
* **Anti-AFK:** Penalidades automáticas para jogadores inativos.

---

## 🌐 Arquitetura Multiplayer

### Modelo: Client–Server Autoritativo
O servidor é a "verdade absoluta" do jogo. O cliente é apenas uma interface visual.



[Image of client server architecture diagram]


### Fluxo Básico de Ação:
1.  **Cliente:** Envia uma intenção de ação (ex: "Jogar Carta X").
2.  **Servidor:** Valida as regras (Tem mana? É o turno dele? O alvo é válido?).
3.  **Servidor:** Aplica os efeitos no estado do jogo (Game State).
4.  **Sincronização:** O servidor envia o novo estado atualizado para **todos** os jogadores.

---

## 🔐 Segurança
Para garantir um ambiente justo (fair play):

* **Validação Total:** O cliente não pode alterar regras (ex: não pode setar a própria vida para 100).
* **Logs de Partida:** Registro de todas as ações para auditoria.
* **Prevenção de Trapaça:** O servidor rejeita qualquer pacote de dados que não obedeça à sequência lógica do jogo.

---

## 🚧 Status do Projeto

### ✅ Concluído
* [x] Definição do conceito e escopo (Commander).
* [x] Escolha da stack tecnológica (Python + Pygame).
* [x] Estrutura inicial de pastas e arquivos.
* [x] Planejamento de produção.
* [x] Modelagem do sistema de cartas (JSON).

### ⚠️ Em Produção
* [ ] Documento de regras iniciais.
* [ ] Protótipo offline (Single/Hotseat) em Pygame.
* [ ] Sistema básico de fases do turno.
* [ ] Leitura e renderização das cartas a partir do JSON.

### ❌ Não Iniciado
* [ ] Interface gráfica (UI/UX) final.
* [ ] Sistema de Lobby e Matchmaking.
* [ ] Código de Rede (Multiplayer Online).
* [ ] Sistema de Reconexão (Crash recovery).
* [ ] Testes com usuários reais.

---

## 🧪 Etapas de Produção (Roadmap)

### Fase 1 – Pré-produção (EM ANDAMENTO)
* Criação do GDD (Game Design Document).
* Definição das regras simplificadas.
* Protótipo conceitual.

### Fase 2 – Protótipo Offline (NÃO FINALIZADO)
* Partida jogável local.
* Sistema de cartas funcional (Parse de JSON).
* Ciclo de turnos completo (Compra -> Main -> Combate).

### Fase 3 – Multiplayer Básico
* Implementação do servidor em Python (`socket` ou `asyncio`).
* Protocolo de comunicação.
* Partidas 1v1 em rede local.

### Fase 4 – Multiplayer Completo
* Suporte a 4 jogadores (Mesa de Commander).
* Lobby e salas de espera.
* Controle de desconexão e tempo.

### Fase 5 – Polimento
* Interface final (Assets visuais).
* Animações de movimento e partículas.
* Sons e Trilha Sonora.
* Feedback visual de ações.

### Fase 6 – Testes e Lançamento
* Testes fechados (Alpha).
* Correção de bugs e balanceamento.
* Beta público.

---

## 📅 Planejamento Estimado

| Etapa | Duração Estimada |
| :--- | :--- |
| **Pré-produção** | 1 mês |
| **Protótipo Offline** | 1 mês |
| **Multiplayer Básico** | 1 mês |
| **Multiplayer Completo** | 1–2 meses |
| **Polimento e Testes** | 1 mês |
| **TOTAL ESTIMADO** | **5 a 6 meses** |

---

## 🚀 Próximos Passos Imediatos

1.  Finalizar a documentação das regras iniciais.
2.  Implementar o **Main Loop** jogável em Pygame.
3.  Criar a base de dados inicial (JSON) com as primeiras cartas.
4.  Implementar a lógica de turnos locais.
5.  Iniciar a refatoração para arquitetura Cliente-Servidor.

---

## 📄 Licença
Projeto em desenvolvimento para fins educacionais e experimentais.