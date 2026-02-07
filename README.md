# 🎴 MTG Commander Simulator – Pygame

## 📌 Visão Geral
Este projeto é um **simulador de Magic: The Gathering** focado no formato **Commander**, desenvolvido em **Python com Pygame**.  
O sistema evoluiu de um conceito estático para um **protótipo funcional offline**, capaz de rodar partidas completas com até **4 jogadores (Humano vs Bots)**, com regras automatizadas.

---

## 🎯 Objetivo do Projeto
Criar um jogo de cartas que:
- Utilize **Pygame** como base gráfica
- Funcione inicialmente em modo **offline**
- Evolua para **multiplayer online**
- Possua sistema de cartas **data-driven (JSON)**
- Seja **escalável, organizado e seguro**

---

## 🧠 Conceito do Jogo
- **Partidas:** Por turnos
- **Jogadores:** Até 4
- **Deck:** Um deck por jogador
- **Comandante:** Define identidade de cores e regras
- **Regras:** Inspiradas em Commander (EDH), porém **simplificadas**
- **Foco:** Estratégia e interação política multiplayer

---

## 🚀 Status Atual do Protótipo
- Salas dinâmicas para 2–4 jogadores
- IA autônoma funcional
- Rules Engine com validação de mana e timing
- Motor de combate multi-alvo
- Interface sem sobreposição visual

---

## 🧱 Estrutura do Projeto
```
src/
├── model/
│   ├── card.py
│   ├── player.py
│   └── turn_manager.py
├── view/
│   ├── menu_view.py
│   ├── table_manager.py
│   └── ui_components.py
├── controller/
│   ├── ai_engine.py
│   ├── combat_manager.py
│   ├── input_handler.py
│   └── rules_engine.py
└── main.py
```

---

## 🐍 Tecnologias
- Python
- Pygame
- Sockets (planejado)
- SQLite / PostgreSQL / Redis (planejado)

---

## 🃏 Sistema de Cartas (JSON)
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

---

## 🌐 Arquitetura Multiplayer
Modelo **Client–Server Autoritativo**, com validação total no servidor.

---

## 🚧 Roadmap

### ✅ Concluído
- Stack definida
- MVC estruturado
- IA funcional
- Combate implementado

### ⚠️ Em Produção
- Efeitos avançados via JSON
- Seleção de alvos
- Histórico de partidas

### ❌ Não Iniciado
- Multiplayer online
- Lobby
- Feedback visual

---

## 📄 Licença
Projeto educacional e experimental.
