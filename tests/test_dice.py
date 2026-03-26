import pytest
import random
from app.services.dice import DiceParser, DiceRollerService

def test_parse_basic_roll():
    # 1d20
    # Seed 1 -> random.randint(1, 20) is deterministic.
    # Let's mock random instead, or just test bounds if seed is tricky to know exactly.
    # Actually with seed=42, random.randint(1, 20) usually yields 20, 4, 1, ...
    random.seed(42)
    val = random.randint(1, 20)

    result = DiceParser.parse_and_roll("1d20", seed=42)
    assert len(result.dice_results) == 1
    assert result.total == val
    assert result.modifiers == 0

def test_parse_modifiers():
    result = DiceParser.parse_and_roll("2d6+3", seed=42)
    assert len(result.dice_results) == 2
    assert result.modifiers == 3
    assert result.total == sum(result.dice_results) + 3

def test_parse_negative_modifiers():
    result = DiceParser.parse_and_roll("1d10-2", seed=42)
    assert result.modifiers == -2
    assert result.total == sum(result.dice_results) - 2

def test_keep_highest():
    # 4d6k3
    # let's mock the dice results so we know what they are
    result = DiceParser.parse_and_roll("4d6k3", seed=42)
    assert len(result.dice_results) == 4
    # keep 3, drop 1
    assert len(result.dropped_dice) == 1
    # total should be sum of highest 3
    sorted_dice = sorted(result.dice_results, reverse=True)
    assert result.total == sum(sorted_dice[:3])

def test_drop_lowest():
    # 4d6dl1
    result = DiceParser.parse_and_roll("4d6dl1", seed=42)
    assert len(result.dice_results) == 4
    assert len(result.dropped_dice) == 1
    sorted_dice = sorted(result.dice_results)
    assert result.total == sum(sorted_dice[1:])

def test_advantage():
    # Should roll twice, keep highest
    # We can use seeds to guarantee different results
    # Just run it without seed and check properties
    result = DiceParser.parse_and_roll("1d20", advantage=True, seed=42)
    # Since it rolls twice, it drops the lowest whole roll's dice
    assert len(result.dropped_dice) == 1
    assert len(result.dice_results) == 1
    # total should be >= the dropped dice (since it's 1d20, dropped_dice is just the other d20)
    assert result.total >= result.dropped_dice[0]

def test_disadvantage():
    result = DiceParser.parse_and_roll("1d20", disadvantage=True, seed=42)
    assert len(result.dropped_dice) == 1
    assert len(result.dice_results) == 1
    assert result.total <= result.dropped_dice[0]

def test_crit_fail():
    # Find a seed that produces 20 and 1
    # Or just mock
    import unittest.mock as mock

    with mock.patch('random.randint', return_value=20):
        result = DiceParser.parse_and_roll("1d20")
        assert result.is_crit is True
        assert result.is_fail is False

    with mock.patch('random.randint', return_value=1):
        result = DiceParser.parse_and_roll("1d20")
        assert result.is_crit is False
        assert result.is_fail is True

def test_dice_roller_service():
    service = DiceRollerService()
    assert len(service.get_history()) == 0

    service.roll("1d20")
    service.roll("2d6+3")

    history = service.get_history()
    assert len(history) == 2
    assert history[0].notation == "1d20"
    assert history[1].notation == "2d6+3"

    service.clear_history()
    assert len(service.get_history()) == 0

def test_invalid_notation():
    with pytest.raises(ValueError):
        DiceParser.parse_and_roll("abc")
