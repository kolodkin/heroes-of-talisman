"""
Tests for the main API endpoints using FastAPI TestClient.

Tests the following endpoints:
- GET /api/games/ - Get list of games
- POST /api/games/ - Add a new game
- DELETE /api/games/{gamename} - Delete a game
- POST /check-game-name - Check if game name is unique

Uses PostgreSQL test database configured in conftest.py
"""


def test_get_games_empty(client):
    """Test getting games when no games exist"""
    response = client.get("/api/games/")
    assert response.status_code == 200
    assert response.json() == []


def test_add_game(client, gamename):
    """Test adding a new game"""
    game_data = {"name": gamename}
    response = client.post("/api/games/", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Game added successfully"}


def test_add_game_empty_name(client):
    """Test adding a game with empty name"""
    game_data = {"name": ""}
    response = client.post("/api/games/", json=game_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Game name cannot be empty"}


def test_add_game_duplicate(client, gamename):
    """Test adding a game with duplicate name"""
    game_data = {"name": gamename}

    # Add first game
    response = client.post("/api/games/", json=game_data)
    assert response.status_code == 200

    # Try to add duplicate
    response = client.post("/api/games/", json=game_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Game already exists"}


def test_get_games_with_data(client, gamename):
    """Test getting games when games exist"""
    # Add some games
    games = [f"{gamename}-1", f"{gamename}-2", f"{gamename}-3"]
    for game_name in games:
        client.post("/api/games/", json={"name": game_name})

    response = client.get("/api/games/")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 3
    assert set(result) == set(games)


def test_delete_game(client, gamename):
    """Test deleting an existing game"""
    # Add a game first
    client.post("/api/games/", json={"name": gamename})

    # Delete the game
    response = client.delete(f"/api/games/{gamename}")
    assert response.status_code == 200
    assert response.json() == {"message": "Game deleted successfully"}

    # Verify game is deleted
    response = client.get("/api/games/")
    assert response.status_code == 200
    assert gamename not in response.json()


def test_delete_nonexistent_game(client):
    """Test deleting a game that doesn't exist"""
    response = client.delete("/api/games/nonexistent_game")
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_check_game_name_unique(client):
    """Test checking if a game name is unique"""
    game_data = {"name": "unique_game"}
    response = client.post("/check-game-name", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"isUnique": True}


def test_check_game_name_not_unique(client, gamename):
    """Test checking if a game name is not unique"""
    # Add a game first
    client.post("/api/games/", json={"name": gamename})

    # Check if name is unique
    response = client.post("/check-game-name", json={"name": gamename})
    assert response.status_code == 200
    assert response.json() == {"isUnique": False}


def test_add_preset_game_default(client, gamename):
    """Test adding a preset game with default preset"""
    game_data = {"name": gamename, "preset": "default"}
    response = client.post("/api/games/preset_games", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Preset game added successfully"}

    # Verify game exists
    response = client.get("/api/games/")
    assert gamename in response.json()


def test_add_preset_game_health_1(client, gamename):
    """Test adding a preset game with health_1 preset"""
    game_data = {"name": gamename, "preset": "health_1"}
    response = client.post("/api/games/preset_games", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Preset game added successfully"}

    # Verify game exists
    response = client.get("/api/games/")
    assert gamename in response.json()


def test_add_preset_game_with_stage(client, gamename):
    """Test adding a preset game with specific stage"""
    game_data = {"name": gamename, "preset": "health_1", "stage": "battle_dice_roll"}
    response = client.post("/api/games/preset_games", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Preset game added successfully"}

    # Verify game exists
    response = client.get("/api/games/")
    assert gamename in response.json()


def test_add_preset_game_empty_name(client):
    """Test adding a preset game with empty name"""
    game_data = {"name": "", "preset": "default"}
    response = client.post("/api/games/preset_games", json=game_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Game name cannot be empty"}


def test_add_preset_game_duplicate(client, gamename):
    """Test adding a preset game with duplicate name"""
    game_data = {"name": gamename, "preset": "default"}

    # Add first game
    response = client.post("/api/games/preset_games", json=game_data)
    assert response.status_code == 200

    # Try to add duplicate
    response = client.post("/api/games/preset_games", json=game_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Game already exists"}
