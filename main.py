import os
import sys
import pygame
import tkinter as tk
import random 
from tkinter import filedialog

# --- [CONFIGURAÇÃO DE CAMINHOS E IMPORTS] ---
diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
if diretorio_raiz not in sys.path:
    sys.path.insert(0, diretorio_raiz)

try:
    from src.view.assets_mgr import AssetsManager
    from src.view.table_manager import TableManager 
    from src.view.ui_components import UIComponents  
    from src.view.menu_view import MenuView
    from src.model.deck_loader import DeckLoader
    from src.model.player import Player
    from src.model.turn_manager import TurnManager 
    from src.controller.rules_engine import RulesEngine
    from src.controller.ai_engine import AIEngine
    from src.controller.input_handler import InputHandler
    from src.controller.combat_manager import CombatManager
except Exception as e:
    print(f"Erro ao importar módulos internos: {e}")
    sys.exit(1)

class MTGGame:
    def __init__(self):
        pygame.init()
        self.root = tk.Tk()
        self.root.withdraw()
        
        info = pygame.display.Info()
        self.largura, self.altura = info.current_w, info.current_h
        self.tela = pygame.display.set_mode((self.largura, self.altura), pygame.RESIZABLE)
        pygame.display.set_caption("MTG Commander Simulator")
        
        # --- Componentes Principais ---
        self.ui = UIComponents(self.largura, self.altura)
        self.assets_mgr = AssetsManager()
        self.table_mgr = TableManager(self.largura, self.altura)
        self.turn_mgr = TurnManager()
        self.combat_mgr = CombatManager()
        
        self.fontes = {
            'titulo': pygame.font.SysFont("Arial", 64, bold=True),
            'menu': pygame.font.SysFont("Arial", 28, bold=True),
            'vida': pygame.font.SysFont("Arial", 36, bold=True),
            'fase': pygame.font.SysFont("Arial", 22, bold=True)
        }
        
        self.menu_view = MenuView(self.tela, self.ui, self.fontes)
        self.handler = InputHandler(self)
        
        # --- Estados do Jogo ---
        self.ESTADO_MENU, self.ESTADO_JOGO, self.ESTADO_CADASTRO = "menu", "jogo", "cadastro"
        self.estado_atual = self.ESTADO_MENU
        self.executando = True
        self.relogio = pygame.time.Clock()
        
        # --- Dados de Sessão ---
        self.jogadores_ativos = []
        self.jogador_local = None
        self.total_jogadores_selecionado = 4 
        self.decks_disponiveis = []
        self.indice_deck_selecionado = 0
        self.nome_sala = ""
        self.input_ativo_sala = False
        
        # Cadastro
        self.input_nome_deck = ""
        self.caminho_arquivo_selecionado = ""
        self.input_ativo_deck = False

        self.atualizar_lista_decks()

    def atualizar_lista_decks(self):
        caminho_decks = os.path.join(diretorio_raiz, "assets", "decks")
        if os.path.exists(caminho_decks):
            self.decks_disponiveis = [d for d in os.listdir(caminho_decks) if os.path.isdir(os.path.join(caminho_decks, d))]
        if not self.decks_disponiveis:
            self.decks_disponiveis = ["Nenhum Deck Encontrado"]

    def iniciar_jogo(self):
        """Prepara a partida para 2, 3 ou 4 jogadores."""
        if not self.decks_disponiveis or self.decks_disponiveis[0] == "Nenhum Deck Encontrado": 
            return
        
        nome_deck = self.decks_disponiveis[self.indice_deck_selecionado]
        caminho_txt = os.path.join(diretorio_raiz, "assets", "decks", nome_deck, "decklist.txt")
        
        if os.path.exists(caminho_txt):
            lista_nomes = DeckLoader.load_from_txt(caminho_txt)
            
            # Ajusta o layout visual conforme a sua imagem (quadrantes)
            self.table_mgr.ajustar_layout(self.total_jogadores_selecionado)
            
            self.jogadores_ativos = []
            self.combat_mgr.limpar_combate()

            for i in range(self.total_jogadores_selecionado):
                is_bot = (i != 0)
                # Slot 0 = Você (Inferior Esquerdo conforme TableManager)
                nome_player = "Você" if i == 0 else f"Bot {i}"
                
                p = Player(nome_player, lista_nomes)
                p.shuffle()
                p.draw(self.assets_mgr, 7, nome_deck)
                
                if i == 0: self.jogador_local = p
                
                self.jogadores_ativos.append({
                    'player': p, 
                    'slot': i, 
                    'is_bot': is_bot
                })
            
            self.turn_mgr.em_mulligan = True 
            self.estado_atual = self.ESTADO_JOGO

    def update(self):
        if self.estado_atual == self.ESTADO_JOGO:
            pos_mouse = pygame.mouse.get_pos()
            nome_deck_atual = self.decks_disponiveis[self.indice_deck_selecionado]
            fase_atual = self.turn_mgr.get_fase_atual()

            # Resolução Automática de Dano de Combate
            if fase_atual == "DAMAGE" and self.combat_mgr.fila_ataque:
                self.combat_mgr.resolver_dano_total(self.jogadores_ativos, RulesEngine)

            for item in self.jogadores_ativos:
                p = item['player']
                quad = self.table_mgr.get_player_quadrant(item['slot'])
                
                # CORREÇÃO: Passando todos os parâmetros para o AIEngine
                if item['is_bot'] and not self.turn_mgr.em_mulligan:
                    AIEngine.pensar_e_jogar(
                        item, self.assets_mgr, nome_deck_atual, 
                        self.turn_mgr, self.combat_mgr, self.jogadores_ativos
                    )
                
                # Interação do Humano
                if p == self.jogador_local:
                    todas = p.hand + p.battlefield
                    hover_found = False
                    for c in reversed(todas):
                        if c.rect.collidepoint(pos_mouse) and not hover_found and not any(x.dragging for x in todas):
                            c.is_hovered = True
                            hover_found = True
                        else:
                            c.is_hovered = False
                    for c in todas: c.update_position(pos_mouse)
                
                # Organização nas áreas da mesa
                p.organize_battlefield(quad.width, quad.height, quad.x, quad.y)
                if p == self.jogador_local:
                    p.organize_hand(quad.width, quad.height, quad.x, quad.y)

    def draw(self):
        self.tela.fill((15, 15, 15)) # Fundo escuro para destacar os quadrantes
        
        if self.estado_atual == self.ESTADO_MENU:
            self.menu_view.exibir_menu_principal(
                self.nome_sala, self.input_ativo_sala, 
                self.decks_disponiveis, self.indice_deck_selecionado,
                self.total_jogadores_selecionado
            )

        elif self.estado_atual == self.ESTADO_CADASTRO:
            self.menu_view.exibir_tela_cadastro(self.input_nome_deck, self.input_ativo_deck, 
                                              self.caminho_arquivo_selecionado)

        elif self.estado_atual == self.ESTADO_JOGO:
            # Desenha as linhas de divisão da mesa
            self.table_mgr.draw_layout(self.tela, self.turn_mgr.indice_jogador_ativo)
            
            for item in self.jogadores_ativos:
                p = item['player']
                quad = self.table_mgr.get_player_quadrant(item['slot'])
                
                # Renderiza o Nome do Bot/Jogador conforme a imagem
                cor_nome = (255, 255, 0) if item['is_bot'] else (0, 255, 0)
                txt_nome = self.fontes['fase'].render(p.name, True, cor_nome)
                self.tela.blit(txt_nome, (quad.x + 10, quad.bottom - 30))

                # HUD de Vida (Posicionado no topo de cada quadrante)
                pygame.draw.rect(self.tela, (0, 100, 0), (quad.x + 10, quad.y + 10, 30, 30)) # Quadrado verde de vida
                txt_vida = self.fontes['vida'].render(str(p.life), True, (200, 200, 200))
                self.tela.blit(txt_vida, (quad.x + 50, quad.y + 10))
                
                # Desenha as cartas do campo e mão
                for c in p.battlefield:
                    if not c.is_hovered: c.draw(self.tela)
                
                # Apenas desenha a mão do jogador local para manter o "segredo"
                if p == self.jogador_local:
                    for c in p.hand:
                        if not c.is_hovered: c.draw(self.tela)
                
                # Hover por último
                for c in p.battlefield + p.hand:
                    if c.is_hovered: c.draw(self.tela)

            # Botão Central de Fase
            self.ui.desenhar_botao_arredondado(self.tela, (0, 80, 150), self.ui.btn_proxima_fase, 
                                             self.turn_mgr.get_fase_atual(), self.fontes['fase'])
            
            # Interface de Mulligan (MANTER / MULLIGAN)
            if self.turn_mgr.em_mulligan:
                overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.tela.blit(overlay, (0,0))
                self.ui.desenhar_botao_arredondado(self.tela, (34, 177, 76), self.ui.btn_manter_mao, "MANTER", self.fontes['menu'])
                self.ui.desenhar_botao_arredondado(self.tela, (180, 50, 50), self.ui.btn_fazer_mulligan, "MULLIGAN", self.fontes['menu'])

        pygame.display.flip()

    def run(self):
        while self.executando:
            self.handler.processar_eventos(pygame.event.get())
            self.update()
            self.draw()
            self.relogio.tick(60)
        pygame.quit()

if __name__ == "__main__":
    MTGGame().run()