import pygame

class InfoBox:
    def __init__(self):
        # Fonte padrão do sistema
        self.title_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 14)
        self.bg_color = (30, 30, 30, 230) # Cinza escuro semi-transparente
        self.text_color = (255, 255, 255) # Branco
        self.border_color = (100, 100, 255) # Azul claro

    def draw(self, surface, card, mouse_pos):
        """Desenha a caixa de informações ao lado do mouse."""
        if not card: return

        # 1. Preparar o Conteúdo
        linhas = []
        
        # Nome
        linhas.append((card.name, self.title_font))
        
        # Tipo e Custo
        custo_txt = card.mana_cost if card.mana_cost else ""
        linhas.append((f"{card.type_line}   {custo_txt}", self.text_font))
        
        # Poder / Resistência (Apenas se for criatura)
        if card.is_creature:
            pt_text = f"P/T: {card.power} / {card.toughness}"
            linhas.append((pt_text, self.title_font)) # Destaque

        # Separador
        linhas.append(("--- Texto de Regras ---", self.text_font))

        # Texto de Regras (Quebra de linha manual simples)
        if card.oracle_text:
            palavras = card.oracle_text.split(' ')
            linha_atual = ""
            for palavra in palavras:
                if len(linha_atual) + len(palavra) > 40: # Limite de caracteres por linha
                    linhas.append((linha_atual, self.text_font))
                    linha_atual = palavra + " "
                else:
                    linha_atual += palavra + " "
            linhas.append((linha_atual, self.text_font))

        # 2. Calcular Tamanho da Caixa
        largura_box = 300
        altura_box = 20 + (len(linhas) * 20)
        
        # 3. Definir Posição (Evita sair da tela)
        x, y = mouse_pos
        x += 120 # Desloca para a direita do mouse (assumindo zoom ali)
        
        # Se estiver muito à direita da tela, joga para a esquerda
        if x + largura_box > surface.get_width():
            x = mouse_pos[0] - largura_box - 120
            
        y = min(y, surface.get_height() - altura_box) # Não deixa sair por baixo

        rect_box = pygame.Rect(x, y, largura_box, altura_box)

        # 4. Desenhar Fundo e Borda
        s = pygame.Surface((largura_box, altura_box), pygame.SRCALPHA)
        s.fill(self.bg_color)
        surface.blit(s, (x, y))
        pygame.draw.rect(surface, self.border_color, rect_box, 2)

        # 5. Renderizar Texto
        current_y = y + 10
        for texto, fonte in linhas:
            surf_texto = fonte.render(texto, True, self.text_color)
            surface.blit(surf_texto, (x + 10, current_y))
            current_y += 20
