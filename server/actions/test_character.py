import pytest
from unittest.mock import patch

from .character import CharacterSelectAction, CharacterSelectedAction
from ..models import GameModel, PlayerModel, CharacterModel, ReportedException


@pytest.fixture
def player_model():
    """Create a test player model"""
    characters = {
        "knight": CharacterModel(health=2, level=1, max_health=2, skills={}, dice=1, attack=1),
        "archer": CharacterModel(health=3, level=1, max_health=3, skills={}, dice=1),
    }
    return PlayerModel(status="connected", cards=["talisman"], characters=characters)


@pytest.fixture
def game_model(player_model):
    """Create a test game model with character_select stage"""
    return GameModel(
        stage="character_select",
        stage_meta={},
        deck=["talisman", "golden_apple"],
        playing="test_user",
        selected_character=None,
        players={"test_user": player_model},
    )


def test_character_select_action_run_without_character(game_model):
    """Test CharacterSelectAction run without character parameter"""
    action = CharacterSelectAction("test_user", game_model)
    result = action.run()

    assert isinstance(result, GameModel)
    assert action.stage_meta == {"selected": None}


def test_character_select_action_run_with_valid_character(game_model):
    """Test CharacterSelectAction run with valid character"""
    action = CharacterSelectAction("test_user", game_model)
    result = action.run(character="knight")

    assert isinstance(result, GameModel)
    assert action.stage_meta == {"selected": "knight"}


def test_character_select_action_run_with_invalid_character(game_model):
    """Test CharacterSelectAction run with character not owned by player"""
    action = CharacterSelectAction("test_user", game_model)

    with pytest.raises(ReportedException, match="Invalid action. \\(character not found\\)"):
        action.run(character="mage")


def test_character_select_action_run_wrong_stage(game_model):
    """Test CharacterSelectAction run in wrong stage"""
    game_model.stage = "card_draw"
    action = CharacterSelectAction("test_user", game_model)

    with pytest.raises(ReportedException, match="Invalid action. \\(wrong stage 'card_draw'\\)"):
        action.run()


def test_character_selected_action_run_with_valid_character(game_model):
    """Test CharacterSelectedAction run with valid character"""
    action = CharacterSelectedAction("test_user", game_model)

    with patch("random.choice") as mock_choice:
        mock_choice.return_value = "talisman"
        result = action.run("knight")

        assert isinstance(result, GameModel)
        assert action.selected_character == "knight"
        assert action.stage == "card_draw"
        assert action.stage_meta == {"card": "talisman", "drawn": False}
        mock_choice.assert_called_once_with(action.deck)


def test_character_selected_action_run_with_invalid_character(game_model):
    """Test CharacterSelectedAction run with character not owned by player"""
    action = CharacterSelectedAction("test_user", game_model)

    with pytest.raises(ReportedException, match="Invalid action. \\(character not found\\)"):
        action.run("mage")


def test_character_selected_action_run_wrong_stage(game_model):
    """Test CharacterSelectedAction run in wrong stage"""
    game_model.stage = "card_draw"
    action = CharacterSelectedAction("test_user", game_model)

    with pytest.raises(ReportedException, match="Invalid action. \\(wrong stage 'card_draw'\\)"):
        action.run("knight")


def test_character_selected_action_run_random_card_selection(game_model):
    """Test that CharacterSelectedAction randomly selects a card from deck"""
    action = CharacterSelectedAction("test_user", game_model)

    # Mock random.choice to return different cards in different calls
    with patch("random.choice") as mock_choice:
        mock_choice.return_value = "golden_apple"
        result = action.run("archer")

        assert action.stage_meta["card"] == "golden_apple"
        mock_choice.assert_called_once_with(["talisman", "golden_apple"])


def test_character_selected_action_run_stage_transition(game_model):
    """Test that CharacterSelectedAction properly transitions game state"""
    action = CharacterSelectedAction("test_user", game_model)

    # Verify initial state
    assert action.stage == "character_select"
    assert action.selected_character is None

    with patch("random.choice") as mock_choice:
        mock_choice.return_value = "talisman"
        result = action.run("knight")

        # Verify state after action
        assert action.stage == "card_draw"
        assert action.selected_character == "knight"
        assert action.stage_meta["drawn"] is False
