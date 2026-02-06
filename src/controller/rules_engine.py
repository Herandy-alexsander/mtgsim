import re

class RulesEngine:
    @staticmethod
    def can_play(player, card, fase_atual):
        """
        Retorna True se a jogada for permitida. 
        Tenta pagar com a reserva atual ou via Auto Tap (virando terrenos).
        """
        # --- TRAVA DE SEGURANÇA ---
        if not hasattr(card, 'type_line') or not card.type_line:
            print(f"ERRO: Dados de '{card.name}' não carregados. Jogada bloqueada.")
            return False

        fase_nome = fase_atual.lower()
        is_main_phase = "main" in fase_nome or "principal" in fase_nome
        # Melhorei a detecção de Flash para checar tanto no type_line quanto no oracle_text
        has_flash = "flash" in card.type_line.lower() or "flash" in getattr(card, 'oracle_text', '').lower()
        
        print(f"\n--- ANALISANDO JOGADA: {card.name} ---")

        # REGRA 1: Sincronia de Fase
        if not (card.is_instant or has_flash) and not is_main_phase:
            print(f"Bloqueado: {card.name} exige Fase Principal.")
            return False

        # REGRA 2: Terrenos
        if card.is_land:
            lands_limit = getattr(player, 'max_lands_per_turn', 1)
            lands_count = getattr(player, 'lands_played', 0)
            if lands_count >= lands_limit:
                print(f"Bloqueado: Limite de {lands_limit} terreno(s) atingido.")
                return False
            return True

        # REGRA 3: Mana (Com Auto Tap)
        # --- CORREÇÃO AQUI: Se não existe o dict, nós criamos a partir da string ---
        custo = getattr(card, 'mana_cost_dict', None)
        if not custo and hasattr(card, 'mana_cost'):
            custo = RulesEngine._parse_cost_to_dict(card.mana_cost)
            card.mana_cost_dict = custo # Salva na carta para não ter que processar de novo

        if not custo:
            print(f"ERRO: Custo de mana de {card.name} não definido.")
            return False

        # 1. Tentar pagar apenas com a reserva atual (Mana Pool)
        if RulesEngine._validar_pagamento(player.mana_pool, custo):
            print(f"Sucesso: {card.name} pago com reserva atual!")
            RulesEngine._pagar_custo(player, custo)
            return True

        # 2. Se não deu, tentar o AUTO TAP
        print(f"Reserva insuficiente. Tentando Auto Tap...")
        
        # Criamos uma pool imaginária: Reserva Atual + Potencial dos Terrenos Desvirados
        pool_simulada = player.mana_pool.copy()
        terrenos_disponiveis = [c for c in player.battlefield if c.is_land and not c.tapped]
        
        for terreno in terrenos_disponiveis:
            cor_produzida = RulesEngine._get_land_color(terreno)
            pool_simulada[cor_produzida] = pool_simulada.get(cor_produzida, 0) + 1

        # Validamos se com o potencial dos terrenos a conta fecha
        if RulesEngine._validar_pagamento(pool_simulada, custo):
            print(f"Sucesso: {card.name} será pago via Auto Tap!")
            if hasattr(player, 'auto_tap_for_cost'):
                player.auto_tap_for_cost(custo)
                return True
            else:
                print("ERRO: Método auto_tap_for_cost não encontrado no Player.")
                return False

        print(f"Bloqueado: Mana insuficiente mesmo com terrenos disponíveis.")
        return False

    @staticmethod
    def _parse_cost_to_dict(mana_str):
        """Converte {1}{W}{B} para {'generic': 1, 'white': 1, 'black': 1}"""
        dict_cost = {"white":0, "blue":0, "black":0, "red":0, "green":0, "colorless":0, "generic":0}
        if not mana_str: return dict_cost
        
        mapping = {'W': 'white', 'U': 'blue', 'B': 'black', 'R': 'red', 'G': 'green', 'C': 'colorless'}
        symbols = re.findall(r'\{(.*?)\}', mana_str)
        
        for s in symbols:
            if s.isdigit():
                dict_cost["generic"] += int(s)
            elif s in mapping:
                dict_cost[mapping[s]] += 1
            elif '/' in s: # Exemplo {W/B}
                # Para simplificar auto-tap, tratamos híbrido como a primeira cor
                cor_hibrida = mapping.get(s.split('/')[0], 'generic')
                dict_cost[cor_hibrida] += 1
        return dict_cost

    @staticmethod
    def _validar_pagamento(pool, custo):
        """Apenas verifica se uma determinada pool cobre um custo, sem subtrair nada."""
        temp_pool = pool.copy()
        # Cores específicas
        for cor in ["white", "blue", "black", "red", "green", "colorless"]:
            valor_custo = custo.get(cor, 0)
            if valor_custo > temp_pool.get(cor, 0):
                return False
            temp_pool[cor] -= valor_custo
        
        # Genérico (pode ser pago por qualquer sobra de qualquer cor)
        total_restante = sum(temp_pool.values())
        return custo.get("generic", 0) <= total_restante

    @staticmethod
    def _get_land_color(card):
        """Detecta que cor o terreno produz."""
        tl = card.type_line.lower()
        if "forest" in tl: return "green"
        if "island" in tl: return "blue"
        if "mountain" in tl: return "red"
        if "swamp" in tl: return "black"
        if "plains" in tl: return "white"
        return "colorless"

    @staticmethod
    def _pagar_custo(player, custo):
        """Subtrai a mana da reserva do jogador de forma inteligente."""
        for cor in ["white", "blue", "black", "red", "green", "colorless"]:
            player.mana_pool[cor] -= custo.get(cor, 0)
        
        generico_pendente = custo.get("generic", 0)
        ordem_pagamento = ["colorless", "white", "blue", "black", "red", "green"]
        
        for cor in ordem_pagamento:
            while generico_pendente > 0 and player.mana_pool.get(cor, 0) > 0:
                player.mana_pool[cor] -= 1
                generico_pendente -= 1
