#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def convert_mcp_json_to_commands(mcp_json_path="mcp.json"):
    """
    Convert mcp.json configuration to Claude MCP add-json commands
    """
    try:
        with open(mcp_json_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: {mcp_json_path} not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    if "mcpServers" not in config:
        print("Error: No mcpServers found in configuration")
        return

    commands = []

    for server_name, server_config in config["mcpServers"].items():
        # Create the JSON string for the server configuration
        server_json = json.dumps(server_config, separators=(",", ":"))

        # Create claude mcp add-json command
        command = f"claude mcp add-json {server_name} '{server_json}'"
        commands.append(command)

    return commands


def main():
    if len(sys.argv) > 1:
        mcp_json_path = sys.argv[1]
    else:
        mcp_json_path = Path(__file__).parent / "mcp-tools.json"

    commands = convert_mcp_json_to_commands(mcp_json_path)

    if commands:
        # print("# Claude MCP installation commands:")
        # print("# Generated from", mcp_json_path)
        # print()
        for command in commands:
            print(command)
    else:
        print("No commands generated")


if __name__ == "__main__":
    main()
