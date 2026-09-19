"""
Endpoints de debug expostos.
"""
import os
import platform
import sys
import traceback

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core import JWT_ALGORITHM, SECRET_KEY

router = APIRouter(prefix="/debug", tags=["Sistema"])


@router.get("/config")
def cfg():
    return {
        "secret_key": SECRET_KEY,
        "jwt_algorithm": JWT_ALGORITHM,
        "db_path": "sga.db",
        "db_user": "sga_app",
        "db_password": "Sg@2024#ValeAco",
    }


@router.get("/env")
def env():
    return dict(os.environ)


@router.get("/info")
def info():
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "cwd": os.getcwd(),
    }


@router.get("/erro")
def erro():
    try:
        1 / 0
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"erro": "internal_error", "traceback": traceback.format_exc()},
        )