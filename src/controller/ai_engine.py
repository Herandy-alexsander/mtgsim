import random
from src.controller.rules_engine import RulesEngine

class AIEngine:
    @staticmethod
    def pensar_e_jogar(item_jogador, assets_mgr, nome_deck, turn_mgr, combat_mgr, lista_jogadores):
        """
        Executa a lógica de decisão para um bot.
        item_jogador: Dicionário com {'player': objeto, 'slot': int, 'is_bot': bool}
        combat_mgr: Gerenciador para registrar ataques.
        lista_jogadores: Necessário para o bot escolher quem atacar.
        """
        bot = item_jogador['player']
        fase_atual = turn_mgr.get_fase_atual()

        # 1. VERIFICAÇÃO DE TURNO: O bot só age se o slot dele for o ativo no TurnManager
        if not turn_mgr.e_turno_do_jogador(item_jogador['slot']):
            return

        # 2. LÓGICA DE FASE PRINCIPAL (MAIN 1 e MAIN 2)
        if "MAIN" in fase_atual.upper() or "PRINCIPAL" in fase_atual.upper():
            AIEngine._executar_fase_principal(bot, assets_mgr, nome_deck, turn_mgr)

        # 3. LÓGICA DE COMBATE (DECLARAÇÃO DE ATACANTES)
        elif fase_atual == "DECLARE ATTACKERS":
            AIEngine.executar_combate(bot, combat_mgr, turn_mgr, lista_jogadores)

    @staticmethod
    def _executar_fase_principal(bot, assets_mgr, nome_deck, turn_mgr):
        """
        O Bot tenta jogar 1 terreno e 1 mágica por ativação para não 'atropelar' o jogo.
        """
        # Tentar jogar terreno primeiro (Regra: 1 por turno)
        terrenos_na_mao = [c for c in bot.hand if c.is_land]
        for terreno in terrenos_na_mao:
            if RulesEngine.can_play(bot, terreno, turn_mgr):
                bot.play_card(terreno, assets_mgr, nome_deck)
                print(f"BOT [{bot.name}]: Jogou terreno {terreno.name}")
                break 

        # Tentar jogar uma carta de criatura ou feitiço
        nao_terrenos = [c for c in bot.hand if not c.is_land]
        random.shuffle(nao_terrenos) # Dá variedade às jogadas do bot

        for carta in nao_terrenos:
            if RulesEngine.can_play(bot, carta, turn_mgr):
                bot.play_card(carta, assets_mgr, nome_deck)
                print(f"BOT [{bot.name}]: Conjurou {carta.name}")
                break 

    @staticmethod
    def executar_combate(bot, combat_mgr, turn_mgr, lista_jogadores):
        """
        O Bot escolhe alvos aleatórios entre os oponentes para suas criaturas prontas.
        """
        # Seleciona criaturas que podem atacar (não viradas e com poder > 0)
        atacantes = [c for c in bot.battlefield if c.is_creature and not c.tapped]
        
        if atacantes:
            for criatura in atacantes:
                # O Bot identifica quem são os oponentes (indices da lista que não são ele)
                indices_oponentes = [i for i in range(len(lista_jogadores)) if i != turn_mgr.indice_jogador_ativo]
                
                if indices_oponentes:
                    alvo_idx = random.choice(indices_oponentes)
                    # O CombatManager registra o ataque e vira a carta
                    sucesso = combat_mgr.registrar_ataque(criatura, alvo_idx, RulesEngine, turn_mgr)
                    if sucesso:
                        print(f"BOT [{bot.name}]: Atacando Jogador {alvo_idx} com {criatura.name}")