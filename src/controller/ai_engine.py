import random
import pygame

class AIEngine:
    @staticmethod
    def pensar_e_jogar(item_jogador, assets_mgr, nome_deck, turn_mgr):
        bot = item_jogador['player']
        fase_atual = turn_mgr.get_fase_atual().upper()

        if "MAIN" in fase_atual:
            acao_realizada = AIEngine._executar_logica_principal(bot, assets_mgr, nome_deck)
            
            if not acao_realizada:
                print(f"BOT [{bot.name}]: Sem jogadas disponíveis. Passando...")
                turn_mgr.proxima_fase(bot, assets_mgr, nome_deck)
        else:
            # Pula fases automáticas ou de combate (por enquanto)
            turn_mgr.proxima_fase(bot, assets_mgr, nome_deck)

    @staticmethod
    def _executar_logica_principal(bot, assets_mgr, nome_deck):
        # --- 1. JOGAR TERRENO ---
        if bot.lands_played < bot.max_lands_per_turn:
            terrenos = [c for c in bot.hand if getattr(c, 'is_land', False)]
            if terrenos:
                terreno = terrenos[0] 
                bot.play_card(terreno, assets_mgr, nome_deck)
                print(f"BOT [{bot.name}]: Jogou terreno {terreno.name}")
                return True

        # --- 2. GERAR MANA ---
        if hasattr(bot, 'virar_tudo_para_gerar_mana'):
            bot.virar_tudo_para_gerar_mana()

        # --- 3. CONJURAR MÁGICAS ---
        # Filtramos apenas o que não é terreno
        nao_terrenos = [c for c in bot.hand if not getattr(c, 'is_land', False)]
        
        for carta in nao_terrenos:
            # USANDO O NOVO MÉTODO DA CLASSE CARD:
            # Isso garante que o Bot entenda custos como {1}{W}{B} corretamente
            custo_formatado = carta.get_mana_dict()

            # O Player tenta pagar o custo real
            if bot.auto_tap_for_cost(custo_formatado):
                bot.play_card(carta, assets_mgr, nome_deck)
                print(f"BOT [{bot.name}]: Conjurou {carta.name} pagando {carta.mana_cost}")
                return True
        
        return False
