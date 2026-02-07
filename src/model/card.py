import pygame
import re  # Essencial para processar os custos de mana (Regex)

# --- [CONFIGURAÇÕES VISUAIS] ---
CARD_WIDTH = 80
CARD_HEIGHT = 112
ZOOM_SCALE = 3.0

class Card:
    def __init__(self, name, assets_mgr, deck_name=None):
        """
        Representa uma carta individual no jogo.
        Lê dados técnicos do JSON para permitir lógica de combate e regras.
        """
        # 1. ATRIBUTOS BÁSICOS
        self.name = name
        self.tapped = False
        self.is_hovered = False
        self.dragging = False
        self.host_card = None  # Referência para carta onde esta está anexada (ex: Aura)

        # 2. ATRIBUTOS DE REGRAS (Lógica de Jogo)
        self.type_line = ""
        self.oracle_text = ""
        self.mana_cost = ""
        self.mana_value = 0     # CMC (Custo de Mana Convertido)
        self.is_land = False
        self.is_instant = False
        self.has_flash = False
        self.is_creature = False
        self.power = 0
        self.toughness = 0

        # 3. CARREGAMENTO DE IMAGEM ORIGINAL
        # Obtém a imagem bruta do AssetsManager
        self.original_image = assets_mgr.get_card_image(name, deck_name)

        # 4. PROCESSAMENTO DE DADOS TÉCNICOS (JSON)
        # Verifica se as informações da carta existem no cache carregado
        if assets_mgr.card_data_cache and name in assets_mgr.card_data_cache:
            data = assets_mgr.card_data_cache[name]
            
            # Extrai textos básicos
            self.type_line = data.get('type_line', '')
            self.oracle_text = data.get('oracle_text', '')
            self.mana_cost = data.get('mana_cost', '')
            
            # Define tipos para o RulesEngine
            self.is_land = "Land" in self.type_line
            self.is_instant = "Instant" in self.type_line
            self.is_creature = "Creature" in self.type_line
            self.has_flash = "Flash" in (self.oracle_text or "")
            
            # Processa Poder e Resistência se for criatura
            if self.is_creature and 'power' in data:
                # Converte para int para garantir que cálculos matemáticos funcionem
                try:
                    self.power = int(data.get('power', 0))
                    self.toughness = int(data.get('toughness', 0))
                except ValueError:
                    self.power = 0 # Fallback para casos de '*' ou 'X'
                    self.toughness = 0

            # Calcula o valor numérico (CMC) do custo de mana
            self.mana_value = self._calculate_mana_value(self.mana_cost)
        
        # 5. FALLBACK PARA TERRENOS BÁSICOS
        # Se o JSON falhar, identifica terrenos pelo nome para não quebrar o jogo
        terrenos_basicos = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]
        if not self.type_line:
            if any(t in self.name for t in terrenos_basicos):
                self.is_land = True
                self.type_line = "Basic Land"
                self.mana_value = 0

        # 6. CONFIGURAÇÃO VISUAL (Sprites)
        # Imagem pequena para a mesa
        self.image_small = pygame.transform.smoothscale(self.original_image, (CARD_WIDTH, CARD_HEIGHT))
        
        # Imagem ampliada para quando passar o mouse (Hover)
        w_zoom, h_zoom = int(CARD_WIDTH * ZOOM_SCALE), int(CARD_HEIGHT * ZOOM_SCALE)
        self.image_zoom = pygame.transform.smoothscale(self.original_image, (w_zoom, h_zoom))
        
        self.image = self.image_small
        self.rect = self.image.get_rect()

    def _calculate_mana_value(self, cost_str):
        """
        Usa Expressões Regulares (Regex) para converter {1}{W}{B} em 3.
        """
        if not cost_str:
            return 0
        # Pega tudo que estiver entre chaves
        symbols = re.findall(r'\{(.*?)\}', cost_str)
        total = 0
        for s in symbols:
            if s.isdigit():
                total += int(s) # Se for número (ex: {3}), soma o valor
            elif s in ['W', 'U', 'B', 'R', 'G', 'C', 'S'] or '/' in s:
                total += 1 # Se for símbolo de cor ou híbrido, soma 1
        return total

    def toggle_tap(self, force_untap=False):
        """Vira ou desvira a carta."""
        self.tapped = False if force_untap else not self.tapped

    def update_position(self, mouse_pos):
        """Atualiza a posição do Rect durante o arraste."""
        if self.dragging:
            self.rect.center = mouse_pos

    def draw(self, surface):
        """
        Desenha a carta na tela, tratando estados de Zoom e Virada.
        """
        # Define qual imagem e qual retângulo usar (Zoom ou Normal)
        if self.is_hovered:
            img_to_draw = self.image_zoom
            rect_to_draw = img_to_draw.get_rect(center=self.rect.center)
            # Impede que o zoom saia pelas bordas da tela
            rect_to_draw.clamp_ip(surface.get_rect())
        else:
            img_to_draw = self.image_small
            rect_to_draw = self.rect

        # Trata a rotação se a carta estiver virada (Tap)
        if self.tapped:
            img_rot = pygame.transform.rotate(img_to_draw, -90)
            rect_rot = img_rot.get_rect(center=rect_to_draw.center)
            surface.blit(img_rot, rect_rot)
            if self.is_hovered:
                pygame.draw.rect(surface, (255, 255, 0), rect_rot, 3) # Borda de destaque
        else:
            surface.blit(img_to_draw, rect_to_draw)
            if self.is_hovered:
                pygame.draw.rect(surface, (255, 255, 0), rect_to_draw, 3) # Borda de destaque