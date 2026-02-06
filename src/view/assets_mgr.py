import pygame
import os
import requests
import threading
import json

class AssetsManager:
    def __init__(self):
        self.card_images = {}
        # --- CORREÇÃO DO ERRO ---
        # Inicializamos o cache de dados para que a classe Card possa consultá-lo
        self.card_data_cache = {} 
        self.download_queue = []
        self.is_downloading = False
        
        # Cria uma fonte padrão para desenhar placeholders
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)

    def get_card_image(self, card_name, deck_name=None):
        """
        Retorna a imagem da carta. Se não existir, retorna um placeholder
        e tenta carregar do disco.
        """
        # Se já está na memória RAM, retorna direto
        if card_name in self.card_images:
            return self.card_images[card_name]

        # Tenta carregar do disco
        image = self.load_from_disk(card_name, deck_name)
        
        if image:
            self.card_images[card_name] = image
            return image
        
        # Se não achou em lugar nenhum, cria um placeholder temporário
        return self.create_placeholder(card_name)

    def load_from_disk(self, card_name, deck_name):
        """Tenta encontrar o arquivo de imagem nas pastas."""
        base_path = os.path.join("assets", "decks")
        possible_paths = []
        
        # Gera nomes de arquivo possíveis (ex: "Sol Ring.jpg", "Sol Ring.png")
        extensions = [".jpg", ".png", ".jpeg"]
        
        # 1. Procura na pasta específica do deck
        if deck_name:
            for ext in extensions:
                possible_paths.append(os.path.join(base_path, deck_name, card_name + ext))
        
        # 2. Procura numa pasta genérica 'cache' ou 'all_cards' (opcional)
        for ext in extensions:
            possible_paths.append(os.path.join("assets", "cards", card_name + ext))

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Tenta carregar o JSON de dados associado se existir
                    json_path = path.rsplit('.', 1)[0] + ".json"
                    if os.path.exists(json_path):
                        with open(json_path, 'r', encoding='utf-8') as f:
                            self.card_data_cache[card_name] = json.load(f)
                    return img
                except Exception as e:
                    print(f"Erro ao carregar imagem {path}: {e}")
        
        return None

    def create_placeholder(self, text):
        """Cria uma imagem cinza com o nome da carta (para quando a imagem falta)."""
        surface = pygame.Surface((220, 300))
        surface.fill((100, 100, 100)) # Cinza
        pygame.draw.rect(surface, (200, 200, 200), (5, 5, 210, 290), 2) # Borda
        
        # Renderiza o texto (quebra de linha simples)
        words = text.split()
        y = 50
        for word in words:
            txt_img = self.font.render(word, True, (255, 255, 255))
            surface.blit(txt_img, (110 - txt_img.get_width()//2, y))
            y += 20
            
        return surface

    def baixar_deck_completo(self, nome_deck, lista_cartas, tela, fonte):
        """
        Baixa imagens e dados (JSON) do Scryfall.
        """
        base_dir = os.path.join("assets", "decks", nome_deck)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        total = len(lista_cartas)
        
        for i, card_name in enumerate(lista_cartas):
            # Atualiza tela de carregamento
            tela.fill((0, 0, 0))
            texto = fonte.render(f"Baixando: {card_name} ({i+1}/{total})", True, (255, 255, 255))
            tela.blit(texto, (tela.get_width()//2 - texto.get_width()//2, tela.get_height()//2))
            pygame.display.flip()
            
            # Caminhos de destino
            caminho_img = os.path.join(base_dir, f"{card_name}.jpg")
            caminho_json = os.path.join(base_dir, f"{card_name}.json")
            
            # Pula se já existe
            if os.path.exists(caminho_img) and os.path.exists(caminho_json):
                # Carrega o JSON para a memória já que estamos aqui
                try:
                    with open(caminho_json, 'r', encoding='utf-8') as f:
                        self.card_data_cache[card_name] = json.load(f)
                except: pass
                continue
                
            try:
                # 1. Busca dados na API
                url_api = f"https://api.scryfall.com/cards/named?exact={card_name}"
                resp = requests.get(url_api, timeout=5)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Salva JSON (Importante para saber se é Land depois!)
                    relevant_data = {
                        "name": data.get("name"),
                        "type_line": data.get("type_line"),
                        "oracle_text": data.get("oracle_text", ""),
                        "mana_cost": data.get("mana_cost", "")
                    }
                    with open(caminho_json, 'w', encoding='utf-8') as f:
                        json.dump(relevant_data, f, ensure_ascii=False)
                    
                    # Guarda no cache em memória agora
                    self.card_data_cache[card_name] = relevant_data

                    # 2. Baixa Imagem
                    if "image_uris" in data:
                        img_url = data["image_uris"]["normal"]
                        img_data = requests.get(img_url).content
                        with open(caminho_img, 'wb') as f:
                            f.write(img_data)
                    else:
                        print(f"Sem imagem para {card_name}")
                else:
                    print(f"Erro Scryfall {card_name}: {resp.status_code}")
                    
            except Exception as e:
                print(f"Erro ao baixar {card_name}: {e}")

            pygame.event.pump() # Mantém a janela viva
