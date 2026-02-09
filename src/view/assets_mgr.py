import pygame
import os
import requests
import threading
import json

class AssetsManager:
    def __init__(self):
        self.card_images = {}
        self.card_data_cache = {} 
        self.download_queue = []
        self.is_downloading = False
        
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)

    def get_card_image(self, card_name, deck_name=None):
        if card_name in self.card_images:
            return self.card_images[card_name]

        image = self.load_from_disk(card_name, deck_name)
        if image:
            self.card_images[card_name] = image
            return image
        
        return self.create_placeholder(card_name)

    def load_from_disk(self, card_name, deck_name):
        base_path = os.path.join("assets", "decks")
        extensions = [".jpg", ".png", ".jpeg"]
        possible_paths = []
        
        if deck_name:
            for ext in extensions:
                possible_paths.append(os.path.join(base_path, deck_name, card_name + ext))
        
        for ext in extensions:
            possible_paths.append(os.path.join("assets", "cards", card_name + ext))

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    json_path = path.rsplit('.', 1)[0] + ".json"
                    if os.path.exists(json_path):
                        with open(json_path, 'r', encoding='utf-8') as f:
                            self.card_data_cache[card_name] = json.load(f)
                    return img
                except Exception as e:
                    print(f"Erro ao carregar imagem {path}: {e}")
        return None

    def create_placeholder(self, text):
        surface = pygame.Surface((220, 300))
        surface.fill((100, 100, 100))
        pygame.draw.rect(surface, (200, 200, 200), (5, 5, 210, 290), 2)
        words = text.split()
        y = 50
        for word in words:
            txt_img = self.font.render(word, True, (255, 255, 255))
            surface.blit(txt_img, (110 - txt_img.get_width()//2, y))
            y += 20
        return surface

    def baixar_deck_completo(self, nome_deck, lista_cartas, tela, fonte):
        base_dir = os.path.join("assets", "decks", nome_deck)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        total = len(lista_cartas)
        
        for i, card_name in enumerate(lista_cartas):
            tela.fill((30, 30, 30))
            texto = fonte.render(f"Processando: {card_name} ({i+1}/{total})", True, (255, 255, 255))
            tela.blit(texto, (tela.get_width()//2 - texto.get_width()//2, tela.get_height()//2))
            pygame.display.flip()
            
            caminho_img = os.path.join(base_dir, f"{card_name}.jpg")
            caminho_json = os.path.join(base_dir, f"{card_name}.json")
            
            # Pula se já existe (Para forçar a atualização dos dados, apague a pasta do deck)
            if os.path.exists(caminho_img) and os.path.exists(caminho_json):
                try:
                    with open(caminho_json, 'r', encoding='utf-8') as f:
                        self.card_data_cache[card_name] = json.load(f)
                except: pass
                continue
                
            try:
                url_api = f"https://api.scryfall.com/cards/named?exact={card_name}"
                resp = requests.get(url_api, timeout=5)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # --- NOVO BLOCO DE EXTRAÇÃO DE DADOS ---
                    # Captura dados de cartas normais ou da primeira face de cartas duplas
                    relevant_data = {
                        "name": data.get("name"),
                        "type_line": data.get("type_line"),
                        "mana_cost": data.get("mana_cost", ""),
                        "cmc": data.get("cmc", 0),
                        "oracle_text": data.get("oracle_text", ""),
                        "flavor_text": data.get("flavor_text", ""), # <-- Flavor Text aqui
                        "power": data.get("power", ""),             # <-- Poder
                        "toughness": data.get("toughness", ""),     # <-- Resistência
                        "rarity": data.get("rarity", ""),
                        "colors": data.get("colors", [])
                    }

                    # Caso especial: Cartas de duas faces (Transformers, Sagas, etc)
                    if "card_faces" in data:
                        face = data["card_faces"][0] # Pegamos a face principal
                        relevant_data["oracle_text"] = face.get("oracle_text", relevant_data["oracle_text"])
                        relevant_data["flavor_text"] = face.get("flavor_text", relevant_data["flavor_text"])
                        relevant_data["power"] = face.get("power", relevant_data["power"])
                        relevant_data["toughness"] = face.get("toughness", relevant_data["toughness"])

                    # Salva o JSON completo com os novos campos
                    with open(caminho_json, 'w', encoding='utf-8') as f:
                        json.dump(relevant_data, f, ensure_ascii=False, indent=4)
                    
                    self.card_data_cache[card_name] = relevant_data

                    # Baixa Imagem
                    img_url = ""
                    if "image_uris" in data:
                        img_url = data["image_uris"]["normal"]
                    elif "card_faces" in data and "image_uris" in data["card_faces"][0]:
                        img_url = data["card_faces"][0]["image_uris"]["normal"]

                    if img_url:
                        img_data = requests.get(img_url).content
                        with open(caminho_img, 'wb') as f:
                            f.write(img_data)
                else:
                    print(f"Erro Scryfall {card_name}: {resp.status_code}")
                    
            except Exception as e:
                print(f"Erro ao baixar {card_name}: {e}")

            pygame.event.pump()
