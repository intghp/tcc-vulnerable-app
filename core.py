"""
Banco, sessão e templates compartilhados.
"""
import base64
import hashlib
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import jwt
from fastapi import Header, HTTPException, Request
from fastapi.templating import Jinja2Templates

SECRET_KEY = "sga-mva-2024-Xy9kLmPqR7sT3uVwZ5yN8cD2fG6hJ1kL"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MIN = 60 * 24 * 30
DB_PATH = Path("sga.db")

templates = Jinja2Templates(directory="templates")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _hash(pw: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 100_000)
    return base64.b64encode(salt + key).decode()


def verify_password(plain: str, stored: str) -> bool:
    try:
        raw = base64.b64decode(stored)
        salt, key = raw[:16], raw[16:]
        return hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 100_000) == key
    except Exception:
        return False


def init_db() -> None:
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'colaborador'
        );
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            equipamento TEXT NOT NULL,
            valor REAL DEFAULT 0,
            status TEXT DEFAULT 'ativo',
            data TEXT
        );
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL DEFAULT 0,
            status TEXT DEFAULT 'disponível'
        );
        """
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO users (matricula, nome, senha, role) VALUES (?, ?, ?, ?)",
            [
                ("COL-001", "Carlos Andrade", _hash("col001"), "admin"),
                ("COL-002", "João Pereira",   _hash("col002"), "colaborador"),
                ("COL-003", "Maria Souza",    _hash("col003"), "colaborador"),
            ],
        )
        cur.executemany(
            "INSERT INTO documents (user_id, equipamento, valor, status, data) "
            "VALUES (?, ?, ?, ?, ?)",
            [
                (2, "Notebook Dell 5420", 4500.00, "ativo",         "2024-03-10"),
                (2, "Monitor LG 24''",     890.00, "devolvido",     "2024-03-12"),
                (3, "Projetor Epson",     3200.00, "ativo",         "2024-03-14"),
                (3, "Furadeira Bosch",     720.00, "em manutenção", "2024-03-15"),
            ],
        )
        cur.executemany(
            "INSERT INTO equipment (nome, valor, status) VALUES (?, ?, ?)",
            [
                ("Notebook Dell 5420", 4500.00, "em uso"),
                ("Monitor LG 24''",     890.00, "disponível"),
                ("Furadeira Bosch",     720.00, "em uso"),
                ("Projetor Epson",     3200.00, "disponível"),
            ],
        )
        conn.commit()
    conn.close()

def get_user_by_matricula(mat: str):
    conn = get_conn()
    r = conn.execute("SELECT * FROM users WHERE matricula = ?", (mat,)).fetchone()
    conn.close()
    return dict(r) if r else None


def get_user_by_id(uid: int):
    conn = get_conn()
    r = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()
    return dict(r) if r else None

def create_token(user_id: int, matricula: str, nome: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "matricula": matricula,
        "nome": nome,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MIN),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(request: Request) -> dict:
    token = request.cookies.get("sga_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user = get_user_by_id(int(payload["sub"]))
        if not user:
            raise HTTPException(401, "Unauthorized")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def current_user_optional(request: Request) -> dict | None:
    token = request.cookies.get("sga_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return get_user_by_id(int(payload["sub"]))
    except Exception:
        return None