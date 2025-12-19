import random
import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

class TerrainType(Enum):
    PLAINS = "Равнины"
    FOREST = "Лес"
    MOUNTAINS = "Горы"
    HILLS = "Холмы"
    COAST = "Побережье"
    OCEAN = "Океан"

class UnitType(Enum):
    SETTLER = "Поселенец"
    WARRIOR = "Воин"
    ARCHER = "Лучник"
    SCOUT = "Разведчик"
    SPEARMAN = "Копейщик"
    HORSEMAN = "Всадник"
    CATAPULT = "Катапульта"

class BuildingType(Enum):
    GRANARY = "Амбар"
    BARRACKS = "Казармы"
    LIBRARY = "Библиотека"
    MARKET = "Рынок"
    WALLS = "Стены"
    TEMPLE = "Храм"

class Technology(Enum):
    AGRICULTURE = "Земледелие"
    POTTERY = "Гончарное дело"
    WRITING = "Письменность"
    ARCHERY = "Стрельба из лука"
    MINING = "Горное дело"
    BRONZE_WORKING = "Обработка бронзы"
    THE_WHEEL = "Колесо"
    MASONRY = "Каменная кладка"
    HORSEBACK_RIDING = "Верховая езда"
    MATHEMATICS = "Математика"

class Civilization:
    def __init__(self, name: str, leader: str):
        self.name = name
        self.leader = leader
        self.cities: List[City] = []
        self.technology: Dict[Technology, bool] = {tech: False for tech in Technology}
        self.discovered_techs: List[Technology] = []
        self.gold = 100
        self.science_per_turn = 0
        self.gold_per_turn = 0
        self.units: List[Unit] = []
        self.diplomacy: Dict[str, str] = {}  # цивилизация: статус
        self.active_research: Optional[Technology] = None
        
    def add_city(self, city: 'City'):
        self.cities.append(city)
        
    def calculate_yields(self):
        self.science_per_turn = sum(city.science for city in self.cities)
        self.gold_per_turn = sum(city.gold for city in self.cities) - len(self.units) * 1
        
    def research_tech(self, tech: Technology) -> bool:
        if self.technology[tech]:
            return False
            
        if tech not in self.discovered_techs:
            self.active_research = tech
            return True
        return False
    
    def complete_research(self):
        if self.active_research:
            self.technology[self.active_research] = True
            self.discovered_techs.append(self.active_research)
            self.active_research = None

class City:
    def __init__(self, name: str, x: int, y: int, civilization: Civilization):
        self.name = name
        self.x = x
        self.y = y
        self.population = 1
        self.food = 0
        self.production = 0
        self.science = 0
        self.gold = 0
        self.happiness = 100
        self.buildings: List[BuildingType] = []
        self.current_production: Optional[UnitType] = None
        self.production_progress = 0
        self.terrain = random.choice(list(TerrainType))
        self.civilization = civilization
        
    def work_tile(self):
        # Производство в зависимости от местности
        if self.terrain == TerrainType.PLAINS:
            self.food += 2
            self.production += 1
        elif self.terrain == TerrainType.FOREST:
            self.food += 1
            self.production += 2
        elif self.terrain == TerrainType.HILLS:
            self.production += 3
            self.gold += 1
        elif self.terrain == TerrainType.COAST:
            self.food += 2
            self.gold += 2
            
        if BuildingType.GRANARY in self.buildings:
            self.food += 1
        if BuildingType.LIBRARY in self.buildings:
            self.science += 2
        if BuildingType.MARKET in self.buildings:
            self.gold += 2
            
    def set_production(self, unit_type: UnitType):
        self.current_production = unit_type
        self.production_progress = 0
        
    def process_turn(self):
        self.work_tile()
        
        if self.current_production:
            cost = UNIT_COSTS[self.current_production]
            self.production_progress += self.production
            
            if self.production_progress >= cost:
                self.production_progress = 0
                unit = Unit(self.current_production, self.x, self.y, self.civilization)
                self.civilization.units.append(unit)
                print(f"В городе {self.name} построен {unit.type.value}!")
                self.current_production = None

class Unit:
    def __init__(self, unit_type: UnitType, x: int, y: int, civilization: Civilization):
        self.type = unit_type
        self.x = x
        self.y = y
        self.health = 100
        self.moves = 2
        self.combat_strength = UNIT_STRENGTH[unit_type]
        self.civilization = civilization
        
    def move(self, dx: int, dy: int):
        if self.moves > 0:
            self.x += dx
            self.y += dy
            self.moves -= 1
            return True
        return False
    
    def reset_moves(self):
        self.moves = 2

