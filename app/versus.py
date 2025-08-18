from __future__ import annotations
import asyncio
import json
import uuid
import time
import secrets
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from .generator import generate_puzzle
from .checker import check_expression

router = APIRouter()

def normalize_mode(mode: str) -> str:
    return "coop" if str(mode).lower() == "coop" else "versus"

def room_key(room: str, mode: str) -> str:
    return f"{mode}:{room}"

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + password).encode("utf-8")).hexdigest()

@dataclass
class Room:
    id: str                                     # human room id (without mode)
    mode: str = "versus"                        # 'versus' | 'coop'
    password_salt: Optional[str] = None
    password_hash: Optional[str] = None

    clients: Dict[str, WebSocket] = field(default_factory=dict)   # playerId -> socket
    names: Dict[str, str] = field(default_factory=dict)           # playerId -> display name
    scores: Dict[str, int] = field(default_factory=dict)          # playerId -> score (versus)
    nums: List[int] = field(default_factory=list)                 # current round cards
    round_active: bool = False
    round_id: str = ""
    # Co-op stats
    coop_correct: int = 0
    coop_round_started_at_ms: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

# Keyed by "{mode}:{room}"
ROOMS: Dict[str, Room] = {}

@dataclass
class JoinToken:
    token: str
    room_key: str
    name: str
    issued_at_ms: int
    ttl_ms: int = 2 * 60 * 60 * 1000  # 2 hours

    def expired(self) -> bool:
        return (time.time() * 1000) > (self.issued_at_ms + self.ttl_ms)

# token -> JoinToken
TOKENS: Dict[str, JoinToken] = {}

async def send_to_room(room: Room, payload: dict):
    msg = json.dumps(payload)
    dead: List[str] = []
    for pid, ws in list(room.clients.items()):
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(pid)
    for pid in dead:
        room.clients.pop(pid, None)
        room.names.pop(pid, None)
        room.scores.pop(pid, None)

def room_players_payload(room: Room):
    return [
        {"id": pid, "name": room.names.get(pid, f"Player {pid[:4]}"), "score": room.scores.get(pid, 0)}
        for pid in room.clients.keys()
    ]

async def start_round(room: Room):
    room.nums = generate_puzzle()
    room.round_active = True
    room.round_id = uuid.uuid4().hex
    if room.mode == "coop":
        room.coop_round_started_at_ms = int(time.time() * 1000)

    await send_to_room(room, {
        "type": "state",
        "roomId": room.id,
        "mode": room.mode,
        "players": room_players_payload(room),
        "roundId": room.round_id,
        **({"teamCorrect": room.coop_correct} if room.mode == "coop" else {}),
    })
    await send_to_room(room, {
        "type": "puzzle",
        "roomId": room.id,
        "mode": room.mode,
        "nums": room.nums,
        "roundId": room.round_id,
        "message": "New round started",
        **({"startedAt": room.coop_round_started_at_ms} if room.mode == "coop" else {}),
    })

async def next_round_soon(room: Room, delay: float = 1.0):
    await asyncio.sleep(delay)
    async with room.lock:
        await start_round(room)

# --------- REST API: create room and request join token ---------

class CreateRoomReq(BaseModel):
    room: str
    mode: str = "versus"
    password: str

class CreateRoomRes(BaseModel):
    roomId: str
    mode: str

@router.post("/rooms", response_model=CreateRoomRes)
async def create_room(body: CreateRoomReq):
    room = body.room.strip()
    mode = normalize_mode(body.mode)
    if not room:
        raise HTTPException(HTTP_400_BAD_REQUEST, "Room ID required.")
    if not body.password:
        raise HTTPException(HTTP_400_BAD_REQUEST, "Password must be used.")
    key = room_key(room, mode)
    if key in ROOMS:
        raise HTTPException(HTTP_400_BAD_REQUEST, "Room already exists.")
    salt = secrets.token_hex(16)
    r = Room(id=room, mode=mode, password_salt=salt, password_hash=hash_password(body.password, salt))
    ROOMS[key] = r
    return CreateRoomRes(roomId=room, mode=mode)

class JoinRoomReq(BaseModel):
    room: str
    mode: str = "versus"
    password: str
    name: str

class JoinRoomRes(BaseModel):
    token: str
    roomId: str
    mode: str
    name: str

