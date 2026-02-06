import random

class AIEngine:
    @staticmethod
    def pensar_e_jogar(item_jogador, assets_mgr, nome_deck, turn_mgr):
        """
        Executa a lógica de decisão para um bot.
        item_jogador: dicionário {'player': obj, 'slot': int, 'is_bot': bool}
        """
        bot = item_jogador['player']
        fase_atual = turn_mgr.get_fase_atual().lower()

        # O Bot só age se for o turno dele (ou você pode permitir reações simples)
        # Por enquanto, vamos focar no básico de Main Phase
        if "main" in fase_atual:
            AIEngine._executar_fase_principal(bot, assets_mgr, nome_deck)

    @staticmethod
    def _executar_fase_principal(bot, assets_mgr, nome_deck):
        # 1. Tentar jogar um terreno (prioridade máxima)
        if bot.lands_played < bot.max_lands_per_turn:
            terrenos_na_mao = [c for c in bot.hand if c.is_land]
            if terrenos_na_mao:
                terreno = random.choice(terrenos_na_mao)
                bot.play_card(terreno, assets_mgr, nome_deck)
                print(f"BOT [{bot.name}]: Jogou terreno {terreno.name}")

        # 2. Tentar jogar uma carta não-terreno aleatória (se tiver mana)
        # Nota: Futuramente integrar com o sistema de custo de mana
        nao_terrenos = [c for c in bot.hand if not c.is_land]
        if nao_terrenos:
            carta = random.choice(nao_terrenos)
            # Simulação simples: Bot tem 30% de chance de conjurar algo por turno
            if random.random() < 0.3:
                bot.play_card(carta, assets_mgr, nome_deck)
                print(f"BOT [{bot.name}]: Conjurou {carta.name}")
