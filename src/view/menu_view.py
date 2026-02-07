import pygame

class MenuView:
    def __init__(self, tela, ui_manager, fontes):
        self.tela = tela
        self.ui = ui_manager
        self.fontes = fontes

    def exibir_menu_principal(self, nome_sala, input_ativo, decks, indice, total_jogadores):
        """
        Renderiza o menu principal com suporte à seleção de quantidade de jogadores.
        """
        # --- [TÍTULO] ---
        txt_t = self.fontes['titulo'].render("MTG SIMULATOR", True, (255, 255, 255))
        self.tela.blit(txt_t, (self.tela.get_width()//2 - txt_t.get_width()//2, 50))
        
        # --- [CAMPO DE TEXTO DA SALA] ---
        cor_b = (100, 100, 255) if input_ativo else (150, 150, 150)
        pygame.draw.rect(self.tela, cor_b, self.ui.campo_texto_sala, 2)
        
        txt_s = self.fontes['menu'].render(nome_sala or "Nome da Sala...", True, 
                                           (255,255,255) if nome_sala else (100,100,100))
        self.tela.blit(txt_s, (self.ui.campo_texto_sala.x + 10, self.ui.campo_texto_sala.y + 5))
        
        # --- [SELEÇÃO DE DECK] ---
        # Setas de navegação
        pygame.draw.rect(self.tela, (60, 60, 60), self.ui.btn_deck_esq)
        pygame.draw.rect(self.tela, (60, 60, 60), self.ui.btn_deck_dir)
        
        # Nome do Deck selecionado
        nome_d = decks[indice] if decks else "---"
        txt_deck = self.fontes['menu'].render(nome_d, True, (255, 255, 0))
        self.tela.blit(txt_deck, (self.tela.get_width()//2 - txt_deck.get_width()//2, 325))
        
        # --- [NOVO: SELEÇÃO DE QUANTIDADE DE JOGADORES] ---
        # Texto Informativo
        txt_label = self.fontes['menu'].render("Jogadores:", True, (200, 200, 200))
        self.tela.blit(txt_label, (self.ui.btn_selecao_2.x, self.ui.btn_selecao_2.y - 35))

        opcoes = [
            (2, self.ui.btn_selecao_2), 
            (3, self.ui.btn_selecao_3), 
            (4, self.ui.btn_selecao_4)
        ]

        for num, rect in opcoes:
            # Se o número for o selecionado no MTGGame, desenha em verde, senão cinza
            cor_btn = (50, 150, 50) if total_jogadores == num else (80, 80, 80)
            self.ui.desenhar_botao_arredondado(self.tela, cor_btn, rect, str(num), self.fontes['menu'])
            
            # Adiciona uma borda branca para destacar ainda mais a seleção atual
            if total_jogadores == num:
                pygame.draw.rect(self.tela, (255, 255, 255), rect, 2, border_radius=10)

        # --- [BOTÕES DE AÇÃO] ---
        self.ui.desenhar_botao_arredondado(self.tela, (50, 150, 50), self.ui.btn_criar, "ABRIR SALA", self.fontes['menu'])
        self.ui.desenhar_botao_arredondado(self.tela, (100, 100, 100), self.ui.btn_cadastrar, "CADASTRAR NOVO", self.fontes['menu'])

    def exibir_tela_cadastro(self, nome_deck, input_ativo, arquivo_selecionado):
        """
        Renderiza a interface de cadastro de novos decks.
        """
        self.ui.desenhar_botao_arredondado(self.tela, (80, 80, 80), self.ui.btn_voltar, "Voltar", self.fontes['menu'])
        
        # Input Nome do Deck
        cor_i = (255, 255, 255) if input_ativo else (100, 100, 100)
        pygame.draw.rect(self.tela, cor_i, self.ui.rect_input_nome_deck, 2)
        
        txt_i = self.fontes['menu'].render(nome_deck or "Nome do Deck...", True, (100,100,100))
        self.tela.blit(txt_i, (self.ui.rect_input_nome_deck.x + 5, self.ui.rect_input_nome_deck.y + 5))
        
        # Botão para selecionar o arquivo .txt
        cor_arq = (70, 70, 200) if arquivo_selecionado else (100, 100, 100)
        label_arq = "Arquivo Selecionado" if arquivo_selecionado else "Selecionar .txt"
        self.ui.desenhar_botao_arredondado(self.tela, cor_arq, self.ui.btn_selecionar_arquivo, label_arq, self.fontes['menu'])
        
        # Botão de confirmação (só aparece se houver nome e arquivo)
        if nome_deck and arquivo_selecionado:
            self.ui.desenhar_botao_arredondado(self.tela, (50, 150, 50), self.ui.btn_confirmar_cadastro, "CADASTRAR", self.fontes['menu'])