import pygame
from tkinter import filedialog

class InputHandler:
    def __init__(self, game):
        """
        Gerencia todas as entradas do usuário (Mouse e Teclado).
        Recebe a instância principal 'game' para modificar estados e chamar métodos.
        """
        self.game = game

    def processar_eventos(self, eventos):
        """
        Distribui os eventos do Pygame para os tratadores específicos de cada estado.
        """
        for evento in eventos:
            # Fecha o jogo se o usuário clicar no X da janela
            if evento.type == pygame.QUIT:
                self.game.executando = False
            
            # Direciona o evento baseado no estado atual da tela
            if self.game.estado_atual == "menu":
                self.handle_menu(evento)
            elif self.game.estado_atual == "cadastro":
                self.handle_cadastro(evento)
            elif self.game.estado_atual == "jogo":
                self.handle_jogo(evento)

    def handle_menu(self, evento):
        """
        Trata cliques e digitação na tela de Menu Principal.
        """
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # 1. FOCO NO CAMPO DE TEXTO (Nome da Sala)
            self.game.input_ativo_sala = self.game.ui.campo_texto_sala.collidepoint(evento.pos)
            
            # 2. SELEÇÃO DE DECK (Navegação pelas setas)
            if self.game.ui.btn_deck_esq.collidepoint(evento.pos):
                self.game.indice_deck_selecionado = (self.game.indice_deck_selecionado - 1) % len(self.game.decks_disponiveis)
            elif self.game.ui.btn_deck_dir.collidepoint(evento.pos):
                self.game.indice_deck_selecionado = (self.game.indice_deck_selecionado + 1) % len(self.game.decks_disponiveis)
            
            # 3. NOVO: SELEÇÃO DA QUANTIDADE DE JOGADORES (2, 3 ou 4)
            if self.game.ui.btn_selecao_2.collidepoint(evento.pos):
                self.game.total_jogadores_selecionado = 2
                print("Modo Selecionado: X1 (2 Jogadores)")
                
            elif self.game.ui.btn_selecao_3.collidepoint(evento.pos):
                self.game.total_jogadores_selecionado = 3
                print("Modo Selecionado: 3 Players")
                
            elif self.game.ui.btn_selecao_4.collidepoint(evento.pos):
                self.game.total_jogadores_selecionado = 4
                print("Modo Selecionado: Commander (4 Jogadores)")

            # 4. BOTÕES DE AÇÃO PRINCIPAIS
            elif self.game.ui.btn_cadastrar.collidepoint(evento.pos):
                self.game.estado_atual = "cadastro"
                
            elif self.game.ui.btn_criar.collidepoint(evento.pos):
                # Antes de iniciar, ajustamos o layout da mesa (TableManager)
                self.game.table_mgr.ajustar_layout(self.game.total_jogadores_selecionado)
                # Inicia o jogo com os decks e bots configurados
                self.game.iniciar_jogo()

        # Tratamento de digitação para o nome da sala
        if evento.type == pygame.KEYDOWN and self.game.input_ativo_sala:
            if evento.key == pygame.K_BACKSPACE:
                self.game.nome_sala = self.game.nome_sala[:-1]
            else:
                self.game.nome_sala += evento.unicode

    def handle_cadastro(self, evento):
        """
        Trata o processo de importação de novos arquivos de deck .txt.
        """
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.game.ui.btn_voltar.collidepoint(evento.pos):
                self.game.estado_atual = "menu"
            
            # Foco no input de nome do novo deck
            self.game.input_ativo_deck = self.game.ui.rect_input_nome_deck.collidepoint(evento.pos)
            
            # Abre explorador de arquivos do Windows (Tkinter)
            if self.game.ui.btn_selecionar_arquivo.collidepoint(evento.pos):
                c = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
                if c: self.game.caminho_arquivo_selecionado = c
            
            # Confirmação do cadastro
            if self.game.ui.btn_confirmar_cadastro.collidepoint(evento.pos) and \
               self.game.input_nome_deck and self.game.caminho_arquivo_selecionado:
                
                # Carrega e baixa as imagens do Scryfall via AssetsManager
                from src.model.deck_loader import DeckLoader
                lista = DeckLoader.load_from_txt(self.game.caminho_arquivo_selecionado)
                self.game.assets_mgr.baixar_deck_completo(self.game.input_nome_deck, lista, self.game.tela, self.game.fontes['menu'])
                
                # Reseta campos e volta ao menu
                self.game.input_nome_deck, self.game.caminho_arquivo_selecionado = "", ""
                self.game.atualizar_lista_decks()
                self.game.estado_atual = "menu"

        if evento.type == pygame.KEYDOWN and self.game.input_ativo_deck:
            if evento.key == pygame.K_BACKSPACE:
                self.game.input_nome_deck = self.game.input_nome_deck[:-1]
            else:
                self.game.input_nome_deck += evento.unicode

    def handle_jogo(self, evento):
        """
        Trata a interação com cartas e botões durante a partida.
        """
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Lógica de Mulligan
            if self.game.turn_mgr.em_mulligan:
                if self.game.ui.btn_manter_mao.collidepoint(evento.pos):
                    self.game.turn_mgr.finalizar_mulligan()
                elif self.game.ui.btn_fazer_mulligan.collidepoint(evento.pos):
                    # Executa o mulligan e registra no contador
                    nome_deck_atual = self.game.decks_disponiveis[self.game.indice_deck_selecionado]
                    self.game.jogador_local.mulligan(self.game.assets_mgr, 
                                                     nome_deck_atual, 
                                                     (self.game.turn_mgr.quantidade_mulligans == 0))
                    self.game.turn_mgr.registrar_mulligan()
            
            # Botão de passar fase/turno
            elif self.game.ui.btn_proxima_fase.collidepoint(evento.pos):
                nome_deck_atual = self.game.decks_disponiveis[self.game.indice_deck_selecionado]
                self.game.turn_mgr.proxima_fase(self.game.jogador_local, 
                                                self.game.assets_mgr, 
                                                nome_deck_atual)
        
        # Lógica de Arrastar Cartas (Drag and Drop)
        if evento.type == pygame.MOUSEBUTTONDOWN and not self.game.turn_mgr.em_mulligan:
            for carta in reversed(self.game.jogador_local.hand + self.game.jogador_local.battlefield):
                if carta.rect.collidepoint(evento.pos):
                    carta.dragging = True
                    break

        if evento.type == pygame.MOUSEBUTTONUP:
            for carta in self.game.jogador_local.hand + self.game.jogador_local.battlefield:
                if carta.dragging:
                    carta.dragging = False
                    # Se soltar a carta no campo, tenta jogá-la usando o RulesEngine
                    # (Lógica de play_card pode ser expandida aqui)