from fractions import Fraction

class Enemy:
    def __init__(self, \
                name = "Verus Hilla", \
                defence_rate = Fraction(300, 100), \
                HP = 176_000_000_000_000, \
                level = 250, \
                elemental_resistance = Fraction(1, 2), \
                field_type = "arc", \
                field_force = 900) -> None:
        """
        field_type
        None, arc (arcane), aut (authentic/sacred)
        """
        self.name = name
        self.defence_rate = defence_rate
        self.HP = HP
        self.level = level
        self.elemental_resistance = elemental_resistance
        self.field_type = field_type
        self.field_force = field_force
    
    def show_monster_info(self):
        print(f"========== Monster Info ==========")
        for name, value in self.__dict__.items():
            print(f"{name}: {value}")