@router.post("/rooms/join", response_model=JoinRoomRes)
async def join_room(body: JoinRoomReq):
    room = body.room.strip()
    mode = normalize_mode(body.mode)
    key = room_key(room, mode)
    r = ROOMS.get(key)
    if r is None:
        raise HTTPException(HTTP_404_NOT_FOUND, "Room not found.")
    if not r.password_hash or not r.password_salt:
        raise HTTPException(HTTP_400_BAD_REQUEST, "Room misconfigured.")
    if hash_password(body.password, r.password_salt) != r.password_hash:
        raise HTTPException(HTTP_403_FORBIDDEN, "Invalid password.")

    token = secrets.token_urlsafe(24)
    name = (body.name or "").strip()[:24] or "Player"
    TOKENS[token] = JoinToken(token=token, room_key=key, name=name, issued_at_ms=int(time.time() * 1000))
    return JoinRoomRes(token=token, roomId=room, mode=mode, name=name)

# --------- WebSocket: connect using token ---------

@router.websocket("/ws")
async def ws_room(
    websocket: WebSocket,
    token: Optional[str] = None,
    room: Optional[str] = None,
    name: Optional[str] = None,
    mode: str = "versus",
):
    await websocket.accept()

    # Require token 
    if not token:
        await websocket.close(code=4403)  # forbidden
        return

    jt = TOKENS.get(token)
    if jt is None or jt.expired():
        await websocket.close(code=4403)
        return

    resolved_room_key = jt.room_key
    resolved_name = jt.name

    r = ROOMS.get(resolved_room_key)
    if r is None:
        await websocket.close(code=4404)  # room not found
        return

    player_id = uuid.uuid4().hex

    async with r.lock:
        r.clients[player_id] = websocket
        r.names[player_id] = resolved_name
        r.scores.setdefault(player_id, 0)

        await send_to_room(r, {
            "type": "state",
            "roomId": r.id,
            "mode": r.mode,
            "players": room_players_payload(r),
            "roundId": r.round_id,
            **({"teamCorrect": r.coop_correct} if r.mode == "coop" else {}),
        })

        if not r.round_active or not r.nums:
            await start_round(r)
        else:
            try:
                await websocket.send_text(json.dumps({
                    "type": "puzzle",
                    "roomId": r.id,
                    "mode": r.mode,
                    "nums": r.nums,
                    "roundId": r.round_id,
                    "message": "Joined in-progress round",
                    **({"startedAt": r.coop_round_started_at_ms} if r.mode == "coop" else {}),
                }))
            except Exception:
                pass

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if not isinstance(msg, dict):
                continue

            if msg.get("type") == "attempt":
                expr = str(msg.get("expression", ""))[:256]
                async with r.lock:
                    if not r.round_active:
                        try:
                            await websocket.send_text(json.dumps({
                                "type": "attemptResult",
                                "ok": False,
                                "message": "Round already solved. Wait for the next round.",
                            }))
                        except Exception:
                            pass
                        continue

                    nums_copy = list(r.nums)
                    try:
                        ok, message = check_expression(nums_copy, expr)
                    except Exception:
                        ok, message = False, "Error checking expression."

                    try:
                        await websocket.send_text(json.dumps({
                            "type": "attemptResult",
                            "ok": ok,
                            "message": message,
                        }))
                    except Exception:
                        pass

                    if ok:
                        r.round_active = False
                        solved_msg = ""
                        if r.mode == "versus":
                            r.scores[player_id] = r.scores.get(player_id, 0) + 1
                            solved_msg = f"{r.names[player_id]} got it first!"
                        else:  # coop
                            r.coop_correct += 1
                            solved_msg = f"{r.names[player_id]} solved it for the team!"

                        await send_to_room(r, {
                            "type": "solved",
                            "roomId": r.id,
                            "mode": r.mode,
                            "roundId": r.round_id,
                            "by": {"id": player_id, "name": r.names[player_id]},
                            "expression": expr,
                            "nums": r.nums,
                            "players": room_players_payload(r),
                            "message": solved_msg,
                            **({"teamCorrect": r.coop_correct} if r.mode == "coop" else {}),
                        })
                        asyncio.create_task(next_round_soon(r))
    except WebSocketDisconnect:
        pass
    finally:
        try:
            async with r.lock:
                r.clients.pop(player_id, None)
                await send_to_room(r, {
                    "type": "state",
                    "roomId": r.id,
                    "mode": r.mode,
                    "players": room_players_payload(r),
                    "roundId": r.round_id,
                    **({"teamCorrect": r.coop_correct} if r.mode == "coop" else {}),
                })
                if not r.clients:
                    ROOMS.pop(room_key(r.id, r.mode), None)
        except Exception:
            pass