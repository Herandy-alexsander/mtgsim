import random
import pygame 
from src.model.card import Card

class Player:
    def __init__(self, name, deck_list):
        self.name = name
        self.library = list(deck_list)  
        self.hand = []            
        self.battlefield = []     
        
        # --- [CORREÇÃO: CEMITÉRIO] ---
        # Definimos graveyard como o padrão para o GraveyardManager e Main.py
        self.graveyard = [] 
        # Mantemos 'grave' como referência para não quebrar códigos antigos se houver
        self.grave = self.graveyard 
        
        self.life = 40            
        
        # --- [ATRIBUTO PARA COMBATE] ---
        self.rect = pygame.Rect(0, 0, 100, 100) 
        
        # --- [ATRIBUTOS DE REGRAS] ---
        self.mana_pool = {
            "white": 0, "blue": 0, "black": 0, 
            "red": 0, "green": 0, "colorless": 0
        }
        self.lands_played = 0
        self.max_lands_per_turn = 1

    def shuffle(self):
        """Embaralha a biblioteca do jogador."""
        random.shuffle(self.library)

    def draw(self, assets_mgr, quantidade, nome_deck):
        """Compra uma ou mais cartas."""
        for _ in range(quantidade):
            self.draw_single_card(assets_mgr, nome_deck)

    def draw_single_card(self, assets_mgr, nome_deck):
        """Remove do topo da library e cria o objeto Card na mão."""
        if self.library:
            nome_carta = self.library.pop(0)
            nova_carta = Card(nome_carta, assets_mgr, nome_deck)
            self.hand.append(nova_carta)
        else:
            print(f"DEBUG: {self.name} tentou comprar de um deck vazio!")

    def untap_all(self):
        """Prepara o jogador para o novo turno (Fase de Desvirar)."""
        for card in self.battlefield:
            # Força o desvirar da carta
            if hasattr(card, 'toggle_tap'):
                card.toggle_tap(force_untap=True)
            else:
                card.tapped = False
                
            # Limpa alvos de ataque e danos marcados (importante para SBA)
            if hasattr(card, 'attack_target'):
                card.attack_target = None
            if hasattr(card, 'damage_marked'):
                card.damage_marked = 0
            
        self.lands_played = 0
        self.empty_mana_pool()
        print(f"DEBUG: {self.name} desvirou tudo e resetou contadores.")
    
    def add_mana(self, color, amount=1):
        if color in self.mana_pool:
            self.mana_pool[color] += amount
            print(f"DEBUG: +{amount} mana {color}. Total: {self.mana_pool[color]}")

    def add_mana_from_land(self, card):
        if card.tapped: return 

        tipos = card.type_line.lower()
        mapa_basicos = {
            "swamp": "black", "island": "blue", "mountain": "red",
            "forest": "green", "plains": "white"
        }
        
        gerou = False
        for busca, cor in mapa_basicos.items():
            if busca in tipos:
                self.add_mana(cor)
                gerou = True
                break
        
        if not gerou and card.is_land:
            self.add_mana("colorless")
            
        card.tapped = True 

    def empty_mana_pool(self):
        for key in self.mana_pool:
            self.mana_pool[key] = 0

    def mulligan(self, assets_mgr, nome_deck, gratis=False):
        nova_quantidade = 7 if gratis else max(0, len(self.hand) - 1)
        for carta in self.hand:
            self.library.append(carta.name)
        
        self.hand = [] 
        self.shuffle() 
        self.draw(assets_mgr, nova_quantidade, nome_deck)

    def change_life(self, amount):
        self.life += amount

    def play_card(self, card, assets_mgr=None, nome_deck=None):
        if card in self.hand:
            self.hand.remove(card)
            self.battlefield.append(card)
            
            # Inicializa atributos de combate na carta ao entrar em jogo
            if not hasattr(card, 'damage_marked'):
                card.damage_marked = 0
            
            from src.controller.effect_engine import EffectEngine
            EffectEngine.process_etb(card, self)
            
            if card.is_land:
                self.lands_played += 1
            
            card.dragging = False

    def organize_hand(self, quad_largura, quad_altura, quad_x, quad_y):
        if not self.hand: return
        num_cartas = len(self.hand)
        overlap = min(80, (quad_largura - 100) // num_cartas) if num_cartas > 0 else 80
        largura_total = (num_cartas - 1) * overlap
        x_inicial = quad_x + (quad_largura // 2) - (largura_total // 2)
        target_y = quad_y + quad_altura - 80 
        
        for i, carta in enumerate(self.hand):
            if not carta.dragging:
                target_x = x_inicial + (i * overlap)
                carta.rect.center = (target_x, target_y)

    def organize_battlefield(self, quad_largura, quad_altura, quad_x, quad_y):
        # Sincroniza o Rect do jogador para cliques e setas
        self.rect.topleft = (quad_x + 10, quad_y + 10)
        self.rect.width = quad_largura - 20
        self.rect.height = quad_altura - 150 # Deixa espaço para a mão

        terrenos = [c for c in self.battlefield if c.is_land]
        permanentes = [c for c in self.battlefield if not c.is_land]

        x_perm = quad_x + 80
        y_perm = quad_y + (quad_altura // 3) 
        
        for carta in permanentes:
            if not carta.dragging:
                carta.rect.center = (x_perm, y_perm)
                x_perm += 110 
                if x_perm > quad_x + quad_largura - 60:
                    x_perm = quad_x + 80
                    y_perm += 120

        pilhas = {}
        for t in terrenos:
            if t.name not in pilhas: pilhas[t.name] = []
            pilhas[t.name].append(t)

        x_terreno = quad_x + 80
        y_terreno = quad_y + (quad_altura // 1.8)
        
        for nome_carta, lista_cartas in pilhas.items():
            for i, carta in enumerate(lista_cartas):
                if not carta.dragging:
                    offset = i * 20 
                    carta.rect.center = (x_terreno, y_terreno + offset)
            x_terreno += 90
            if x_terreno > quad_x + quad_largura - 60:
                x_terreno = quad_x + 80
                y_terreno += 100

    def auto_tap_for_cost(self, custo_card):
        custo_restante = custo_card.copy()
        for cor in ["white", "blue", "black", "red", "green", "colorless"]:
            if cor in custo_restante and cor in self.mana_pool:
                usado = min(custo_restante[cor], self.mana_pool[cor])
                custo_restante[cor] -= usado
                self.mana_pool[cor] -= usado

        terrenos_disponiveis = [c for c in self.battlefield if c.is_land and not c.tapped]
        for terreno in terrenos_disponiveis:
            if sum(v for k, v in custo_restante.items() if k != 'generic') <= 0 and custo_restante.get('generic', 0) <= 0:
                break
            cor_terreno = self.get_land_color(terreno)
            if custo_restante.get(cor_terreno, 0) > 0:
                custo_restante[cor_terreno] -= 1
                terreno.tapped = True
            elif custo_restante.get('generic', 0) > 0:
                custo_restante['generic'] -= 1
                terreno.tapped = True
        return sum(custo_restante.values()) <= 0

    def get_land_color(self, card):
        tl = card.type_line.lower()
        if "forest" in tl: return "green"
        if "island" in tl: return "blue"
        if "mountain" in tl: return "red"
        if "swamp" in tl: return "black"
        if "plains" in tl: return "white"
        return "colorless"

    def get_available_mana_total(self):
        """Soma a mana na pool + terrenos desvirados que podem gerar mana."""
        mana_na_pool = sum(self.mana_pool.values())
        terrenos_prontos = len([c for c in self.battlefield if c.is_land and not c.tapped])
        return mana_na_pool + terrenos_prontos

    def virar_tudo_para_gerar_mana(self):
        """Faz o bot virar todos os terrenos para encher a pool antes de conjurar."""
        terrenos_desvirados = [c for c in self.battlefield if c.is_land and not c.tapped]
        for terreno in terrenos_desvirados:
            self.add_mana_from_land(terreno)
            
            
