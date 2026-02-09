import pygame

class GraveyardManager:
    def __init__(self):
        self.visivel = False
        self.jogador_sendo_visualizado = None

    def processar_sba(self, player):
        """
        Verifica State-Based Actions (SBAs).
        Garante que apenas CRIATURAS com resistência <= 0 morram.
        """
        cartas_para_remover = []
        
        for carta in player.battlefield:
            # 1. Só verificamos morte se a carta for uma CRIATURA
            # getattr evita erro caso a carta não tenha type_line
            tipo = getattr(carta, 'type_line', "").lower()
            
            if "creature" in tipo and hasattr(carta, 'toughness'):
                if carta.toughness is not None:
                    dano = getattr(carta, 'damage_marked', 0)
                    resistencia_atual = carta.toughness - dano
                    
                    if resistencia_atual <= 0:
                        cartas_para_remover.append(carta)

        # 2. Move as cartas identificadas para o cemitério
        for carta in cartas_para_remover:
            print(f">>> SBA: {carta.name} morreu e foi para o cemitério.")
            self.enviar_para_cemiterio(player, carta)

    def enviar_para_cemiterio(self, player, carta):
        """Remove a carta do campo e adiciona à lista de graveyard do jogador."""
        if carta in player.battlefield:
            player.battlefield.remove(carta)
            
            # Reseta status da carta
            carta.tapped = False
            if hasattr(carta, 'damage_marked'): 
                carta.damage_marked = 0
            if hasattr(carta, 'is_hovered'): 
                carta.is_hovered = False
            
            # Adiciona ao cemitério
            if not hasattr(player, 'graveyard'):
                player.graveyard = []
            player.graveyard.append(carta)

    def abrir_visualizacao(self, player):
        self.visivel = True
        self.jogador_sendo_visualizado = player

    def fechar_visualizacao(self):
        self.visivel = False
        self.jogador_sendo_visualizado = None
