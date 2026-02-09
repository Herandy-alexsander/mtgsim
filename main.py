import os
import sys
import pygame
import tkinter as tk
import shutil  
import random 
from src.view.ui_utils import InfoBox
from tkinter import filedialog

# --- [CONFIGURAÇÃO DE CAMINHOS] ---
diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
if diretorio_raiz not in sys.path:
    sys.path.insert(0, diretorio_raiz)

try:
    from src.view.assets_mgr import AssetsManager
    from src.view.table_manager import TableManager 
    from src.model.deck_loader import DeckLoader
    from src.model.player import Player
    from src.model.turn_manager import TurnManager 
    from src.controller.rules_engine import RulesEngine
    from src.controller.effect_engine import EffectEngine  
    from src.controller.attachment_manager import AttachmentManager
    from src.controller.ai_engine import AIEngine
    # --- NOVOS IMPORTS ---
    from src.controller.combat_manager import CombatManager
    from src.model.graveyard_manager import GraveyardManager
except Exception as e:
    print(f"Erro ao importar módulos internos: {e}")
    sys.exit(1)

# --- [INICIALIZAÇÃO] ---
pygame.init()
root = tk.Tk()
root.withdraw()

info_renderer = InfoBox()

info = pygame.display.Info()
LARGURA, ALTURA = info.current_w, info.current_h
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
pygame.display.set_caption("MTG Commander - Combat & Graveyard Integrated")

# Fontes
fonte_titulo = pygame.font.SysFont("Arial", 64, bold=True)
fonte_menu = pygame.font.SysFont("Arial", 28, bold=True)
fonte_vida = pygame.font.SysFont("Arial", 36, bold=True)
fonte_fase = pygame.font.SysFont("Arial", 22, bold=True)

# Estados
ESTADO_MENU = "menu"
ESTADO_JOGO = "jogo"
ESTADO_CADASTRO = "cadastro"
estado_atual = ESTADO_MENU

# Variáveis Globais
gerenciador_assets = AssetsManager()
table_mgr = TableManager(LARGURA, ALTURA)
turn_mgr = TurnManager() 
attachment_mgr = AttachmentManager()
combat_mgr = CombatManager()      # Gerenciador de Combate
graveyard_mgr = GraveyardManager()  # Gerenciador de Cemitério

jogadores_ativos = [] # Lista de dicionários: {'player': obj, 'slot': int, 'is_bot': bool}
jogador_local = None
decks_disponiveis = []
indice_deck_selecionado = 0
nome_sala = ""
input_ativo_sala = False
input_nome_deck, caminho_arquivo_selecionado = "", ""
input_ativo_deck = False

def atualizar_lista_decks():
    global decks_disponiveis
    caminho_decks = os.path.join(diretorio_raiz, "assets", "decks")
    if os.path.exists(caminho_decks):
        decks_disponiveis = [d for d in os.listdir(caminho_decks) if os.path.isdir(os.path.join(caminho_decks, d))]
    if not decks_disponiveis:
        decks_disponiveis = ["Nenhum Deck Encontrado"]

atualizar_lista_decks()

