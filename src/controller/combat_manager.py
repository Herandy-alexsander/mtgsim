class CombatManager:
    def __init__(self):
        """
        Gerencia as declarações de ataque, bloqueio e a resolução de dano.
        Suporta múltiplos alvos para o modo Commander.
        """
        # Lista de tuplas: (objeto_carta_atacante, indice_do_alvo)
        self.fila_ataque = [] 

    def registrar_ataque(self, carta, alvo_idx, rules_engine, turn_mgr):
        """
        Valida se a criatura pode atacar o oponente selecionado e a adiciona à fila.
        """
        pode_atacar, erro = rules_engine.can_attack(carta, turn_mgr)
        
        if pode_atacar:
            # Vira a criatura (custo de atacar)
            carta.tapped = True
            self.fila_ataque.append((carta, alvo_idx))
            print(f"COMBATE: {carta.name} declarada contra Jogador {alvo_idx}")
            return True
        else:
            print(f"ERRO DE COMBATE: {erro}")
            return False

    def resolver_dano_total(self, lista_jogadores, rules_engine):
        """
        Percorre a fila de ataque e aplica o dano nos jogadores alvo.
        Deve ser chamado no 'update' do main.py quando a fase for 'DAMAGE'.
        """
        if not self.fila_ataque:
            return

        print("--- RESOLVENDO DANO DE COMBATE ---")
        for atacante, alvo_idx in self.fila_ataque:
            # Localiza o jogador defensor na lista de jogadores ativos
            # O alvo_idx corresponde ao índice na lista jogadores_ativos do main.py
            defensor = lista_jogadores[alvo_idx]['player']
            
            # O RulesEngine aplica a subtração de vida
            rules_engine.resolve_combat_damage(atacante, defensor)
            
        # Limpa a fila após o dano ser processado
        self.limpar_combate()

    def limpar_combate(self):
        """Reseta a fila de ataque para o próximo turno/fase."""
        self.fila_ataque = []