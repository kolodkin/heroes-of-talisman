import pytest
from unittest.mock import patch

from .card import CardDrawAction, CardSelectAction
from ..models import GameModel, PlayerModel, CharacterModel, ReportedException


@pytest.fixture
def player_model():
    """Create a test player model"""
    characters = {"knight": CharacterModel(health=2, level=1, max_health=2, skills={}, dice=1, attack=1)}
    return PlayerModel(status="connected", cards=["talisman"], characters=characters)


@pytest.fixture
def game_model(player_model):
    """Create a test game model with card_draw stage"""
    return GameModel(
        stage="card_draw",
        stage_meta={},
        deck=["talisman", "golden_apple"],
        playing="test_user",
        selected_character="knight",
        players={"test_user": player_model},
    )


def test_card_draw_action_run_without_parameters(game_model):
    """Test CardDrawAction run without parameters"""
    action = CardDrawAction("test_user", game_model)
    result = action.run()

    assert isinstance(result, GameModel)
    assert action.stage_meta == {"card": None, "drawn": False}


def test_card_draw_action_run_with_card_parameter(game_model):
    """Test CardDrawAction run with card parameter"""
    action = CardDrawAction("test_user", game_model)
    result = action.run(card="talisman")

    assert isinstance(result, GameModel)
    assert action.stage_meta == {"card": "talisman", "drawn": False}


def test_card_draw_action_run_with_drawn_parameter(game_model):
    """Test CardDrawAction run with drawn parameter"""
    action = CardDrawAction("test_user", game_model)
    result = action.run(drawn=True)

    assert isinstance(result, GameModel)
    assert action.stage_meta == {"card": None, "drawn": True}


def test_card_draw_action_run_with_both_parameters(game_model):
    """Test CardDrawAction run with both parameters"""
    action = CardDrawAction("test_user", game_model)
    result = action.run(card="golden_apple", drawn=True)

    assert isinstance(result, GameModel)
    assert action.stage_meta == {"card": "golden_apple", "drawn": True}


def test_card_draw_action_run_wrong_stage(game_model):
    """Test CardDrawAction run in wrong stage"""
    game_model.stage = "character_select"
    action = CardDrawAction("test_user", game_model)

    with pytest.raises(ReportedException, match="Invalid action. \\(wrong stage 'character_select'\\)"):
        action.run()


def test_card_select_action_run_success(game_model):
    """Test CardSelectAction run successfully"""
    action = CardSelectAction("test_user", game_model)
    result = action.run("talisman")

    assert isinstance(result, GameModel)
    assert "talisman" not in action.deck
    assert action.stage == "use_skill"
    assert action.stage_meta == {}


def test_card_select_action_run_card_not_in_deck(game_model):
    """Test CardSelectAction run with card not in deck"""
    action = CardSelectAction("test_user", game_model)

    with pytest.raises(ReportedException, match="Invalid action. \\(card 'invalid_card' not in deck\\)"):
        action.run("invalid_card")


def test_card_select_action_run_empty_deck_refill(game_model):
    """Test CardSelectAction run when deck becomes empty"""
    # Set deck to have only one card
    game_model.deck = ["talisman"]
    action = CardSelectAction("test_user", game_model)

    with patch("server.actions.card.shuffled_deck") as mock_shuffled_deck:
        mock_shuffled_deck.return_value = ["talisman", "golden_apple"]
        result = action.run("talisman")

        assert isinstance(result, GameModel)
        assert action.deck == ["talisman", "golden_apple"]
        assert action.stage == "use_skill"
        mock_shuffled_deck.assert_called_once()


def test_card_select_action_run_deck_not_empty_after_remove(game_model):
    """Test CardSelectAction run when deck still has cards after removal"""
    action = CardSelectAction("test_user", game_model)
    original_deck_length = len(action.deck)

    result = action.run("talisman")

    assert isinstance(result, GameModel)
    assert len(action.deck) == original_deck_length - 1
    assert "talisman" not in action.deck
    assert action.stage == "use_skill"


def test_card_select_action_run_wrong_stage(game_model):
    """Test CardSelectAction run in wrong stage"""
    game_model.stage = "character_select"
    action = CardSelectAction("test_user", game_model)

    with pytest.raises(ReportedException, match="Invalid action. \\(wrong stage 'character_select'\\)"):
        action.run("talisman")
