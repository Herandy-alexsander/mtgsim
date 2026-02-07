import re

class RulesEngine:
    @staticmethod
    def can_play(player, card, turn_manager):
        """
        O Juiz do jogo: decide se uma jogada é legal ou não.
        IMPORTANTE: turn_manager deve ser o OBJETO, não uma string.
        """
        # Obtém a fase do objeto TurnManager
        fase_atual = turn_manager.get_fase_atual()

        # Bloqueia jogadas durante Mulligan ou Seleção
        if turn_manager.modo_selecao or turn_manager.em_mulligan:
            return False, "Aguarde a resolução atual."

        # 1. Validação de Terrenos
        if card.is_land:
            if player.lands_played >= player.max_lands_per_turn:
                return False, "Você já jogou um terreno este turno."
            if "MAIN" not in fase_atual.upper():
                return False, "Terrenos só podem ser jogados nas Fases Principais."
            return True, ""

        # 2. Validação de Custo de Mana
        # O auto_tap_for_cost deve estar implementado na classe Player
        if not player.auto_tap_for_cost(card.mana_cost):
            return False, "Mana insuficiente ou terrenos virados."

        # 3. Validação de Timing (Mágicas)
        if not card.is_instant and not card.has_flash:
            if "MAIN" not in fase_atual.upper():
                return False, "Feitiços e Criaturas só podem ser jogados nas Fases Principais."

        return True, ""

    @staticmethod
    def can_attack(card, turn_manager):
        """
        Verifica se uma criatura pode ser declarada como atacante.
        """
        fase_atual = turn_manager.get_fase_atual()
        
        if fase_atual != "DECLARE ATTACKERS":
            return False, "Ataques só podem ser declarados na fase de combate."
        
        if not card.is_creature:
            return False, "Apenas criaturas podem atacar."
            
        if card.tapped:
            return False, "Criaturas viradas não podem atacar."
            
        return True, ""

    @staticmethod
    def resolve_combat_damage(attacker, defender_player):
        """
        Aplica o dano da criatura atacante diretamente na vida do defensor.
        Garante conversão de tipos para evitar erros de cálculo.
        """
        # Converte poder para int (caso venha como string do JSON)
        try:
            dano = int(attacker.power) if attacker.power is not None else 0
        except ValueError:
            dano = 0

        # Aplica a redução de vida diretamente no atributo
        defender_player.life -= dano
        print(f"RULES: {attacker.name} causou {dano} de dano em {defender_player.name} (Vida atual: {defender_player.life})")

    @staticmethod
    def _parse_mana_cost(cost_str):
        """
        Transforma a string {2}{W}{B} em um dicionário utilizável.
        """
        if not cost_str:
            return {}
            
        symbols = re.findall(r'\{(.*?)\}', cost_str)
        parsed = {"generic": 0}
        
        mapa_cores = {
            'W': 'white', 'U': 'blue', 'B': 'black', 
            'R': 'red', 'G': 'green', 'C': 'colorless'
        }
        
        for s in symbols:
            if s.isdigit():
                parsed["generic"] += int(s)
            elif s in mapa_cores:
                cor = mapa_cores[s]
                parsed[cor] = parsed.get(cor, 0) + 1
            elif '/' in s: # Custos híbridos
                parsed["generic"] += 1
                
        return parsed