# --- [BOTÕES MENU] ---
campo_texto_sala = pygame.Rect(LARGURA//2 - 150, 180, 300, 40)
btn_deck_esq = pygame.Rect(LARGURA//2 - 180, 320, 40, 40)
btn_deck_dir = pygame.Rect(LARGURA//2 + 140, 320, 40, 40)
btn_criar = pygame.Rect(LARGURA//2 - 150, 420, 300, 50)
btn_cadastrar = pygame.Rect(LARGURA//2 - 150, 500, 300, 50)
btn_voltar = pygame.Rect(20, 20, 100, 40)
rect_input_nome_deck = pygame.Rect(LARGURA//2 - 150, 200, 300, 40)
btn_selecionar_arquivo = pygame.Rect(LARGURA//2 - 150, 300, 300, 50)
btn_confirmar_cadastro = pygame.Rect(LARGURA//2 - 150, 450, 300, 50)

# Botões Jogo
btn_proxima_fase = pygame.Rect(LARGURA//2 - 90, ALTURA//2 - 30, 180, 60)
btn_manter_mao = pygame.Rect(LARGURA//2 - 210, ALTURA//2 + 50, 200, 60)
btn_fazer_mulligan = pygame.Rect(LARGURA//2 + 10, ALTURA//2 + 50, 200, 60)

def iniciar_jogo():
    global jogadores_ativos, jogador_local, estado_atual
    if not decks_disponiveis or decks_disponiveis[0] == "Nenhum Deck Encontrado": return
    
    nome_deck = decks_disponiveis[indice_deck_selecionado]
    caminho_txt = os.path.join(diretorio_raiz, "assets", "decks", nome_deck, "decklist.txt")
    
    if os.path.exists(caminho_txt):
        lista_nomes = DeckLoader.load_from_txt(caminho_txt)
        if lista_nomes:
            slots = [0, 1, 2, 3]
            jogadores_ativos = []
            for i in range(4):
                is_bot = (i != 0)
                nome_p = "Você" if i == 0 else f"Bot {i}"
                
                p = Player(nome_p, lista_nomes)
                p.shuffle()
                p.draw(gerenciador_assets, 7, nome_deck)
                
                if i == 0:
                    jogador_local = p
                
                jogadores_ativos.append({'player': p, 'slot': slots[i], 'is_bot': is_bot})
            
            turn_mgr.inicializar_jogadores([item['player'] for item in jogadores_ativos])
            turn_mgr.em_mulligan = True 
            estado_atual = ESTADO_JOGO

relogio = pygame.time.Clock()
executando = True

while executando:
    pos_mouse = pygame.mouse.get_pos()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: executando = False
            
        if estado_atual == ESTADO_MENU:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                input_ativo_sala = campo_texto_sala.collidepoint(evento.pos)
                if btn_deck_esq.collidepoint(evento.pos): indice_deck_selecionado = (indice_deck_selecionado - 1) % len(decks_disponiveis)
                if btn_deck_dir.collidepoint(evento.pos): indice_deck_selecionado = (indice_deck_selecionado + 1) % len(decks_disponiveis)
                if btn_cadastrar.collidepoint(evento.pos): estado_atual = ESTADO_CADASTRO
                if btn_criar.collidepoint(evento.pos) and nome_sala.strip(): iniciar_jogo()
            
            if evento.type == pygame.KEYDOWN and input_ativo_sala:
                if evento.key == pygame.K_BACKSPACE: nome_sala = nome_sala[:-1]
                else: nome_sala += evento.unicode

        elif estado_atual == ESTADO_CADASTRO:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if btn_voltar.collidepoint(evento.pos): estado_atual = ESTADO_MENU
                input_ativo_deck = rect_input_nome_deck.collidepoint(evento.pos)
                if btn_selecionar_arquivo.collidepoint(evento.pos):
                    c = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
                    if c: caminho_arquivo_selecionado = c
                if btn_confirmar_cadastro.collidepoint(evento.pos) and input_nome_deck and caminho_arquivo_selecionado:
                    lista = DeckLoader.load_from_txt(caminho_arquivo_selecionado)
                    gerenciador_assets.baixar_deck_completo(input_nome_deck, lista, tela, fonte_menu)
                    shutil.copy(caminho_arquivo_selecionado, os.path.join(diretorio_raiz, "assets", "decks", input_nome_deck, "decklist.txt"))
                    input_nome_deck, caminho_arquivo_selecionado = "", ""
                    atualizar_lista_decks(); estado_atual = ESTADO_MENU
            
            if evento.type == pygame.KEYDOWN and input_ativo_deck:
                if evento.key == pygame.K_BACKSPACE: input_nome_deck = input_nome_deck[:-1]
                else: input_nome_deck += evento.unicode

        elif estado_atual == ESTADO_JOGO:
            jogador_da_vez = turn_mgr.get_jogador_atual()
            is_turno_local = (jogador_da_vez == jogador_local)

            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Sistema de Seleção (Efeitos ou Combate)
                if turn_mgr.modo_selecao:
                    alvo = None
                    for item in jogadores_ativos:
                        for carta in reversed(item['player'].battlefield):
                            if carta.rect.collidepoint(evento.pos): alvo = carta; break
                    
                    if alvo:
                        # Se estivermos em fase de combate, passamos pelo combat_mgr
                        if "COMBAT" in turn_mgr.get_fase_atual().upper():
                            combat_mgr.registrar_declaracao(alvo, turn_mgr)
                        else:
                            EffectEngine.finalizar_selecao_alvo(alvo, jogador_local, turn_mgr, attachment_mgr)
                    continue

                if turn_mgr.em_mulligan:
                    if btn_manter_mao.collidepoint(evento.pos): turn_mgr.finalizar_mulligan()
                    elif btn_fazer_mulligan.collidepoint(evento.pos):
                        jogador_local.mulligan(gerenciador_assets, decks_disponiveis[indice_deck_selecionado], (turn_mgr.quantidade_mulligans == 0))
                        turn_mgr.registrar_mulligan()
                    continue

                if btn_proxima_fase.collidepoint(evento.pos) and is_turno_local:
                    # Antes de passar, o Combat Manager resolve danos se necessário
                    if turn_mgr.get_fase_atual().upper() == "COMBAT_DAMAGE":
                        combat_mgr.resolver_combate(jogadores_ativos, graveyard_mgr)
                    
                    turn_mgr.proxima_fase(jogador_local, gerenciador_assets, decks_disponiveis[indice_deck_selecionado])
                    attachment_mgr.clean_invalid_links(jogador_local.battlefield)

                # Clique no Cemitério (Novo)
                for item in jogadores_ativos:
                    quad = table_mgr.get_player_quadrant(item['slot'])
                    # Área hipotética do cemitério no quadrante
                    rect_gy = pygame.Rect(quad.right - 80, quad.bottom - 110, 70, 100)
                    if rect_gy.collidepoint(evento.pos):
                        graveyard_mgr.abrir_visualizacao(item['player'])

                # Controle de Vida
                for item in jogadores_ativos:
                    quad = table_mgr.get_player_quadrant(item['slot'])
                    if pygame.Rect(quad.x + 10, quad.y + 10, 30, 30).collidepoint(evento.pos): item['player'].change_life(1)
                    if pygame.Rect(quad.x + 10, quad.y + 50, 30, 30).collidepoint(evento.pos): item['player'].change_life(-1)

                for carta in reversed(jogador_local.hand + jogador_local.battlefield):
                    if carta.rect.collidepoint(evento.pos):
                        if evento.button == 1 and is_turno_local: 
                            carta.dragging = True
                        elif evento.button == 3 and carta in jogador_local.battlefield:
                            EffectEngine.trigger_activated_ability(carta, jogador_local, gerenciador_assets, decks_disponiveis[indice_deck_selecionado], turn_mgr, attachment_mgr)
                        break

            elif evento.type == pygame.MOUSEBUTTONUP:
                if jogador_local:
                    meu_slot = next(item['slot'] for item in jogadores_ativos if item['player'] == jogador_local)
                    quad_local = table_mgr.get_player_quadrant(meu_slot)
                    for carta in (jogador_local.hand + jogador_local.battlefield):
                        if carta.dragging:
                            carta.dragging = False
                            if carta.rect.centery < quad_local.bottom - 150:
                                if RulesEngine.can_play(jogador_local, carta, turn_mgr.get_fase_atual()):
                                    jogador_local.play_card(carta, gerenciador_assets, decks_disponiveis[indice_deck_selecionado])

    # --- ATUALIZAÇÃO ---
    if estado_atual == ESTADO_JOGO:
        nome_deck_atual = decks_disponiveis[indice_deck_selecionado]
        
        # Manutenção de cemitério: checar criaturas com resistência <= 0
        for item in jogadores_ativos:
            graveyard_mgr.processar_sba(item['player']) # State Based Actions

        for item in jogadores_ativos:
            p, slot = item['player'], item['slot']
            quad = table_mgr.get_player_quadrant(slot)
            
            if item['is_bot'] and not turn_mgr.em_mulligan and turn_mgr.get_jogador_atual() == p:
                AIEngine.pensar_e_jogar(item, gerenciador_assets, nome_deck_atual, turn_mgr)

            todas = p.hand + p.battlefield
            if p == jogador_local:
                hover_found = False
                for c in reversed(todas):
                    if c.rect.collidepoint(pos_mouse) and not hover_found and not any(x.dragging for x in todas):
                        c.is_hovered = True; hover_found = True
                    else: c.is_hovered = False
                for c in todas: c.update_position(pos_mouse)
            
            p.organize_battlefield(quad.width, quad.height, quad.x, quad.y)
            if p == jogador_local and not any(c.dragging for c in p.hand):
                p.organize_hand(quad.width, quad.height, quad.x, quad.y)

    # --- DESENHO ---
    tela.fill((30, 33, 45))
    
    if estado_atual == ESTADO_MENU:
        # (Lógica de menu idêntica mantida)
        txt_t = fonte_titulo.render("MTG SIMULATOR", True, (255, 255, 255))
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 50))
        pygame.draw.rect(tela, (100, 100, 255) if input_ativo_sala else (150, 150, 150), campo_texto_sala, 2)
        txt_s = fonte_menu.render(nome_sala or "Nome da Sala...", True, (255,255,255) if nome_sala else (100,100,100))
        tela.blit(txt_s, (campo_texto_sala.x + 10, campo_texto_sala.y + 5))
        pygame.draw.rect(tela, (60, 60, 60), btn_deck_esq); pygame.draw.rect(tela, (60, 60, 60), btn_deck_dir)
        nome_d = decks_disponiveis[indice_deck_selecionado] if decks_disponiveis else "---"
        tela.blit(fonte_menu.render(nome_d, True, (255, 255, 0)), (LARGURA//2 - 50, 325))
        for b, t, c in [(btn_criar, "ABRIR SALA", (50, 150, 50)), (btn_cadastrar, "CADASTRAR NOVO", (100, 100, 100))]:
            pygame.draw.rect(tela, c, b, border_radius=10)
            img = fonte_menu.render(t, True, (255,255,255))
            tela.blit(img, (b.centerx - img.get_width()//2, b.centery - img.get_height()//2))

    elif estado_atual == ESTADO_CADASTRO:
        # (Lógica de cadastro mantida)
        pygame.draw.rect(tela, (80, 80, 80), btn_voltar, border_radius=5)
        tela.blit(fonte_menu.render("Voltar", True, (255,255,255)), (30, 25))
        pygame.draw.rect(tela, (255,255,255) if input_ativo_deck else (100, 100, 100), rect_input_nome_deck, 2)
        tela.blit(fonte_menu.render(input_nome_deck or "Nome do Deck...", True, (100,100,100)), (rect_input_nome_deck.x+5, rect_input_nome_deck.y+5))
        pygame.draw.rect(tela, (100, 100, 100), btn_selecionar_arquivo, border_radius=10)
        tela.blit(fonte_menu.render("Selecionar .txt", True, (255,255,255)), (btn_selecionar_arquivo.x + 60, btn_selecionar_arquivo.y + 10))
        if input_nome_deck and caminho_arquivo_selecionado:
            pygame.draw.rect(tela, (50, 150, 50), btn_confirmar_cadastro, border_radius=10)
            tela.blit(fonte_menu.render("CADASTRAR", True, (255,255,255)), (btn_confirmar_cadastro.x + 80, btn_confirmar_cadastro.y + 10))

    elif estado_atual == ESTADO_JOGO:
        table_mgr.draw_layout(tela, 0)
        
        for item in jogadores_ativos:
            p, slot = item['player'], item['slot']
            quad = table_mgr.get_player_quadrant(slot)
            
            # Desenhar Cemitério (Visual)
            rect_gy = pygame.Rect(quad.right - 80, quad.bottom - 110, 70, 100)
            pygame.draw.rect(tela, (40, 40, 40), rect_gy, border_radius=5)
            if p.graveyard:
                # Desenha a última carta do cemitério no topo
                tela.blit(pygame.transform.scale(p.graveyard[-1].image, (70, 100)), rect_gy)
            
            # HUD Vida e Nome
            pygame.draw.rect(tela, (50, 150, 50), (quad.x + 10, quad.y + 10, 30, 30))
            pygame.draw.rect(tela, (150, 50, 50), (quad.x + 10, quad.y + 50, 30, 30))
            tela.blit(fonte_vida.render(str(p.life), True, (255,255,255)), (quad.x + 50, quad.y + 20))
            
            is_turno_dele = (turn_mgr.get_jogador_atual() == p)
            cor_nome = (0, 255, 0) if is_turno_dele else (255, 255, 0) if item['is_bot'] else (200, 200, 200)
            tela.blit(fonte_fase.render(p.name, True, cor_nome), (quad.x + 10, quad.bottom - 30))

            todas_visiveis = p.battlefield + (p.hand if p == jogador_local else [])
            for c in p.battlefield:
                if c.host_card and not c.is_hovered: c.draw(tela)
            for c in todas_visiveis:
                if not c.host_card and not c.is_hovered: c.draw(tela)
            for c in todas_visiveis:
                if c.is_hovered: c.draw(tela)

        # Botão de Fase
        cor_btn_fase = (0, 120, 200) if turn_mgr.get_jogador_atual() == jogador_local else (100, 100, 100)
        pygame.draw.rect(tela, cor_btn_fase, btn_proxima_fase, border_radius=10)
        tela.blit(fonte_fase.render(turn_mgr.get_fase_atual(), True, (255, 255, 255)), (btn_proxima_fase.centerx - 60, btn_proxima_fase.centery - 10))

        # Overlay de Mulligan
        if turn_mgr.em_mulligan:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200)); tela.blit(overlay, (0,0))
            pygame.draw.rect(tela, (34, 177, 76), btn_manter_mao, border_radius=10)
            pygame.draw.rect(tela, (180, 50, 50), btn_fazer_mulligan, border_radius=10)
            tela.blit(fonte_menu.render("MANTER", True, (255,255,255)), (btn_manter_mao.x+50, btn_manter_mao.y+15))
            tela.blit(fonte_menu.render("MULLIGAN", True, (255,255,255)), (btn_fazer_mulligan.x+40, btn_fazer_mulligan.y+15))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
