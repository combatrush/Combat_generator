import random
import numpy as np
from faker import Faker

class CombatGenerator:
    def __init__(self, seed=None):
        """
        Initialize the Combat Generator with optional random seed
        """
        self.fake = Faker()
        random.seed(seed)
        np.random.seed(seed)
        
        # Combat environment types
        self.environments = [
            "Dense Forest", "Mountain Pass", "Desert Wasteland", 
            "Urban Ruins", "Frozen Tundra", "Volcanic Terrain"
        ]
        
        # Character classes
        self.character_classes = [
            "Warrior", "Mage", "Rogue", "Archer", "Paladin", 
            "Berserker", "Assassin", "Necromancer"
        ]
        
        # Weapon types
        self.weapons = [
            "Sword", "Bow", "Staff", "Axe", "Dagger", 
            "Spear", "Mace", "Crossbow"
        ]
    
    def generate_character(self):
        """
        Generate a random character with diverse attributes
        """
        return {
            "name": self.fake.name(),
            "class": random.choice(self.character_classes),
            "weapon": random.choice(self.weapons),
            "health": random.randint(50, 200),
            "attack": random.randint(5, 25),
            "defense": random.randint(3, 20),
            "special_ability": self._generate_special_ability()
        }
    
    def _generate_special_ability(self):
        """
        Generate a unique special ability
        """
        abilities = [
            "Lightning Strike", "Healing Aura", "Shadow Step", 
            "Fire Blast", "Ice Shield", "Poison Dart"
        ]
        return random.choice(abilities)
    
    def generate_combat_scenario(self, num_participants=4):
        """
        Create a comprehensive combat scenario
        """
        scenario = {
            "environment": random.choice(self.environments),
            "participants": [self.generate_character() for _ in range(num_participants)],
            "objective": self._generate_combat_objective(),
            "difficulty": random.choice(["Easy", "Medium", "Hard", "Legendary"])
        }
        return scenario
    
    def _generate_combat_objective(self):
        """
        Generate a combat scenario objective
        """
        objectives = [
            "Capture Strategic Point",
            "Defeat Boss Enemy",
            "Survive Wave of Enemies",
            "Protect VIP",
            "Retrieve Artifact",
            "Eliminate Enemy Commander"
        ]
        return random.choice(objectives)
    
    def simulate_combat(self, scenario):
        """
        Basic combat simulation
        """
        winner = max(scenario['participants'], key=lambda x: x['attack'] + x['health'])
        return {
            "scenario": scenario,
            "winner": winner,
            "combat_log": f"Combat in {scenario['environment']} resolved!"
        }

def main():
    generator = CombatGenerator(seed=42)
    
    # Generate and print a combat scenario
    scenario = generator.generate_combat_scenario()
    print("🔮 Combat Scenario Generated 🔮")
    print("\n--- Scenario Details ---")
    print(f"Environment: {scenario['environment']}")
    print(f"Objective: {scenario['objective']}")
    print(f"Difficulty: {scenario['difficulty']}")
    
    print("\n--- Participants ---")
    for participant in scenario['participants']:
        print(f"- {participant['name']} (Class: {participant['class']}, Weapon: {participant['weapon']})")
    
    # Simulate combat
    result = generator.simulate_combat(scenario)
    print(f"\n🏆 Winner: {result['winner']['name']} ({result['winner']['class']})")
    print(result['combat_log'])

if __name__ == "__main__":
    main()
