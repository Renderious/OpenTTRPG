import pytest
import unittest.mock as mock
from app.services.mechanics import (
    calculate_ability_modifier,
    calculate_proficiency_bonus,
    calculate_ac,
    calculate_hp,
    saving_throw,
    skill_check,
    attack_roll,
    damage_roll
)

def test_ability_modifier():
    assert calculate_ability_modifier(1) == -5
    assert calculate_ability_modifier(10) == 0
    assert calculate_ability_modifier(11) == 0
    assert calculate_ability_modifier(12) == 1
    assert calculate_ability_modifier(15) == 2
    assert calculate_ability_modifier(20) == 5

def test_proficiency_bonus():
    assert calculate_proficiency_bonus(1) == 2
    assert calculate_proficiency_bonus(4) == 2
    assert calculate_proficiency_bonus(5) == 3
    assert calculate_proficiency_bonus(9) == 4
    assert calculate_proficiency_bonus(13) == 5
    assert calculate_proficiency_bonus(17) == 6
    assert calculate_proficiency_bonus(20) == 6

def test_ac_calculation():
    # Base AC
    assert calculate_ac(dex_mod=2) == 12
    # Base 10 + dex + armor + shield
    assert calculate_ac(dex_mod=2, armor_bonus=4, shield_bonus=2) == 18
    # Max Dex capped
    assert calculate_ac(dex_mod=5, armor_bonus=5, max_dex=2) == 17

def test_hp_calculation():
    # Lvl 1 Fighter (d10, +2 Con) -> 12
    assert calculate_hp(10, 1, 2) == 12

    # Lvl 5 Fighter average: 12 + 4 * (6 + 2) = 12 + 32 = 44
    assert calculate_hp(10, 5, 2) == 44

    # Negative con mod minimum 1 rule applied here per level: Wait, our func minimum is 1 total. Let's see.
    # d6, lvl 3, -2 con mod.
    # Lvl 1: 6 - 2 = 4
    # Lvl 2: 4 - 2 = 2
    # Lvl 3: 4 - 2 = 2
    # Total = 8.
    assert calculate_hp(6, 3, -2) == 8

    # Testing rolled HP with a seed
    # With seed=42, 4d10 rolled. Let's just mock it to test sum
    with mock.patch('app.services.mechanics.DiceParser.parse_and_roll') as mock_parse:
        from app.services.dice import RollResult
        mock_parse.return_value = RollResult(total=20, dice_results=[5, 5, 5, 5], modifiers=0)

        # level 5, 10 hit dice, con mod 2, rolled
        hp = calculate_hp(10, 5, 2, roll_hp=True)
        # 10 + 2 + 20 + (2 * 4) = 12 + 20 + 8 = 40
        assert hp == 40

def test_saving_throw():
    with mock.patch('random.randint', return_value=10):
        res = saving_throw(ability_mod=3, is_proficient=True, proficiency_bonus=2)
        assert res.total == 15
        assert res.modifiers == 5

def test_skill_check():
    with mock.patch('random.randint', return_value=10):
        # expertise + prof
        res = skill_check(ability_mod=1, is_proficient=True, proficiency_bonus=3, expertise=True)
        # modifier = 1 + 3 + 3 = 7
        assert res.total == 17
        assert res.modifiers == 7

def test_attack_roll():
    with mock.patch('random.randint', return_value=15):
        # ability 4, prof 3 -> total 7 modifier
        res = attack_roll(ability_mod=4, proficiency_bonus=3, is_proficient=True, target_ac=15)
        # roll 15 + 7 = 22
        assert res["roll"].total == 22
        assert res["is_hit"] is True

    # Crit case
    with mock.patch('random.randint', return_value=20):
        res = attack_roll(ability_mod=4, proficiency_bonus=3, target_ac=30)
        assert res["is_hit"] is True
        assert res["is_crit"] is True

    # Fail case
    with mock.patch('random.randint', return_value=1):
        res = attack_roll(ability_mod=4, proficiency_bonus=3, target_ac=1)
        assert res["is_hit"] is False
        assert res["is_fail"] is True

def test_damage_roll():
    # Normal damage
    with mock.patch('random.randint', return_value=4):
        res = damage_roll("1d8", ability_mod=3)
        assert res.total == 7
        assert len(res.dice_results) == 1

    # Crit damage (double dice)
    with mock.patch('random.randint', side_effect=[4, 5]):
        res = damage_roll("1d8", ability_mod=3, is_crit=True)
        # rolled 2d8 + 3
        # dice: 4, 5 -> 9. mod -> 3. total = 12
        assert res.total == 12
        assert len(res.dice_results) == 2

    # Weapon with built-in modifier (e.g., +1 weapon)
    with mock.patch('random.randint', return_value=4):
        res = damage_roll("1d8+1", ability_mod=3)
        # total mod should be 1 + 3 = 4
        # roll is 4 + 4 = 8
        assert res.total == 8
        assert res.modifiers == 4
