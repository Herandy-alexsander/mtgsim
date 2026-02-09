import pygame
import re

# Configurações de tamanho
CARD_WIDTH = 80
CARD_HEIGHT = 112
ZOOM_SCALE = 3.0

class Card:
    def __init__(self, name, assets_mgr, deck_name=None):
        self.name = name
        self.tapped = False
        
        # --- ESTADOS DE INTERAÇÃO ---
        self.dragging = False
        self.is_hovered = False
        self.host_card = None  
        
        # --- ATRIBUTOS DE REGRAS ---
        self.is_land = False
        self.is_instant = False
        self.has_flash = False
        self.type_line = ""
        self.oracle_text = ""
        self.mana_cost = ""
        self.mana_value = 0  
        
        # --- ATRIBUTOS DE COMBATE ---
        self.power = 0
        self.toughness = 0
        self.is_creature = False
        self.damage_marked = 0
        self.attack_target = None

        # Carrega a imagem original
        self.original_image = assets_mgr.get_card_image(name, deck_name)
        
        # --- PROCESSAMENTO DE DADOS (JSON) ---
        if assets_mgr.card_data_cache and name in assets_mgr.card_data_cache:
            data = assets_mgr.card_data_cache[name]
            self.type_line = data.get('type_line', '')
            self.oracle_text = data.get('oracle_text', '')
            self.mana_cost = data.get('mana_cost', '')
            
            self.is_land = "Land" in self.type_line
            self.is_creature = "Creature" in self.type_line
            self.is_instant = "Instant" in self.type_line
            self.has_flash = "Flash" in (self.oracle_text or "")
            
            if self.is_creature:
                # Ajuste crítico: se for '*' ou variável, colocamos 1 para não morrer no SBA
                # O motor de jogo depois deve aplicar os efeitos de buffs.
                self.power = self._parse_pt(data.get('power', '0'))
                self.toughness = self._parse_pt(data.get('toughness', '0'))
            
            self.mana_value = self._calculate_mana_value(self.mana_cost)
        
        # Fallback para Terrenos
        terrenos_basicos = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]
        if not self.type_line:
            if any(t in self.name for t in terrenos_basicos):
                self.is_land = True
                self.type_line = "Basic Land"
                self.mana_value = 0

        # --- CONFIGURAÇÃO VISUAL ---
        self.image_small = pygame.transform.smoothscale(self.original_image, (CARD_WIDTH, CARD_HEIGHT))
        w_zoom, h_zoom = int(CARD_WIDTH * ZOOM_SCALE), int(CARD_HEIGHT * ZOOM_SCALE)
        self.image_zoom = pygame.transform.smoothscale(self.original_image, (w_zoom, h_zoom))
        self.image = self.image_small
        self.rect = self.image.get_rect()

    def _parse_pt(self, value):
        """Converte strings de P/T em inteiros. Evita que '*' mate a criatura."""
        if not value: return 0
        val_str = str(value).strip()
        
        # Se for uma carta com P/T variável (ex: *), definimos como 1 temporariamente
        # para que ela não morra para o SBA antes do motor processar o efeito dela.
        if '*' in val_str:
            return 1 
            
        try:
            clean_val = re.sub(r'[^0-9-]', '', val_str)
            return int(clean_val) if clean_val else 0
        except ValueError:
            return 0

    def get_mana_dict(self):
        """Retorna o custo de mana em formato de dicionário para o AIEngine e Player."""
        custo_dict = {"white": 0, "blue": 0, "black": 0, "red": 0, "green": 0, "generic": 0}
        if not self.mana_cost:
            return custo_dict
            
        symbols = re.findall(r'\{(.*?)\}', self.mana_cost)
        for s in symbols:
            s = s.upper()
            if s.isdigit(): custo_dict["generic"] += int(s)
            elif s == 'W': custo_dict["white"] += 1
            elif s == 'U': custo_dict["blue"] += 1
            elif s == 'B': custo_dict["black"] += 1
            elif s == 'R': custo_dict["red"] += 1
            elif s == 'G': custo_dict["green"] += 1
        return custo_dict

    def _calculate_mana_value(self, cost_str):
        if not cost_str: return 0
        symbols = re.findall(r'\{(.*?)\}', cost_str)
        total = 0
        for s in symbols:
            if s.isdigit(): total += int(s)
            else: total += 1
        return total

    def toggle_tap(self, force_untap=False):
        self.tapped = False if force_untap else not self.tapped

    def update_position(self, mouse_pos):
        if self.dragging:
            self.rect.center = mouse_pos

    def draw(self, surface):
        img_to_draw = self.image_zoom if self.is_hovered else self.image_small
        rect_to_draw = img_to_draw.get_rect(center=self.rect.center) if self.is_hovered else self.rect
        
        if self.is_hovered:
            rect_to_draw.clamp_ip(surface.get_rect())

        if self.tapped:
            img_rot = pygame.transform.rotate(img_to_draw, -90)
            rect_rot = img_rot.get_rect(center=rect_to_draw.center)
            surface.blit(img_rot, rect_rot)
            if self.is_hovered:
                pygame.draw.rect(surface, (255, 255, 0), rect_rot, 3)
        else:
            surface.blit(img_to_draw, rect_to_draw)
            if self.is_hovered:
                pygame.draw.rect(surface, (255, 255, 0), rect_to_draw, 3)
