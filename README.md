# PittMC Whitelist API

A FastAPI webhook service for automatically whitelisting players on a Minecraft server.

## Features

- Supports both Java and Bedrock Edition players
- HTTP Basic Authentication for secure access
- RCON-based communication with Minecraft server
- Automatic handling of Java player whitelisting edge cases
- Configurable via environment variables

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The following environment variables are used to configure the API:

| Variable | Description | Default |
|----------|-------------|---------|
| `route` | API endpoint route | `/default_route` |
| `rcon_ip` | RCON server IP address | `localhost` |
| `rcon_port` | RCON server port | `25575` |
| `rcon_pass` | RCON password | `""` |
| `AUTH_USERNAME` | Basic auth username | None |
| `AUTH_PASSWORD` | Basic auth password | None |

## Usage

### Starting the server

```bash
python webhook.py
```

This will start the API server on `0.0.0.0:8000`.

### API Endpoints

#### POST `{route}`

Adds a player to the server whitelist.

**Request Body:**
```json
{
  "username": "playerName",
  "type": "java" // or "bedrock"
}
```

**Responses:**
- `200 OK`: Player was successfully added or was already whitelisted
- `401 Unauthorized`: Invalid authentication credentials
- `500 Internal Server Error`: Server error occurred

## How It Works

### Java Edition Players
The API uses a workaround process for Java players:
1. Ban the player to add them to the usercache
2. Pardon the player to remove the ban
3. Add the player to the whitelist

### Bedrock Edition Players
For Bedrock players, the API uses the `fwhitelist add` command directly.

## Deployment

For production deployment, consider using:
- A process manager like Supervisor or PM2
- A reverse proxy like Nginx or Caddy
- Setting up proper SSL/TLS encryption
