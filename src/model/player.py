import random
from src.model.card import Card

class Player:
    def __init__(self, name, deck_list):
        """
        Representa um jogador no sistema.
        Gerencia as zonas (mão, campo, deck), vida e a reserva de mana.
        """
        self.name = name
        self.library = list(deck_list)
        self.hand = []                  # Lista de OBJETOS Card
        self.battlefield = []           # Cartas em jogo (Permanentes)
        self.grave = []                 # Cemitério
        self.life = 40                  # Vida padrão Commander
        
        # --- [ATRIBUTOS DE REGRAS] ---
        self.mana_pool = {
            "white": 0, "blue": 0, "black": 0, 
            "red": 0, "green": 0, "colorless": 0
        }
        self.lands_played = 0           # Contador de terrenos baixados no turno
        self.max_lands_per_turn = 1     # Limite padrão por regra

    def shuffle(self):
        """Embaralha a biblioteca do jogador."""
        random.shuffle(self.library)

    def draw(self, assets_mgr, quantidade, nome_deck):
        """Compra múltiplas cartas chamando a lógica de criação de objetos Card."""
        for _ in range(quantidade):
            if self.library:
                nome_carta = self.library.pop(0)
                nova_carta = Card(nome_carta, assets_mgr, nome_deck)
                self.hand.append(nova_carta)

    # --- [NOVO: MÉTODO QUE ESTAVA FALTANDO] ---
    def play_card(self, card, assets_mgr, nome_deck):
        """
        Executa a jogada de uma carta da mão para o campo.
        Este método resolve o erro 'AttributeError: Player object has no attribute play_card'.
        """
        if card in self.hand:
            self.hand.remove(card)
            self.battlefield.append(card)
            
            # Se for terreno, incrementa o contador para o RulesEngine validar
            if card.is_land:
                self.lands_played += 1
            
            print(f"JOGADOR {self.name}: Jogou {card.name}")
            return True
        return False

    def change_life(self, quantidade):
        """Altera os pontos de vida (dano ou cura)."""
        self.life += quantidade

    def untap_all(self):
        """Fase de Desvirar: Reinicia o estado das cartas e os contadores do turno."""
        for card in self.battlefield:
            card.tapped = False
        self.lands_played = 0
        self.mana_pool = {cor: 0 for cor in self.mana_pool}

    # --- [LÓGICA DE MANA E AUTO-TAP] ---

    def auto_tap_for_cost(self, mana_cost_str):
        """Tenta pagar um custo de mana automaticamente virando terrenos."""
        from src.controller.rules_engine import RulesEngine
        custo = RulesEngine._parse_mana_cost(mana_cost_str)
        
        # 1. Tenta pagar com o que já está na reserva
        for cor in custo:
            if cor in self.mana_pool:
                usado = min(custo[cor], self.mana_pool[cor])
                custo[cor] -= usado
                self.mana_pool[cor] -= usado

        # 2. Vira terrenos para o que ainda falta pagar
        terrenos_disponiveis = [c for c in self.battlefield if c.is_land and not c.tapped]
        
        for terreno in terrenos_disponiveis:
            if sum(v for k, v in custo.items() if k != 'generic') <= 0 and custo.get('generic', 0) <= 0:
                break
                
            cor_terreno = self.get_land_color(terreno)
            
            if custo.get(cor_terreno, 0) > 0:
                custo[cor_terreno] -= 1
                terreno.tapped = True
            elif custo.get('generic', 0) > 0:
                custo['generic'] -= 1
                terreno.tapped = True

        return sum(custo.values()) <= 0

    def get_land_color(self, card):
        tl = card.type_line.lower()
        if "forest" in tl: return "green"
        if "island" in tl: return "blue"
        if "mountain" in tl: return "red"
        if "swamp" in tl: return "black"
        if "plains" in tl: return "white"
        return "colorless"

    # --- [ORGANIZAÇÃO VISUAL] ---

    def organize_hand(self, screen_w, screen_h, quad_x, quad_y):
        if not self.hand: return
        espacamento = 85
        largura_total = len(self.hand) * espacamento
        inicio_x = quad_x + (screen_w // 2) - (largura_total // 2)
        
        for i, card in enumerate(self.hand):
            if not card.dragging:
                card.rect.x = inicio_x + (i * espacamento)
                card.rect.y = quad_y + screen_h - 150

    def organize_battlefield(self, screen_w, screen_h, quad_x, quad_y):
        terrenos = [c for c in self.battlefield if c.is_land]
        outros = [c for c in self.battlefield if not c.is_land]
        
        for i, card in enumerate(terrenos):
            if not card.dragging:
                card.rect.x = quad_x + 20 + (i * 85)
                card.rect.y = quad_y + screen_h - 280
                
        for i, card in enumerate(outros):
            if not card.dragging:
                card.rect.x = quad_x + 20 + (i * 85)
                card.rect.y = quad_y + screen_h - 410