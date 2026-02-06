import pygame
import re  # Essencial para processar os custos de mana

# Configurações de tamanho para layout de 4 jogadores
CARD_WIDTH = 80
CARD_HEIGHT = 112
ZOOM_SCALE = 3.0

class Card:
    def __init__(self, name, assets_mgr, deck_name=None):
        self.name = name
        self.tapped = False
        
        # --- ESTADOS DE INTERAÇÃO (Essenciais para o main.py) ---
        self.dragging = False
        self.is_hovered = False
        self.host_card = None  
        
        # --- ATRIBUTOS DE REGRAS (Essenciais para o RulesEngine) ---
        self.is_land = False
        self.is_instant = False
        self.has_flash = False
        self.type_line = ""
        self.oracle_text = ""
        self.mana_cost = ""
        self.mana_value = 0  # <--- NOVO: Valor numérico (CMC) para cálculos
        
        # Carrega a imagem original do gerenciador
        self.original_image = assets_mgr.get_card_image(name, deck_name)
        
        # --- PROCESSAMENTO DE DADOS (JSON) ---
        if assets_mgr.card_data_cache and name in assets_mgr.card_data_cache:
            data = assets_mgr.card_data_cache[name]
            self.type_line = data.get('type_line', '')
            self.oracle_text = data.get('oracle_text', '')
            self.mana_cost = data.get('mana_cost', '')
            
            self.is_land = "Land" in self.type_line
            self.is_instant = "Instant" in self.type_line
            self.has_flash = "Flash" in (self.oracle_text or "")
            
            # Calcula o valor numérico do custo de mana
            self.mana_value = self._calculate_mana_value(self.mana_cost)
        
        # Fallback para Terrenos Básicos (caso o JSON falhe)
        terrenos_basicos = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]
        if not self.type_line:
            if any(t in self.name for t in terrenos_basicos):
                self.is_land = True
                self.type_line = "Basic Land"
                self.mana_value = 0

        # --- CONFIGURAÇÃO VISUAL ---
        self.image_small = pygame.transform.smoothscale(self.original_image, (CARD_WIDTH, CARD_HEIGHT))
        
        # Criamos a imagem de Zoom
        w_zoom, h_zoom = int(CARD_WIDTH * ZOOM_SCALE), int(CARD_HEIGHT * ZOOM_SCALE)
        self.image_zoom = pygame.transform.smoothscale(self.original_image, (w_zoom, h_zoom))
        
        self.image = self.image_small
        self.rect = self.image.get_rect()

    def _calculate_mana_value(self, cost_str):
        """Converte strings como {1}{W}{B} em um número inteiro (ex: 3)."""
        if not cost_str:
            return 0
        # Encontra todos os valores dentro das chaves {}
        symbols = re.findall(r'\{(.*?)\}', cost_str)
        total = 0
        for s in symbols:
            if s.isdigit():
                total += int(s)
            elif s in ['W', 'U', 'B', 'R', 'G', 'C', 'S']:
                total += 1
            elif '/' in s: # Para custos híbridos como {W/B}
                total += 1
        return total

    def toggle_tap(self, force_untap=False):
        self.tapped = False if force_untap else not self.tapped

    def update_position(self, mouse_pos):
        if self.dragging:
            self.rect.center = mouse_pos

    def draw(self, surface):
        if self.is_hovered:
            img_to_draw = self.image_zoom
            rect_to_draw = img_to_draw.get_rect(center=self.rect.center)
            rect_to_draw.clamp_ip(surface.get_rect())
        else:
            img_to_draw = self.image_small
            rect_to_draw = self.rect

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
