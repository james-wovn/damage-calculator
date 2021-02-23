import random
import statistics
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


class Result(TypedDict):
    average_hits: float
    average_wounds: float
    average_saves: float
    average_damage: float


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


class Attack(object):
    def __init__(self, attacker: UnitProfile, target: UnitProfile, weapon: WeaponProfile):
        self._attacker = attacker
        self._target = target
        self._weapon = weapon
        self._hits: int = None
        self._wounds: int = None
        self._saves: int = None
        self._damage: int = None
        self._hit_rolls: List[Die] = None
        self._wound_rolls: List[Die] = None
        self._save_rolls: List[Die] = None

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def wounds(self) -> int:
        return self._wounds

    @property
    def saves(self) -> int:
        return self._saves

    @property
    def damage(self) -> int:
        return self._damage

    def resolve(self) -> None:
        number_of_hit_rolls: int = self._attacker['models'] * self._weapon['attacks']
        self._hit_rolls = roll_dice(number_of_hit_rolls)
        self._hits = len([hit_roll for hit_roll in self._hit_rolls if self._is_successful_hit_roll(hit_roll)])

        number_of_wound_rolls = self._hits
        self._wound_rolls = roll_dice(number_of_wound_rolls)
        self._wounds = len(
            [wound_roll for wound_roll in self._wound_rolls if self._is_successful_wound_roll(wound_roll)])

        number_of_save_rolls = self._wounds
        self._save_rolls = roll_dice(number_of_save_rolls)
        self._saves = len([save_roll for save_roll in self._save_rolls if self._is_successful_save_roll(save_roll)])

        self._damage = (self._wounds - self._saves) * self._weapon['damage']

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


def roll_dice(number_of_dice: int) -> List[Die]:
    dice: List[Die] = []

    for _ in range(number_of_dice):
        die: Die = Die()
        die.roll()
        dice.append(die)

    return dice


def aggregate_attacks(attacks: List[Attack]) -> Result:
    return {
        'average_hits': statistics.mean([attack.hits for attack in attacks]),
        'average_wounds': statistics.mean([attack.wounds for attack in attacks]),
        'average_saves': statistics.mean([attack.saves for attack in attacks]),
        'average_damage': statistics.mean([attack.damage for attack in attacks])
    }


def print_result(result: Result) -> None:
    message: str = (
        f"Average damage of {result['average_damage']}: "
        f"{result['average_hits']} hits; {result['average_wounds']} wounds; {result['average_saves']} saves."
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

    attacks: List[Attack] = []

    for i in range(10000):
        attack: Attack = Attack(attacker, target, weapon)
        attack.resolve()
        attacks.append(attack)

    result: Result = aggregate_attacks(attacks)

    print_result(result)
