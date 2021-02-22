import random
from typing import List, TypedDict


class WeaponProfile(TypedDict):
    attacks: int
    strength: int
    armour_penetration: int
    damage: int


class UnitProfile(TypedDict, total=False):
    models: int
    ballistic_skill: int
    toughness: int
    save: int


class Die(object):
    def __init__(self, faces: int = 6, total: int = None):
        self._faces: int = faces
        self._total: int = total

    @property
    def faces(self):
        return self._faces

    @property
    def total(self):
        return self._total

    def roll(self):
        self._total = random.randint(1, self.faces)


def _roll_dice(number_of_dice) -> List[Die]:
    dice: List[Die] = []

    for _ in range(number_of_dice):
        die: Die = Die()
        die.roll()
        dice.append(die)

    return dice


class Attack(object):
    def __init__(self, attacker: UnitProfile, target: UnitProfile, weapon: WeaponProfile):
        self._attacker = attacker
        self._target = target
        self._weapon = weapon
        self._attacks: int = None
        self._successful_attacks: int = None
        self._wounds: int = None
        self._successful_wounds: int = None
        self._saves: int = None
        self._successful_saves: int = None
        self._damage: int = None
        self._hit_rolls: List[Die] = None
        self._wound_rolls: List[Die] = None
        self._save_rolls: List[Die] = None

    def resolve(self):
        self._attacks = self._attacker['models'] * self._weapon['attacks']
        self._hit_rolls = _roll_dice(self._attacks)
        self._successful_attacks = len([hit_roll for hit_roll in self._hit_rolls if self._is_successful_hit_roll(hit_roll)])

        self._wounds = self._successful_attacks
        self._wound_rolls = _roll_dice(self._wounds)
        self._successful_wounds = len([wound_roll for wound_roll in self._wound_rolls if self._is_successful_wound_roll(wound_roll)])

        self._saves = self._successful_wounds
        self._save_rolls = _roll_dice(self._saves)
        self._successful_saves = len([save_roll for save_roll in self._save_rolls if self._is_successful_save_roll(save_roll)])

        self._damage = (self._successful_wounds - self._successful_saves) * self._weapon['damage']

        self._print_resolution()

    def _is_successful_hit_roll(self, hit_roll) -> bool:
        return hit_roll.total >= self._attacker['ballistic_skill']

    def _is_successful_wound_roll(self, wound_roll) -> bool:
        attacker_strength: int = self._weapon['strength']
        target_toughness: int = self._target['toughness']

        if attacker_strength >= target_toughness * 2:
            return wound_roll.total >= 2
        elif attacker_strength > target_toughness:
            return wound_roll.total >= 3
        elif attacker_strength == target_toughness:
            return wound_roll.total >= 4
        elif attacker_strength < target_toughness:
            return wound_roll.total >= 5
        else:
            return wound_roll.total >= 6

    def _is_successful_save_roll(self, save_roll) -> bool:
        weapon_armour_penetration: int = self._weapon['armour_penetration']
        target_save: int = self._target['save']

        return (save_roll.total - weapon_armour_penetration) >= target_save

    def _print_resolution(self) -> None:
        message = (
            f"{self._attacks} attacks were made of which {self._successful_attacks} were successful.\n"
            f"{self._wounds} wounds were made of which {self._successful_wounds} were successful.\n"
            f"{self._saves} saves were made of which {self._successful_saves} were successful.\n"
            f"The total damage inflicted was {self._damage}.\n"
        )

        print(message)


if __name__ == '__main__':
    attacker: UnitProfile = {
        'models': 10,
        'ballistic_skill': 3
    }

    target: UnitProfile = {
        'toughness': 4,
        'save': 3
    }

    weapon: WeaponProfile = {
        'attacks': 10,
        'strength': 5,
        'armour_penetration': -1,
        'damage': 2
    }

    attack: Attack = Attack(attacker, target, weapon)
    attack.resolve()