class WorldMap:
    def __init__(self, width: int = 20, height: int = 15):
        self.width = width
        self.height = height
        self.tiles = [[random.choice(list(TerrainType)) for _ in range(width)] for _ in range(height)]
        self.cities: List[City] = []
        self.units: List[Unit] = []
        
    def display(self, player_civ: Civilization):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 80)
        print("КАРТА МИРА".center(80))
        print("=" * 80)
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                # Проверяем, есть ли город
                city = next((c for c in self.cities if c.x == x and c.y == y), None)
                unit = next((u for u in self.units if u.x == x and u.y == y), None)
                
                if city:
                    if city.civilization == player_civ:
                        row += "[C]"
                    else:
                        row += "[c]"
                elif unit:
                    if unit.civilization == player_civ:
                        row += " U "
                    else:
                        row += " u "
                else:
                    terrain = self.tiles[y][x]
                    if terrain == TerrainType.PLAINS:
                        row += " . "
                    elif terrain == TerrainType.FOREST:
                        row += " ^ "
                    elif terrain == TerrainType.MOUNTAINS:
                        row += " /\ "
                    elif terrain == TerrainType.HILLS:
                        row += " n "
                    elif terrain == TerrainType.COAST:
                        row += " ~ "
                    else:
                        row += " O "
            print(row)
        print("=" * 80)
        print("Легенда: [C] - ваш город, [c] - чужой город, U - ваш юнит, u - чужой юнит")
        print(". - равнины, ^ - лес, /\\ - горы, n - холмы, ~ - побережье, O - океан")
        print("=" * 80)

# Константы
UNIT_COSTS = {
    UnitType.SETTLER: 100,
    UnitType.WARRIOR: 40,
    UnitType.ARCHER: 60,
    UnitType.SCOUT: 25,
    UnitType.SPEARMAN: 50,
    UnitType.HORSEMAN: 80,
    UnitType.CATAPULT: 120
}

UNIT_STRENGTH = {
    UnitType.SETTLER: 0,
    UnitType.WARRIOR: 10,
    UnitType.ARCHER: 12,
    UnitType.SCOUT: 5,
    UnitType.SPEARMAN: 15,
    UnitType.HORSEMAN: 18,
    UnitType.CATAPULT: 20
}

BUILDING_COSTS = {
    BuildingType.GRANARY: 60,
    BuildingType.BARRACKS: 80,
    BuildingType.LIBRARY: 90,
    BuildingType.MARKET: 100,
    BuildingType.WALLS: 120,
    BuildingType.TEMPLE: 80
}

TECH_COSTS = {
    Technology.AGRICULTURE: 20,
    Technology.POTTERY: 25,
    Technology.WRITING: 40,
    Technology.ARCHERY: 35,
    Technology.MINING: 30,
    Technology.BRONZE_WORKING: 50,
    Technology.THE_WHEEL: 45,
    Technology.MASONRY: 55,
    Technology.HORSEBACK_RIDING: 60,
    Technology.MATHEMATICS: 70
}

TECH_REQUIREMENTS = {
    Technology.POTTERY: [Technology.AGRICULTURE],
    Technology.WRITING: [Technology.POTTERY],
    Technology.ARCHERY: [Technology.AGRICULTURE],
    Technology.MINING: [],
    Technology.BRONZE_WORKING: [Technology.MINING],
    Technology.THE_WHEEL: [Technology.AGRICULTURE],
    Technology.MASONRY: [Technology.MINING],
    Technology.HORSEBACK_RIDING: [Technology.THE_WHEEL],
    Technology.MATHEMATICS: [Technology.WRITING]
}

