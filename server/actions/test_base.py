import pytest

from .base import Action
from ..models import GameModel, PlayerModel, CharacterModel, GameException, ReportedException


class ConcreteAction(Action):
    """Concrete implementation of Action for testing purposes"""

    def run(self, *args, **kwargs) -> GameModel:
        return self.game


@pytest.fixture
def player_model():
    """Create a test player model"""
    characters = {"knight": CharacterModel(health=2, level=1, max_health=2, skills={}, dice=1, attack=1)}
    return PlayerModel(status="connected", cards=["talisman"], characters=characters)


@pytest.fixture
def game_model(player_model):
    """Create a test game model"""
    return GameModel(
        stage="character_select",
        stage_meta={"test": "data"},
        deck=["talisman", "golden_apple"],
        playing="test_user",
        selected_character="knight",
        players={"test_user": player_model},
    )


@pytest.fixture
def action(game_model):
    """Create a concrete action instance for testing"""
    return ConcreteAction("test_user", game_model)


def test_action_init(game_model):
    """Test Action initialization"""
    action = ConcreteAction("test_user", game_model)
    assert action.user == "test_user"
    assert action.game == game_model


def test_action_players_property(action):
    """Test players property"""
    assert action.players == action.game.players


def test_action_player_property_success(action):
    """Test player property when user exists"""
    player = action.player
    assert player.status == "connected"
    assert player.cards == ["talisman"]


def test_action_player_property_user_not_in_game(game_model):
    """Test player property when user not in game"""
    action = ConcreteAction("nonexistent_user", game_model)
    with pytest.raises(GameException, match="Player not in game"):
        _ = action.player


def test_action_stage_property_getter(action):
    """Test stage property getter"""
    assert action.stage == "character_select"


def test_action_stage_property_setter(action):
    """Test stage property setter"""
    action.stage = "card_draw"
    assert action.stage == "card_draw"
    assert action.game.stage == "card_draw"


def test_action_stage_meta_property_getter(action):
    """Test stage_meta property getter"""
    assert action.stage_meta == {"test": "data"}


def test_action_stage_meta_property_setter(action):
    """Test stage_meta property setter"""
    new_meta = {"new": "metadata"}
    action.stage_meta = new_meta
    assert action.stage_meta == new_meta
    assert action.game.stage_meta == new_meta


def test_action_selected_character_property_getter(action):
    """Test selected_character property getter"""
    assert action.selected_character == "knight"


def test_action_selected_character_property_setter(action):
    """Test selected_character property setter"""
    action.selected_character = "archer"
    assert action.selected_character == "archer"
    assert action.game.selected_character == "archer"


def test_action_deck_property_getter(action):
    """Test deck property getter"""
    assert action.deck == ["talisman", "golden_apple"]


def test_action_deck_property_setter(action):
    """Test deck property setter"""
    new_deck = ["talisman"]
    action.deck = new_deck
    assert action.deck == new_deck
    assert action.game.deck == new_deck


def test_action_assert_stage_success(action):
    """Test assert_stage when stage matches"""
    action.assert_stage("character_select")  # Should not raise


def test_action_assert_stage_failure(action):
    """Test assert_stage when stage doesn't match"""
    with pytest.raises(ReportedException, match="Invalid action. \\(wrong stage 'character_select'\\)"):
        action.assert_stage("card_draw")


def test_action_run_abstract_method(action):
    """Test that run method returns GameModel"""
    result = action.run()
    assert isinstance(result, GameModel)
    assert result == action.game
