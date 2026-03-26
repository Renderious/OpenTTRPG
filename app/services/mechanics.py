import math
from typing import Optional, Dict
from app.services.dice import DiceParser, RollResult

def calculate_ability_modifier(score: int) -> int:
    """Calculate the ability modifier based on the ability score."""
    return math.floor((score - 10) / 2)

def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on character level."""
    if level < 1:
        return 2  # default or lower bounds
    return math.ceil(level / 4) + 1

def calculate_ac(dex_mod: int, base: int = 10, armor_bonus: int = 0, shield_bonus: int = 0, max_dex: Optional[int] = None) -> int:
    """Calculate Armor Class."""
    effective_dex_mod = dex_mod
    if max_dex is not None:
        effective_dex_mod = min(dex_mod, max_dex)
    return base + effective_dex_mod + armor_bonus + shield_bonus

def calculate_hp(hit_dice_val: int, level: int, con_mod: int, roll_hp: bool = False, seed: Optional[int] = None) -> int:
    """
    Calculate max HP. 1st level is max hit die + con_mod.
    Subsequent levels are either rolled or take average.
    Average is (hit_dice_val / 2) + 1.
    """
    if level < 1:
        return 0

    hp = hit_dice_val + con_mod

    if level > 1:
        if roll_hp:
            # We roll 1d(hit_dice_val) for each level above 1
            roll_str = f"{level - 1}d{hit_dice_val}"
            result = DiceParser.parse_and_roll(roll_str, seed=seed)
            hp += result.total + (con_mod * (level - 1))
        else:
            avg_hp = math.ceil((hit_dice_val + 1) / 2.0)
            hp += (avg_hp + con_mod) * (level - 1)

    # Minimum 1 HP per level even if con mod is negative
    # Some variants say minimum 1 overall, but let's just make sure it's at least 1 per level if taking total
    # HP could be very low, but typically D&D 5e minimum max HP is level * 1 (at least 1 per level) or just 1 overall.
    # We won't strictly enforce an obscure rule unless standard.
    return max(1, hp)

def saving_throw(ability_mod: int, is_proficient: bool = False, proficiency_bonus: int = 0, advantage: bool = False, disadvantage: bool = False, seed: Optional[int] = None) -> RollResult:
    """Roll a saving throw."""
    modifier = ability_mod
    if is_proficient:
        modifier += proficiency_bonus

    mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
    notation = f"1d20{mod_str}"

    return DiceParser.parse_and_roll(notation, advantage=advantage, disadvantage=disadvantage, seed=seed)

def skill_check(ability_mod: int, is_proficient: bool = False, proficiency_bonus: int = 0, expertise: bool = False, advantage: bool = False, disadvantage: bool = False, seed: Optional[int] = None) -> RollResult:
    """Roll a skill check."""
    modifier = ability_mod
    if is_proficient:
        modifier += proficiency_bonus
    if expertise:
        modifier += proficiency_bonus

    mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
    notation = f"1d20{mod_str}"

    return DiceParser.parse_and_roll(notation, advantage=advantage, disadvantage=disadvantage, seed=seed)

def attack_roll(ability_mod: int, proficiency_bonus: int = 0, is_proficient: bool = True, target_ac: Optional[int] = None, advantage: bool = False, disadvantage: bool = False, seed: Optional[int] = None) -> Dict[str, any]:
    """
    Roll an attack and compare against target AC if provided.
    Returns the roll result and whether it hit.
    """
    modifier = ability_mod
    if is_proficient:
        modifier += proficiency_bonus

    mod_str = f"+{modifier}" if modifier >= 0 else f"{modifier}"
    notation = f"1d20{mod_str}"

    result = DiceParser.parse_and_roll(notation, advantage=advantage, disadvantage=disadvantage, seed=seed)

    is_hit = False
    if result.is_crit:
        is_hit = True
    elif result.is_fail:
        is_hit = False
    elif target_ac is not None:
        if result.total >= target_ac:
            is_hit = True

    return {
        "roll": result,
        "is_hit": is_hit,
        "is_crit": result.is_crit,
        "is_fail": result.is_fail
    }

def damage_roll(weapon_notation: str, ability_mod: int = 0, is_crit: bool = False, seed: Optional[int] = None) -> RollResult:
    """
    Roll damage. If crit, rolls the dice twice (or rolls double the dice depending on standard 5e rules: usually rolls damage dice twice).
    """
    import re

    if seed is not None:
        import random
        random.seed(seed)

    notation = weapon_notation.replace(" ", "").lower()

    # We can use DiceParser to parse base weapon damage
    # First, let's extract the base dice to double them if crit
    if is_crit:
        # standard 5e rule: roll all of the attack's damage dice twice and add them together, then add relevant modifiers
        # We need to parse XdY and double the X.
        pattern = re.compile(
            r"^(?P<num>\d*)d(?P<sides>\d+)"
            r"(?:(?P<keep_drop>k|dl)(?P<kd_val>\d+))?"
            r"(?:(?P<mod_sign>[\+\-])(?P<mod_val>\d+))?$"
        )
        match = pattern.match(notation)
        if match:
            num_str = match.group("num")
            num = int(num_str) if num_str else 1
            sides = int(match.group("sides"))
            new_num = num * 2

            # Reconstruct notation
            kd = match.group("keep_drop") or ""
            kdv = match.group("kd_val") or ""
            ms = match.group("mod_sign") or ""
            mv = match.group("mod_val") or ""
            notation = f"{new_num}d{sides}{kd}{kdv}{ms}{mv}"

    # Now just append ability mod to the notation
    if ability_mod != 0:
        # Check if notation already has a modifier
        if "+" in notation or "-" in notation:
            # Evaluate base roll with its own modifier, then add ability_mod
            result = DiceParser.parse_and_roll(notation, seed=seed)
            result.modifiers += ability_mod
            result.total += ability_mod
            return result
        else:
            mod_str = f"+{ability_mod}" if ability_mod > 0 else f"{ability_mod}"
            notation += mod_str

    return DiceParser.parse_and_roll(notation, seed=seed)
