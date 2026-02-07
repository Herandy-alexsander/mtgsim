import pygame

class TableManager:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.quadrantes = []
        # Inicializa com 4 jogadores por padrão, mas será atualizado pelo InputHandler
        self.ajustar_layout(4)

    def ajustar_layout(self, num_jogadores):
        """
        Recalcula as áreas de jogo baseadas na quantidade de participantes (2, 3 ou 4).
        Isso garante que cada processador (Bot ou Humano) tenha seu espaço correto.
        """
        self.quadrantes = []
        half_w = self.width // 2
        half_h = self.height // 2

        if num_jogadores == 2:
            # Layout X1: Dividido horizontalmente (Metade superior e metade inferior)
            self.quadrantes.append(pygame.Rect(0, half_h, self.width, half_h)) # P0: Você (Embaixo)
            self.quadrantes.append(pygame.Rect(0, 0, self.width, half_h))      # P1: Oponente (Cima)

        elif num_jogadores == 3:
            # Layout 3 Jogadores: Você embaixo (tela cheia), dois bots em cima divididos
            self.quadrantes.append(pygame.Rect(0, half_h, self.width, half_h)) # P0: Você
            self.quadrantes.append(pygame.Rect(0, 0, half_w, half_h))          # P1: Bot 1
            self.quadrantes.append(pygame.Rect(half_w, 0, half_w, half_h))     # P2: Bot 2

        else: # Padrão 4 Jogadores (Estilo da sua imagem)
            # Organização em cruz: 
            # Inferior Esquerda (Você) | Superior Esquerda (Bot 1)
            # Superior Direita (Bot 2) | Inferior Direita (Bot 3)
            self.quadrantes.append(pygame.Rect(0, half_h, half_w, half_h))     # P0: Você
            self.quadrantes.append(pygame.Rect(0, 0, half_w, half_h))          # P1: Bot 1
            self.quadrantes.append(pygame.Rect(half_w, 0, half_w, half_h))     # P2: Bot 2
            self.quadrantes.append(pygame.Rect(half_w, half_h, half_w, half_h))# P3: Bot 3

    def draw_layout(self, screen, active_player_index):
        """Desenha as linhas divisórias e destaca o jogador do turno."""
        # Desenha as bordas de cada quadrante ativo para separar os cenários
        for i, quad in enumerate(self.quadrantes):
            # Desenha uma linha divisória discreta
            pygame.draw.rect(screen, (50, 50, 50), quad, 2)
            
            # Destaca o jogador que detém o turno (Borda branca brilhante)
            if i == active_player_index:
                pygame.draw.rect(screen, (255, 255, 255), quad, 4)

    def get_player_quadrant(self, index):
        """Retorna o retângulo do quadrante de um jogador específico."""
        if index < len(self.quadrantes):
            return self.quadrantes[index]
        return self.quadrantes[0] # Fallback de segurança

    def adjust_card_pos(self, card_rect, player_index):
        """
        Garante que as cartas fiquem presas dentro do limite do quadrante do seu dono.
        """
        quad = self.get_player_quadrant(player_index)
        card_rect.clamp_ip(quad)