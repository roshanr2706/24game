# app/main.py
# python -m uvicorn app.main:app --reload
from typing import Annotated, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .solver import solve24
from .checker import check_expression
from .generator import generate_puzzle
from .versus import router as versus_router

app = FastAPI(title="24 Game API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://roshanr2706.github.io"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Nums = Annotated[list[int], Field(min_length=4, max_length=4)]

class Puzzle(BaseModel):
    nums: Nums

class Attempt(Puzzle):
    expression: str

@app.get("/puzzle")
def new_puzzle():
    nums = generate_puzzle()
    # Don’t leak the solution here; the client can call /check or /solve if you want hints.
    return {"nums": nums}

@app.post("/solve")
def solve_endpoint(p: Puzzle):
    expr = solve24(p.nums)
    return {"solvable": expr is not None, "expression": expr}

@app.post("/check")
def check_endpoint(a: Attempt):
    ok, msg = check_expression(a.nums, a.expression)
    return {"ok": ok, "message": msg}

app.include_router(versus_router)
