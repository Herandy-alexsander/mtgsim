import random
from src.model.card import Card

class Player:
    def __init__(self, name, deck_list):
        self.name = name
        self.library = list(deck_list)  # Cria uma cópia da lista para não afetar o original
        self.hand = []            # Lista de objetos Card
        self.battlefield = []     # Cartas em jogo
        self.grave = []           # Cemitério
        self.life = 40            # Vida padrão Commander (ajuste para 20 se for padrão)
        
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
        # 1. Desvirar permanentes
        for card in self.battlefield:
            card.toggle_tap(force_untap=True)
            
        # 2. Reseta contadores de restrição
        self.lands_played = 0
        
        # 3. Limpa a reserva de mana
        self.empty_mana_pool()
        print(f"DEBUG: {self.name} desvirou tudo e resetou contadores.")
    
    def add_mana(self, color, amount=1):
        """Adiciona mana à reserva."""
        if color in self.mana_pool:
            self.mana_pool[color] += amount
            print(f"DEBUG: +{amount} mana {color}. Total: {self.mana_pool[color]}")

    def add_mana_from_land(self, card):
        """Gera mana baseada nos tipos do terreno, apenas se não estiver virado."""
        if card.tapped: 
            return # Trava de segurança

        tipos = card.type_line.lower()
        mapa_basicos = {
            "swamp": "black",
            "island": "blue",
            "mountain": "red",
            "forest": "green",
            "plains": "white"
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
        print(f"DEBUG: {card.name} virado para gerar mana.")

    def empty_mana_pool(self):
        """Esvazia a reserva de mana."""
        for key in self.mana_pool:
            self.mana_pool[key] = 0

    def mulligan(self, assets_mgr, nome_deck, gratis=False):
        """Reinicia a mão seguindo a regra de mulligan."""
        nova_quantidade = 7 if gratis else max(0, len(self.hand) - 1)
        
        # Devolve a mão para o deck
        for carta in self.hand:
            self.library.append(carta.name)
        
        self.hand = [] 
        self.shuffle() 
        self.draw(assets_mgr, nova_quantidade, nome_deck)

    def change_life(self, amount):
        self.life += amount

    def play_card(self, card, assets_mgr=None, nome_deck=None):
        """Move a carta da mão para o campo e aplica regras de entrada."""
        if card in self.hand:
            self.hand.remove(card)
            self.battlefield.append(card)
            
            # --- DEBUG DE TEXTO ---
            texto_lido = (card.oracle_text or "").lower()
            
            # Chama o motor de efeitos (Importação local para evitar ciclo)
            from src.controller.effect_engine import EffectEngine
            EffectEngine.process_etb(card, self)
            
            if card.is_land:
                self.lands_played += 1
            
            card.dragging = False

    def organize_hand(self, quad_largura, quad_altura, quad_x, quad_y):
        """Organiza a mão em leque, respeitando a posição do jogador (quadrante)."""
        if not self.hand: return
        
        num_cartas = len(self.hand)
        # Ajusta sobreposição se tiver muitas cartas, mas mantém um máximo de 80px
        overlap = min(80, (quad_largura - 100) // num_cartas) if num_cartas > 0 else 80
        largura_total = (num_cartas - 1) * overlap
        
        # Centraliza baseado na posição X do quadrante + metade da largura do quadrante
        x_inicial = quad_x + (quad_largura // 2) - (largura_total // 2)
        # Fixa no fundo do quadrante
        target_y = quad_y + quad_altura - 80 
        
        for i, carta in enumerate(self.hand):
            if not carta.dragging:
                target_x = x_inicial + (i * overlap)
                carta.rect.center = (target_x, target_y)

    def organize_battlefield(self, quad_largura, quad_altura, quad_x, quad_y):
        """Organiza o campo dentro do quadrante específico do jogador."""
        terrenos = [c for c in self.battlefield if c.is_land]
        permanentes = [c for c in self.battlefield if not c.is_land]

        # Configurações de layout relativas ao quadrante (quad_x, quad_y)
        # Área de Permanentes (parte superior do quadrante)
        x_perm = quad_x + 80
        y_perm = quad_y + (quad_altura // 3) 
        
        for carta in permanentes:
            if not carta.dragging:
                carta.rect.center = (x_perm, y_perm)
                x_perm += 110 # Espaçamento lateral
                # Quebra de linha se passar da largura do quadrante
                if x_perm > quad_x + quad_largura - 60:
                    x_perm = quad_x + 80
                    y_perm += 120

        # Área de Terrenos (parte inferior do quadrante, acima da mão)
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
            # Quebra de linha para terrenos
            if x_terreno > quad_x + quad_largura - 60:
                x_terreno = quad_x + 80
                y_terreno += 100

    def auto_tap_for_cost(self, custo_card):
        """
        Tenta virar terrenos automaticamente para pagar um custo.
        """
        custo_restante = custo_card.copy()
        
        # 1. Usa o que já está na mana_pool
        for cor in ["white", "blue", "black", "red", "green", "colorless"]:
            if cor in custo_restante and cor in self.mana_pool:
                usado = min(custo_restante[cor], self.mana_pool[cor])
                custo_restante[cor] -= usado
                self.mana_pool[cor] -= usado

        # 2. Vira terrenos para o que falta
        terrenos_disponiveis = [c for c in self.battlefield if c.is_land and not c.tapped]
        
        for terreno in terrenos_disponiveis:
            # Se já pagou tudo (inclusive genérico), para.
            if sum(v for k, v in custo_restante.items() if k != 'generic') <= 0 and custo_restante.get('generic', 0) <= 0:
                break
                
            cor_terreno = self.get_land_color(terreno)
            
            # Paga cor específica
            if custo_restante.get(cor_terreno, 0) > 0:
                custo_restante[cor_terreno] -= 1
                terreno.tapped = True
            # Se não precisa da cor, tenta pagar genérico
            elif custo_restante.get('generic', 0) > 0:
                custo_restante['generic'] -= 1
                terreno.tapped = True

        return sum(custo_restante.values()) <= 0

    def get_land_color(self, card):
        """Retorna a cor que o terreno produz baseado na type_line."""
        tl = card.type_line.lower()
        if "forest" in tl: return "green"
        if "island" in tl: return "blue"
        if "mountain" in tl: return "red"
        if "swamp" in tl: return "black"
        if "plains" in tl: return "white"
        return "colorless"
