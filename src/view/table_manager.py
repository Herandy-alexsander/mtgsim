import pygame

class TableManager:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # Define os 4 quadrantes (X, Y, Largura, Altura)
        half_w = screen_width // 2
        half_h = screen_height // 2
        
        # Configuração estilo SpellTable:
        # P0: Superior Esquerdo | P1: Superior Direito
        # P2: Inferior Esquerdo | P3: Inferior Direito (Você)
        self.quadrantes = [
            pygame.Rect(0, 0, half_w, half_h),           # Jogador 1
            pygame.Rect(half_w, 0, half_w, half_h),      # Jogador 2
            pygame.Rect(0, half_h, half_w, half_h),      # Jogador 3
            pygame.Rect(half_w, half_h, half_w, half_h)  # Jogador 4 (Foco Local)
        ]
        
        # Cores para as bordas dos campos
        self.colors = [(200, 0, 0), (0, 200, 0), (0, 0, 200), (200, 200, 0)]

    def draw_layout(self, screen, active_player_index):
        """Desenha as linhas divisórias e destaca o jogador do turno."""
        # Desenha as linhas de divisão
        pygame.draw.line(screen, (50, 50, 50), (self.width // 2, 0), (self.width // 2, self.height), 2)
        pygame.draw.line(screen, (50, 50, 50), (0, self.height // 2), (self.width, self.height // 2), 2)

        # Destaca o jogador que detém o turno (Borda brilhante)
        rect_ativo = self.quadrantes[active_player_index]
        pygame.draw.rect(screen, (255, 255, 255), rect_ativo, 4) # Borda branca para o turno

    def get_player_quadrant(self, index):
        """Retorna o retângulo do quadrante de um jogador específico."""
        return self.quadrantes[index]

    def adjust_card_pos(self, card_rect, player_index):
        """
        Garante que, se uma carta for jogada, ela pertença às 
        coordenadas relativas daquele quadrante.
        """
        quad = self.quadrantes[player_index]
        # Aqui podemos adicionar lógica para impedir que cartas "fujam" do quadrante
        pass
