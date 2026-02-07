class TurnManager:
    def __init__(self):
        # Ordem oficial das fases do Magic: The Gathering
        self.fases = [
            "UNTAP", "UPKEEP", "DRAW", 
            "MAIN 1", 
            "BEGIN COMBAT", "DECLARE ATTACKERS", "DECLARE BLOCKERS", "DAMAGE", "END COMBAT", 
            "MAIN 2", 
            "END STEP", "CLEANUP"
        ]
        self.fase_atual_idx = 0
        self.indice_jogador_ativo = 0  # 0 é sempre o jogador humano, 1-3 são bots
        
        # --- [ATRIBUTOS DE ESTADO DO JOGO] ---
        self.quantidade_mulligans = 0
        self.em_mulligan = True  # O jogo começa na fase de decisão de mão

        # --- [SISTEMA DE ALVOS / SELEÇÃO] ---
        self.modo_selecao = False    
        self.origem_alvo = None      
        self.callback_alvo = None    

    def get_fase_atual(self):
        return self.fases[self.fase_atual_idx]

    def e_turno_do_jogador(self, slot_jogador):
        """
        Verifica se o slot do jogador atual é o que detém o turno.
        Resolva o erro AttributeError no AIEngine.
        """
        return self.indice_jogador_ativo == slot_jogador

    def proxima_fase(self, jogador_atual, assets_mgr, nome_deck, total_jogadores=4):
        """
        Avança as fases e gerencia a troca de turno entre os jogadores da sala.
        """
        if self.em_mulligan:
            print("Decida o Mulligan antes de prosseguir.")
            return

        if self.modo_selecao:
            print(f"Defina o alvo para {self.origem_alvo.name} antes de mudar de fase!")
            return

        # Avança para a próxima fase na lista
        self.fase_atual_idx += 1
        
        # Se passar do Cleanup (fim do turno), volta ao Untap e passa para o próximo jogador
        if self.fase_atual_idx >= len(self.fases):
            self.fase_atual_idx = 0
            self.indice_jogador_ativo = (self.indice_jogador_ativo + 1) % total_jogadores
            print(f"\n>>> NOVO TURNO: Jogador {self.indice_jogador_ativo}")
            
        fase = self.get_fase_atual()

        # --- LÓGICA DE SALTO AUTOMÁTICO (Etapas Administrativas) ---
        # Estas fases acontecem instantaneamente para agilizar o gameplay
        if fase == "UNTAP":
            jogador_atual.untap_all()
            # Reinicia a reserva de mana para o novo turno
            if hasattr(jogador_atual, 'mana_pool'):
                jogador_atual.mana_pool = {cor: 0 for cor in jogador_atual.mana_pool}
            self.proxima_fase(jogador_atual, assets_mgr, nome_deck, total_jogadores)
            return

        if fase == "UPKEEP":
            # Aqui poderiam ser disparados efeitos de "No início da sua manutenção"
            self.proxima_fase(jogador_atual, assets_mgr, nome_deck, total_jogadores)
            return

        if fase == "DRAW":
            jogador_atual.draw(assets_mgr, 1, nome_deck)
            self.proxima_fase(jogador_atual, assets_mgr, nome_deck, total_jogadores)
            return

        # --- LÓGICA DE FIM DE TURNO ---
        if fase == "CLEANUP":
            # Verifica limite de cartas na mão (Regra de 7 cartas)
            if len(jogador_atual.hand) > 7:
                print(f"Jogador {self.indice_jogador_ativo} precisa descartar cartas.")
            else:
                self.proxima_fase(jogador_atual, assets_mgr, nome_deck, total_jogadores)
                return

        print(f"--- FASE ATUAL: {fase} (Jogador {self.indice_jogador_ativo}) ---")

    def finalizar_mulligan(self):
        """Encerra a fase de mulligan e permite o início do jogo."""
        self.em_mulligan = False
        print("Mão mantida! O jogo começou.")

    def registrar_mulligan(self):
        """Incrementa o contador de mulligans."""
        self.quantidade_mulligans += 1

    def reset_turn(self):
        """Reseta o ciclo para o início do jogo."""
        self.fase_atual_idx = 0
        self.indice_jogador_ativo = 0