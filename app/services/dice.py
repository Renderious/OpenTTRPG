import random
import re
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RollResult:
    total: int
    dice_results: List[int]
    modifiers: int
    is_crit: bool = False
    is_fail: bool = False
    notation: str = ""
    dropped_dice: List[int] = field(default_factory=list)

class DiceParser:
    # Match XdY, XdYkZ, XdYdlZ and optionally +N or -N
    # Examples: 1d20, 2d6+3, 4d6k3, 2d20dl1, d20
    # Also handles multiple modifiers sequentially like +5-2 if we needed, but simple regex does + or - one modifier
    # Updated regex to capture one optional modifier block correctly
    pattern = re.compile(
        r"^(?P<num>\d*)d(?P<sides>\d+)"
        r"(?:(?P<keep_drop>k|dl)(?P<kd_val>\d+))?"
        r"(?:(?P<mod_sign>[\+\-])(?P<mod_val>\d+))?$"
    )

    @classmethod
    def parse_and_roll(cls, notation: str, advantage: bool = False, disadvantage: bool = False, seed: Optional[int] = None) -> RollResult:
        if seed is not None:
            random.seed(seed)

        notation = notation.replace(" ", "").lower()

        # When advantage or disadvantage is true, D&D 5e generally means roll two d20s and take the highest/lowest.
        # So we roll the whole expression twice and take the better/worse result.
        # For strict advantage/disadvantage, typically it's just 1d20. We can generalize to "roll expression twice".
        if advantage and not disadvantage:
            roll1 = cls._roll_single(notation)
            roll2 = cls._roll_single(notation)
            if roll1.total >= roll2.total:
                roll1.dropped_dice.extend(roll2.dice_results)
                return roll1
            else:
                roll2.dropped_dice.extend(roll1.dice_results)
                return roll2
        elif disadvantage and not advantage:
            roll1 = cls._roll_single(notation)
            roll2 = cls._roll_single(notation)
            if roll1.total <= roll2.total:
                roll1.dropped_dice.extend(roll2.dice_results)
                return roll1
            else:
                roll2.dropped_dice.extend(roll1.dice_results)
                return roll2
        else:
            return cls._roll_single(notation)

    @classmethod
    def _roll_single(cls, notation: str) -> RollResult:
        match = cls.pattern.match(notation)
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")

        num_str = match.group("num")
        num = int(num_str) if num_str else 1
        sides = int(match.group("sides"))

        keep_drop = match.group("keep_drop")
        kd_val_str = match.group("kd_val")
        kd_val = int(kd_val_str) if kd_val_str else None

        mod_sign = match.group("mod_sign")
        mod_val_str = match.group("mod_val")
        mod_val = int(mod_val_str) if mod_val_str else 0
        modifier = mod_val if mod_sign == "+" else -mod_val if mod_sign == "-" else 0

        dice_results = [random.randint(1, sides) for _ in range(num)]

        is_crit = False
        is_fail = False

        # Check natural 20 or 1 on D20 rolls.
        # Typically applies only to 1d20 (or equivalent with adv/disadv), but if rolling a d20, we check.
        # If it's 1d20 + mod, check first die.
        if num == 1 and sides == 20:
            if dice_results[0] == 20:
                is_crit = True
            elif dice_results[0] == 1:
                is_fail = True

        active_dice = list(dice_results)
        dropped_dice = []

        if keep_drop and kd_val is not None:
            if keep_drop == 'k':
                # Keep highest kd_val
                if kd_val < num:
                    sorted_indices = sorted(range(num), key=lambda i: dice_results[i], reverse=True)
                    keep_indices = set(sorted_indices[:kd_val])
                    active_dice = []
                    for i, val in enumerate(dice_results):
                        if i in keep_indices:
                            active_dice.append(val)
                        else:
                            dropped_dice.append(val)
            elif keep_drop == 'dl':
                # Drop lowest kd_val
                if kd_val < num:
                    sorted_indices = sorted(range(num), key=lambda i: dice_results[i])
                    drop_indices = set(sorted_indices[:kd_val])
                    active_dice = []
                    for i, val in enumerate(dice_results):
                        if i not in drop_indices:
                            active_dice.append(val)
                        else:
                            dropped_dice.append(val)

        total = sum(active_dice) + modifier

        return RollResult(
            total=total,
            dice_results=dice_results,
            modifiers=modifier,
            is_crit=is_crit,
            is_fail=is_fail,
            notation=notation,
            dropped_dice=dropped_dice
        )

class DiceRollerService:
    def __init__(self):
        self.history: List[RollResult] = []

    def roll(self, notation: str, advantage: bool = False, disadvantage: bool = False, seed: Optional[int] = None) -> RollResult:
        result = DiceParser.parse_and_roll(notation, advantage=advantage, disadvantage=disadvantage, seed=seed)
        self.history.append(result)
        return result

    def clear_history(self):
        self.history.clear()

    def get_history(self) -> List[RollResult]:
        return self.history
