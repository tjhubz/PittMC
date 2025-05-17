import os
import traceback
import asyncio
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from aiomcrcon import Client
import uvicorn
from typing import Literal

# Environment variables
route = os.getenv("route", "/default_route")
rcon_ip = os.getenv("rcon_ip", "localhost")
rcon_port = int(os.getenv("rcon_port", 25575))
rcon_pass = os.getenv("rcon_pass", "")
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

# Global RCON client
rcon_client = None
rcon_lock = asyncio.Lock()

async def get_rcon_client():
    global rcon_client
    if rcon_client is None:
        rcon_client = Client(rcon_ip, rcon_port, rcon_pass)
        await rcon_client.connect()
    return rcon_client

async def reset_rcon_client():
    global rcon_client
    if rcon_client:
        await rcon_client.close()
    rcon_client = None

# RCON command execution with retry
async def run_rcon_command(command: str, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with rcon_lock:
                client = await get_rcon_client()
                resp = await client.send_cmd(command)
                print(f"RCON command executed: {command}")
                print(f"Full RCON response: {resp}")
                
                if isinstance(resp, tuple):
                    return str(resp[0]).lower()
                elif isinstance(resp, str):
                    return resp.lower()
                elif isinstance(resp, int):
                    return str(resp)
                else:
                    print(f"Unexpected response type: {type(resp)}")
                    return str(resp)
        except Exception as e:
            print(f"Failed to execute RCON command (attempt {attempt + 1}): {e}")
            await reset_rcon_client()
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail="Failed to execute game server command")
            await asyncio.sleep(1)  # Wait before retrying

# Java whitelist process
async def process_java_whitelist(username: str):
    # Try adding to whitelist directly first
    initial_cmd = f'whitelist add {username}'
    initial_resp = await run_rcon_command(initial_cmd)
    await asyncio.sleep(1) # Give server a moment to process

    # If player added or already whitelisted, return
    if "added" in initial_resp or "already whitelisted" in initial_resp:
        return initial_resp
    
    # If the initial whitelist add failed (e.g. player not found because they're not in usercache.json)
    # then proceed with the ban/pardon workaround
    print(f"Initial whitelist add for {username} failed or did not confirm addition ('{initial_resp}'), attempting ban/pardon workaround.")
    commands = [
        f'ban {username} Temporary - whitelist in progress',
        f'pardon {username}',
        f'whitelist add {username}'
    ]
    resp = ""
    for cmd in commands:
        resp = await run_rcon_command(cmd)
        await asyncio.sleep(1)
    return resp

# Routes
@app.get("/")
async def default_route():
    return JSONResponse({"status": "error", "response": "You must be lost!"}, status_code=404)

@app.post(route)
async def return_response(request: WhitelistRequest, auth_user: str = Depends(verify_credentials)):
    print(f"Received request: {request}")

    username = request.username.replace(" ", "_") if request.type == "bedrock" else request.username

    try:
        if request.type == "java":
            resp = await process_java_whitelist(username)
        else:
            resp = await run_rcon_command(f'fwhitelist add {username}')

        print(f"Final Response: {resp}")

        if "already whitelisted" in resp:
            return JSONResponse({"status": "warning", "response": resp}, status_code=200)
        elif "added" in resp:
            return JSONResponse({"status": "success", "response": resp}, status_code=200)
        elif "does not exist" in resp:
            return JSONResponse({"status": "failed", "response": "Player does not exist. Please reply to this email so we can manually whitelist you."}, status_code=200)
        elif resp == "" and request.type == "bedrock":
            return JSONResponse({"status": "warning", "response": "Bedrock whitelist requests cannot be verified, but your request was processed. Please try joining the server. If it doesn't work, please reply to this email so we can manually whitelist you."}, status_code=200)
        else:
            return JSONResponse({"status": "success", "response": f"Whitelist process completed: {resp}"}, status_code=200)

    except HTTPException as he:
        return JSONResponse({"status": "error", "response": he.detail}, status_code=he.status_code)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return JSONResponse({"status": "error", "response": "An unknown error occurred while processing the request. We will manually whitelist you shortly."}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=8000)