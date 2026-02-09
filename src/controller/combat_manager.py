import pygame
import math

class CombatManager:
    def __init__(self):
        # Dicionário para rastrear: {CriaturaAtacante: ObjetoAlvo}
        # O Alvo pode ser um Player ou outra Card (se houver bloqueio)
        self.attackers = {} 

    def declare_attacker(self, card, target):
        """Registra o ataque e vira a carta."""
        if not card.is_land:  # Apenas criaturas atacam
            self.attackers[card] = target
            card.tapped = True
            print(f"[COMBAT] {card.name} focado em {getattr(target, 'name', 'Alvo')}")

    def remove_attacker(self, card):
        """Remove uma carta específica do combate (ex: se for destruída antes do dano)."""
        if card in self.attackers:
            del self.attackers[card]

    def reset_combat(self):
        """Limpa todos os alvos (chamado no fim da fase de combate ou turno)."""
        self.attackers = {}

    def resolve_combat_damage(self):
        """
        Processa o dano de todas as criaturas atacantes.
        Retorna uma lista de criaturas que devem ir para o cemitério.
        """
        dead_creatures = []
        
        for attacker, target in self.attackers.items():
            power = int(getattr(attacker, 'power', 0))
            
            # Caso 1: Atacando um Jogador
            if hasattr(target, 'life'): 
                target.life -= power
                print(f"[DAMAGE] {target.name} recebeu {power} de dano de {attacker.name}")
            
            # Caso 2: Atacando outra Criatura (Bloqueio)
            elif hasattr(target, 'toughness'):
                # Dano mútuo
                attacker_power = power
                target_power = int(getattr(target, 'power', 0))
                
                # Aplica dano (lógica simples de MTG)
                # No futuro, podemos usar 'damage_marked' para dano persistente no turno
                if attacker_power >= int(target.toughness):
                    dead_creatures.append(target)
                if target_power >= int(attacker.toughness):
                    dead_creatures.append(attacker)
                    
        return dead_creatures

    def draw_visuals(self, screen):
        """Renderiza as setas de ataque na tela."""
        for attacker, target in self.attackers.items():
            self._draw_attack_arrow(screen, attacker.rect.center, target.rect.center)

    def _draw_attack_arrow(self, screen, start, end):
        """Desenha a seta vermelha de ataque."""
        color = (220, 20, 60)  # Vermelho Carmesim
        pygame.draw.line(screen, color, start, end, 5)
        
        # Geometria da ponta da seta
        angle = math.atan2(start[1] - end[1], end[0] - start[0])
        arrow_size = 20
        
        p1 = (end[0] + arrow_size * math.sin(angle - math.radians(60)),
              end[1] + arrow_size * math.cos(angle - math.radians(60)))
        p2 = (end[0] + arrow_size * math.sin(angle - math.radians(120)),
              end[1] + arrow_size * math.cos(angle - math.radians(120)))
        
        pygame.draw.polygon(screen, color, [end, p1, p2])
