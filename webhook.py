import os
import traceback
import asyncio
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from mcrcon import MCRcon
import uvicorn
from typing import Literal
from contextlib import asynccontextmanager

# Environment variables
route = os.getenv("route", "/default_route")
rcon_ip = os.getenv("rcon_ip")
rcon_port = int(os.getenv("rcon_port", 25575))
rcon_pass = os.getenv("rcon_pass")
auth_username = os.getenv("AUTH_USERNAME")
auth_password = os.getenv("AUTH_PASSWORD")

# FastAPI setup
app = FastAPI()
security = HTTPBasic()

# Pydantic model for request validation
class WhitelistRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=16)
    type: Literal["java", "bedrock"]

# Authentication
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == auth_username and credentials.password == auth_password:
        return credentials.username
    raise HTTPException(status_code=401, detail="Invalid credentials")

# RCON connection manager
@asynccontextmanager
async def get_rcon():
    mcr = MCRcon(rcon_ip, rcon_pass, port=rcon_port)
    try:
        await mcr.connect()
        yield mcr
    finally:
        await mcr.disconnect()

# RCON command execution
async def run_rcon_command(command: str):
    async with get_rcon() as mcr:
        resp = await mcr.command(command)
    return resp.lower()

# Java whitelist process
async def process_java_whitelist(username: str):
    commands = [
        f'ban {username} Temporary - whitelist in progress',
        f'pardon {username}',
        f'whitelist add {username}'
    ]
    for cmd in commands:
        resp = await run_rcon_command(cmd)
        await asyncio.sleep(1)
    return resp

# Routes
@app.get("/")
async def default_route():
    return JSONResponse({"status": "error", "response": "You must be lost!"}, status_code=404)

@app.post(route)
async def return_response(request: WhitelistRequest, username: str = Depends(verify_credentials)):
    print(f"Received request: {request}")

    username = request.username.replace(" ", "_") if request.type == "bedrock" else request.username

    try:
        if request.type == "java":
            resp = await process_java_whitelist(username)
        else:
            resp = await run_rcon_command(f'fwhitelist add {username}')

        print(f"Response: {resp}")

        if "already whitelisted" in resp:
            return JSONResponse({"status": "warning", "response": resp}, status_code=200)
        elif "added" in resp:
            return JSONResponse({"status": "success", "response": resp}, status_code=200)
        elif "does not exist" in resp:
            return JSONResponse({"status": "failed", "response": "Player does not exist. Please reply to this email so we can manually whitelist you."}, status_code=200)
        elif resp == "" and request.type == "bedrock":
            return JSONResponse({"status": "warning", "response": "Bedrock whitelist requests cannot be verified, but your request was processed. Please try joining the server. If it doesn't work, please reply to this email so we can manually whitelist you."}, status_code=200)
        else:
            return JSONResponse({"status": "error", "response": "An unexpected error occurred. We will manually whitelist you shortly."}, status_code=500)

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return JSONResponse({"status": "error", "response": "An unknown error occurred while processing the request. We will manually whitelist you shortly."}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=8000, workers=4)