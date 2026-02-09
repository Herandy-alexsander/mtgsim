class TurnManager:
    def __init__(self):
        # Ordem das fases do Magic (Mantidas conforme seu original)
        self.fases = [
            "UNTAP", "UPKEEP", "DRAW", 
            "MAIN 1", 
            "BEGIN COMBAT", "DECLARE ATTACKERS", "DECLARE BLOCKERS", "DAMAGE", "END COMBAT", 
            "MAIN 2", 
            "END STEP", "CLEANUP"
        ]
        self.fase_atual_idx = 0
        
        # --- [ATRIBUTOS DE ESTADO DO JOGO] ---
        self.jogadores = []        # NOVO: Necessário para saber quem joga
        self.indice_jogador_atual = 0 # NOVO: Para saber de quem é o turno
        self.quantidade_mulligans = 0
        self.em_mulligan = True  

        # --- [SISTEMA DE ALVOS / SELEÇÃO] ---
        self.modo_selecao = False    
        self.origem_alvo = None      
        self.callback_alvo = None    

    # --- [NOVOS MÉTODOS DE INTEGRAÇÃO] ---

    def inicializar_jogadores(self, lista_jogadores):
        """Método que o main.py chama para registrar os participantes."""
        self.jogadores = lista_jogadores
        self.indice_jogador_atual = 0
        self.fase_atual_idx = 0
        print(f"Partida inicializada com {len(self.jogadores)} jogadores.")

    def get_jogador_atual(self):
        """Retorna o objeto Player que detém o turno ativo."""
        if not self.jogadores:
            return None
        return self.jogadores[self.indice_jogador_atual]

    # --- [MÉTODOS ORIGINAIS ATUALIZADOS] ---

    def get_fase_atual(self):
        return self.fases[self.fase_atual_idx]

    def proxima_fase(self, jogador, assets_mgr, nome_deck):
        """Avança as fases e pula automaticamente as etapas burocráticas."""
        if self.em_mulligan:
            print("Decida o Mulligan antes de prosseguir.")
            return

        if self.modo_selecao:
            print(f"Defina o alvo para {self.origem_alvo.name} antes de mudar de fase!")
            return

        # Avança para a próxima fase
        self.fase_atual_idx += 1
        
        # Se passar do Cleanup, muda o turno para o próximo jogador
        if self.fase_atual_idx >= len(self.fases):
            self.proximo_turno()
            # Após mudar o turno, o novo jogador começa no UNTAP
            novo_jogador = self.get_jogador_atual()
            self.executar_fase_automatica(novo_jogador, assets_mgr, nome_deck)
            return
        
        self.executar_fase_automatica(jogador, assets_mgr, nome_deck)

    def executar_fase_automatica(self, jogador, assets_mgr, nome_deck):
        """Encapsula a sua lógica de saltos automáticos para evitar repetição."""
        fase = self.get_fase_atual()

        if fase == "UNTAP":
            print(">>> Automatizando: Untap Step")
            jogador.untap_all()
            # Zera a mana pool no início do turno
            if hasattr(jogador, 'mana_pool'):
                jogador.mana_pool = {cor: 0 for cor in jogador.mana_pool}
            self.proxima_fase(jogador, assets_mgr, nome_deck)
            
        elif fase == "UPKEEP":
            print(">>> Automatizando: Upkeep Step")
            self.proxima_fase(jogador, assets_mgr, nome_deck)
            
        elif fase == "DRAW":
            print(">>> Automatizando: Draw Step")
            jogador.draw(assets_mgr, 1, nome_deck)
            self.proxima_fase(jogador, assets_mgr, nome_deck)
            
        elif fase == "CLEANUP":
            print(">>> Automatizando: Cleanup Step")
            if len(jogador.hand) > 7:
                print(f"Atenção: Você tem {len(jogador.hand)} cartas. Precisa descartar.")
            else:
                self.proxima_fase(jogador, assets_mgr, nome_deck)
        else:
            print(f"--- AGUARDANDO JOGADOR: {fase} ---")

    def proximo_turno(self):
        """Muda o índice para o próximo jogador da lista."""
        self.indice_jogador_atual = (self.indice_jogador_atual + 1) % len(self.jogadores)
        self.fase_atual_idx = 0
        print(f"--- TURNO DE: {self.get_jogador_atual().name} ---")

    def finalizar_mulligan(self):
        self.em_mulligan = False
        print("Mão mantida! O jogo começou.")

    def registrar_mulligan(self):
        self.quantidade_mulligans += 1

    def reset_turn(self):
        self.fase_atual_idx = 0