class Game:
    def __init__(self):
        self.world = WorldMap()
        self.player_civ = None
        self.ai_civs: List[Civilization] = []
        self.turn = 0
        self.game_over = False
        
    def setup_game(self):
        print("ДОБРО ПОЖАЛОВАТЬ В ЦИВИЛИЗАЦИЮ!")
        print("\nСоздайте свою цивилизацию:")
        civ_name = input("Название цивилизации: ") or "Рим"
        leader_name = input("Имя лидера: ") or "Цезарь"
        
        self.player_civ = Civilization(civ_name, leader_name)
        
        # Создаем первый город
        start_x, start_y = self.world.width // 2, self.world.height // 2
        capital = City(f"Столица {civ_name}", start_x, start_y, self.player_civ)
        self.player_civ.add_city(capital)
        self.world.cities.append(capital)
        
        # Создаем первого юнита
        settler = Unit(UnitType.SETTLER, start_x, start_y, self.player_civ)
        self.player_civ.units.append(settler)
        self.world.units.append(settler)
        
        # Создаем AI цивилизации
        self.create_ai_civilizations()
        
        # Начинаем с базовых технологий
        self.player_civ.technology[Technology.AGRICULTURE] = True
        self.player_civ.discovered_techs.append(Technology.AGRICULTURE)
        
    def create_ai_civilizations(self):
        ai_names = ["Египет", "Греция", "Персия", "Карфаген"]
        ai_leaders = ["Рамзес", "Александр", "Кир", "Ганнибал"]
        
        for i in range(2):
            x = random.randint(0, self.world.width - 1)
            y = random.randint(0, self.world.height - 1)
            
            civ = Civilization(ai_names[i], ai_leaders[i])
            city = City(f"Столица {ai_names[i]}", x, y, civ)
            civ.add_city(city)
            
            warrior = Unit(UnitType.WARRIOR, x, y, civ)
            civ.units.append(warrior)
            
            self.ai_civs.append(civ)
            self.world.cities.append(city)
            self.world.units.append(warrior)
            
            # Устанавливаем дипломатические отношения
            self.player_civ.diplomacy[civ.name] = "Мир"
            civ.diplomacy[self.player_civ.name] = "Мир"
    
    def display_status(self):
        print(f"\nХод: {self.turn}")
        print(f"Цивилизация: {self.player_civ.name} ({self.player_civ.leader})")
        print(f"Золото: {self.player_civ.gold} (+{self.player_civ.gold_per_turn}/ход)")
        print(f"Наука: {self.player_civ.science_per_turn}/ход")
        
        if self.player_civ.active_research:
            print(f"Исследуется: {self.player_civ.active_research.value}")
        else:
            print("Исследование не выбрано")
            
        print(f"\nГорода ({len(self.player_civ.cities)}):")
        for city in self.player_civ.cities:
            print(f"  {city.name} - Население: {city.population}, Еда: {city.food}, Производство: {city.production}")
            if city.current_production:
                print(f"    Строится: {city.current_production.value}")
                
        print(f"\nЮниты ({len(self.player_civ.units)}):")
        for unit in self.player_civ.units:
            print(f"  {unit.type.value} ({unit.x},{unit.y}) - Сила: {unit.combat_strength}")
            
        print(f"\nОткрытые технологии ({len(self.player_civ.discovered_techs)}):")
        for tech in self.player_civ.discovered_techs:
            print(f"  {tech.value}")
    
    def city_management(self):
        if not self.player_civ.cities:
            print("У вас нет городов!")
            return
            
        print("\nУПРАВЛЕНИЕ ГОРОДАМИ")
        for i, city in enumerate(self.player_civ.cities):
            print(f"{i+1}. {city.name} - Производство: {city.production}")
            
        choice = input("\nВыберите город для управления (или Enter для выхода): ")
        if not choice:
            return
            
        try:
            city_idx = int(choice) - 1
            if 0 <= city_idx < len(self.player_civ.cities):
                city = self.player_civ.cities[city_idx]
                self.manage_city(city)
        except ValueError:
            pass
    
    def manage_city(self, city: City):
        while True:
            print(f"\nУправление городом: {city.name}")
            print(f"Население: {city.population}")
            print(f"Ресурсы: Еда: {city.food}, Производство: {city.production}, Золото: {city.gold}, Наука: {city.science}")
            print(f"Текущее производство: {city.current_production.value if city.current_production else 'Нет'}")
            
            print("\nДоступные постройки:")
            available_buildings = []
            for building in BuildingType:
                if building not in city.buildings:
                    cost = BUILDING_COSTS[building]
                    print(f"  {building.value} - {cost} производства")
                    available_buildings.append(building)
            
            print("\nДоступные юниты:")
            available_units = []
            for unit in UnitType:
                if unit == UnitType.SETTLER or self.player_civ.technology.get(Technology.BRONZE_WORKING, False):
                    cost = UNIT_COSTS[unit]
                    print(f"  {unit.value} - {cost} производства")
                    available_units.append(unit)
            
            print("\n1. Назначить производство юнита")
            print("2. Назначить постройку")
            print("3. Информация о городе")
            print("4. Вернуться")
            
            choice = input("\nВыберите действие: ")
            
            if choice == "1":
                print("\nВыберите юнита для производства:")
                for i, unit in enumerate(available_units, 1):
                    print(f"{i}. {unit.value}")
                
                unit_choice = input("Выбор: ")
                try:
                    idx = int(unit_choice) - 1
                    if 0 <= idx < len(available_units):
                        city.set_production(available_units[idx])
                        print(f"Начато производство {available_units[idx].value}")
                except ValueError:
                    pass
                    
            elif choice == "2":
                print("\nВыберите постройку:")
                for i, building in enumerate(available_buildings, 1):
                    print(f"{i}. {building.value}")
                
                building_choice = input("Выбор: ")
                try:
                    idx = int(building_choice) - 1
                    if 0 <= idx < len(available_buildings):
                        # В этом упрощенном варианте здания строятся мгновенно
                        city.buildings.append(available_buildings[idx])
                        print(f"Построено {available_buildings[idx].value}")
                except ValueError:
                    pass
                    
            elif choice == "3":
                print(f"\nИнформация о городе {city.name}:")
                print(f"Местность: {city.terrain.value}")
                print(f"Постройки: {', '.join([b.value for b in city.buildings])}")
                
            elif choice == "4":
                break
    
    def technology_tree(self):
        print("\nТЕХНОЛОГИЧЕСКОЕ ДЕРЕВО")
        print("=" * 40)
        
        for tech in Technology:
            status = "✓" if self.player_civ.technology[tech] else " "
            cost = TECH_COSTS[tech]
            requirements = ", ".join([t.value for t in TECH_REQUIREMENTS.get(tech, [])])
            
            print(f"[{status}] {tech.value} ({cost} науки)")
            if requirements:
                print(f"    Требуется: {requirements}")
            print()
        
        if not self.player_civ.active_research:
            print("\nДоступные для исследования технологии:")
            available_techs = []
            for tech in Technology:
                if not self.player_civ.technology[tech]:
                    # Проверяем требования
                    reqs = TECH_REQUIREMENTS.get(tech, [])
                    if all(self.player_civ.technology[r] for r in reqs):
                        available_techs.append(tech)
                        print(f"{len(available_techs)}. {tech.value} - {TECH_COSTS[tech]} науки")
            
            if available_techs:
                choice = input("\nВыберите технологию для исследования (или Enter для отмены): ")
                if choice:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(available_techs):
                            self.player_civ.research_tech(available_techs[idx])
                            print(f"Начато исследование {available_techs[idx].value}")
                    except ValueError:
                        pass
        else:
            print(f"\nСейчас исследуется: {self.player_civ.active_research.value}")
    
    def unit_management(self):
        if not self.player_civ.units:
            print("У вас нет юнитов!")
            return
            
        print("\nУПРАВЛЕНИЕ ЮНИТАМИ")
        for i, unit in enumerate(self.player_civ.units, 1):
            print(f"{i}. {unit.type.value} в ({unit.x},{unit.y}) - ОЗ: {unit.health}")
        
        choice = input("\nВыберите юнит для управления (или Enter для выхода): ")
        if not choice:
            return
            
        try:
            unit_idx = int(choice) - 1
            if 0 <= unit_idx < len(self.player_civ.units):
                unit = self.player_civ.units[unit_idx]
                self.control_unit(unit)
        except ValueError:
            pass
    
    def control_unit(self, unit: Unit):
        while unit.moves > 0:
            print(f"\nУправление {unit.type.value} в ({unit.x},{unit.y})")
            print(f"Осталось ходов: {unit.moves}")
            
            print("\n1. Двигаться на север")
            print("2. Двигаться на юг")
            print("3. Двигаться на запад")
            print("4. Двигаться на восток")
            print("5. Основать город (только для поселенцев)")
            print("6. Завершить ход")
            
            choice = input("Выберите действие: ")
            
            moved = False
            if choice == "1" and unit.y > 0:
                moved = unit.move(0, -1)
            elif choice == "2" and unit.y < self.world.height - 1:
                moved = unit.move(0, 1)
            elif choice == "3" and unit.x > 0:
                moved = unit.move(-1, 0)
            elif choice == "4" and unit.x < self.world.width - 1:
                moved = unit.move(1, 0)
            elif choice == "5" and unit.type == UnitType.SETTLER:
                self.found_city(unit)
                break
            elif choice == "6":
                break
            
            if moved:
                self.world.display(self.player_civ)
    
    def found_city(self, settler: Unit):
        city_name = input("Название нового города: ") or f"Город {len(self.player_civ.cities)+1}"
        city = City(city_name, settler.x, settler.y, self.player_civ)
        self.player_civ.add_city(city)
        self.world.cities.append(city)
        
        # Удаляем поселенца
        self.player_civ.units.remove(settler)
        if settler in self.world.units:
            self.world.units.remove(settler)
        
        print(f"Основан новый город: {city_name}!")
    
    def diplomacy_menu(self):
        print("\nДИПЛОМАТИЯ")
        print("=" * 40)
        
        if not self.ai_civs:
            print("Других цивилизаций не обнаружено")
            return
            
        for i, civ in enumerate(self.ai_civs, 1):
            status = self.player_civ.diplomacy.get(civ.name, "Неизвестно")
            print(f"{i}. {civ.name} ({civ.leader}) - Отношения: {status}")
            print(f"   Городов: {len(civ.cities)}, Сила: {sum(len(c.units) for c in civ.cities)}")
        
        choice = input("\nВыберите цивилизацию для взаимодействия (или Enter для выхода): ")
        if not choice:
            return
            
        try:
            civ_idx = int(choice) - 1
            if 0 <= civ_idx < len(self.ai_civs):
                civ = self.ai_civs[civ_idx]
                print(f"\nВзаимодействие с {civ.name}")
                print("1. Объявить войну")
                print("2. Предложить мир")
                print("3. Информация")
                
                action = input("Выберите действие: ")
                if action == "1":
                    self.player_civ.diplomacy[civ.name] = "Война"
                    civ.diplomacy[self.player_civ.name] = "Война"
                    print(f"Вы объявили войну {civ.name}!")
                elif action == "2":
                    self.player_civ.diplomacy[civ.name] = "Мир"
                    civ.diplomacy[self.player_civ.name] = "Мир"
                    print(f"Вы предложили мир {civ.name}!")
        except ValueError:
            pass
    
    def process_turn(self):
        self.turn += 1
        
        # Обновляем города игрока
        for city in self.player_civ.cities:
            city.process_turn()
        
        # Обновляем ресурсы цивилизации
        self.player_civ.calculate_yields()
        self.player_civ.gold += self.player_civ.gold_per_turn
        
        # Исследования
        if self.player_civ.active_research:
            tech_cost = TECH_COSTS[self.player_civ.active_research]
            if self.player_civ.science_per_turn >= tech_cost:
                self.player_civ.complete_research()
                print(f"\nИсследована новая технология: {self.player_civ.discovered_techs[-1].value}!")
        
        # Восстанавливаем ходы юнитов
        for unit in self.player_civ.units:
            unit.reset_moves()
        
        # Ход AI
        self.ai_turn()
        
        # Проверка условий победы
        self.check_victory()
    
    def ai_turn(self):
        for civ in self.ai_civs:
            # AI развивает города
            for city in civ.cities:
                city.work_tile()
                
            # AI двигает юниты
            for unit in civ.units:
                if unit.moves > 0:
                    dx = random.choice([-1, 0, 1])
                    dy = random.choice([-1, 0, 1])
                    new_x = max(0, min(self.world.width - 1, unit.x + dx))
                    new_y = max(0, min(self.world.height - 1, unit.y + dy))
                    unit.x = new_x
                    unit.y = new_y
                    unit.moves -= 1
    
    def check_victory(self):
        if len(self.player_civ.cities) >= 5:
            print("\n🎉 ПОБЕДА! Вы основали великую империю!")
            self.game_over = True
        elif len(self.player_civ.cities) == 0:
            print("\n💀 ПОРАЖЕНИЕ! Вы потеряли все города!")
            self.game_over = True
    
    def save_game(self):
        data = {
            'turn': self.turn,
            'player_civ': {
                'name': self.player_civ.name,
                'leader': self.player_civ.leader,
                'gold': self.player_civ.gold,
                'techs': [tech.name for tech in self.player_civ.discovered_techs]
            }
        }
        
        filename = f"civilization_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Игра сохранена в файл: {filename}")
    
    def main_menu(self):
        while not self.game_over:
            self.world.display(self.player_civ)
            self.display_status()
            
            print("\nГЛАВНОЕ МЕНЮ")
            print("=" * 40)
            print("1. Управление городами")
            print("2. Управление юнитами")
            print("3. Технологическое дерево")
            print("4. Дипломатия")
            print("5. Завершить ход")
            print("6. Сохранить игру")
            print("7. Выход")
            
            choice = input("\nВыберите действие: ")
            
            if choice == "1":
                self.city_management()
            elif choice == "2":
                self.unit_management()
            elif choice == "3":
                self.technology_tree()
            elif choice == "4":
                self.diplomacy_menu()
            elif choice == "5":
                self.process_turn()
                input("\nНажмите Enter для продолжения...")
            elif choice == "6":
                self.save_game()
            elif choice == "7":
                print("Спасибо за игру!")
                break

def main():
    game = Game()
    game.setup_game()
    game.main_menu()

if __name__ == "__main__":
    main()
