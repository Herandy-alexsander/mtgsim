import pygame

class UIComponents:
    def __init__(self, largura, altura):
        """
        Gerencia as coordenadas e dimensões de todos os elementos da interface.
        Organizado por 'camadas' verticais para evitar qualquer sobreposição.
        """
        self.LARGURA = largura
        self.ALTURA = altura
        centro_x = largura // 2
        
        # --- [DEFINIÇÃO DE ALTURAS (Y) - SISTEMA ANTI-SOBREPOSIÇÃO] ---
        y_titulo = 80
        y_input_sala = 180
        y_label_deck = 260        # Texto 'Selecionar Deck'
        y_deck_navegacao = 290    # Nome do Deck e Setas
        y_label_jogadores = 360   # Texto 'Quantidade de Jogadores'
        y_botoes_jogadores = 390  # Botões 2, 3, 4
        y_botao_abrir = 480       # Botão ABRIR SALA
        y_botao_cadastrar = 550   # Botão CADASTRAR NOVO

        # --- [COMPONENTES DO MENU PRINCIPAL] ---
        # Campo de Texto da Sala
        self.campo_texto_sala = pygame.Rect(centro_x - 150, y_input_sala, 300, 40)
        
        # Seleção de Deck
        self.btn_deck_esq = pygame.Rect(centro_x - 180, y_deck_navegacao, 40, 40)
        self.btn_deck_dir = pygame.Rect(centro_x + 140, y_deck_navegacao, 40, 40)
        
        # Seleção de Jogadores (Botões Lado a Lado)
        largura_btn_jog = 80
        self.btn_selecao_2 = pygame.Rect(centro_x - 135, y_botoes_jogadores, largura_btn_jog, 40)
        self.btn_selecao_3 = pygame.Rect(centro_x - 40, y_botoes_jogadores, largura_btn_jog, 40)
        self.btn_selecao_4 = pygame.Rect(centro_x + 55, y_botoes_jogadores, largura_btn_jog, 40)
        
        # Botões de Ação
        self.btn_criar = pygame.Rect(centro_x - 150, y_botao_abrir, 300, 50)
        self.btn_cadastrar = pygame.Rect(centro_x - 150, y_botao_cadastrar, 300, 50)
        
        # --- [COMPONENTES DE CADASTRO] ---
        self.btn_voltar = pygame.Rect(20, 20, 100, 40)
        self.rect_input_nome_deck = pygame.Rect(centro_x - 150, 200, 300, 40)
        self.btn_selecionar_arquivo = pygame.Rect(centro_x - 150, 300, 300, 50)
        self.btn_confirmar_cadastro = pygame.Rect(centro_x - 150, 450, 300, 50)
        
        # --- [COMPONENTES DE JOGO] ---
        # Botão Central de Fase
        self.btn_proxima_fase = pygame.Rect(centro_x - 90, altura // 2 - 30, 180, 60)
        
        # Botões de Mulligan (Abaixo do botão de fase para não sobrepor)
        self.btn_manter_mao = pygame.Rect(centro_x - 210, altura // 2 + 80, 200, 60)
        self.btn_fazer_mulligan = pygame.Rect(centro_x + 10, altura // 2 + 80, 200, 60)

    def atualizar_resolucao(self, nova_largura, nova_altura):
        """Atualiza o layout caso a janela seja redimensionada."""
        self.__init__(nova_largura, nova_altura)

    @staticmethod
    def desenhar_botao_arredondado(surface, cor, rect, texto, fonte, cor_texto=(255, 255, 255), raio=10):
        """Helper para desenhar botões com cantos arredondados e texto centralizado."""
        # Borda externa opcional ou sombra
        pygame.draw.rect(surface, (30, 30, 30), rect.move(0, 2), border_radius=raio) # Sombra
        
        # Corpo do botão
        pygame.draw.rect(surface, cor, rect, border_radius=raio)
        
        # Renderização do texto
        img_texto = fonte.render(texto, True, cor_texto)
        pos_texto = (rect.centerx - img_texto.get_width() // 2, 
                     rect.centery - img_texto.get_height() // 2)
        surface.blit(img_texto, pos_texto)