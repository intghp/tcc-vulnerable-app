from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from core import (
    create_token,
    current_user_optional,
    get_conn,
    get_user_by_matricula,
    init_db,
    templates,
    verify_password,
)
from vulns import bac, misconfig, sqli


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="SGA · Sistema de Gestão de Almoxarifado",
    version="2.4.1",
    debug=True,
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bac.router)
app.include_router(sqli.router)
app.include_router(misconfig.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/login")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@app.post("/login")
def login_submit(
    request: Request,
    matricula: str = Form(...),
    senha: str = Form(...),
):
    user = get_user_by_matricula(matricula)
    if not user or not verify_password(senha, user["senha"]):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"erro": "Matrícula ou senha inválidos"},
            status_code=401,
        )

    token = create_token(user["id"], user["matricula"], user["nome"], user["role"])
    resp = RedirectResponse("/dashboard", status_code=302)
    resp.set_cookie("sga_token", token)
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("sga_token")
    return resp


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = current_user_optional(request)
    if not user:
        return RedirectResponse("/login")

    conn = get_conn()
    row = conn.execute(
        "SELECT MIN(id) AS meu_recibo FROM documents WHERE user_id = ?",
        (user["id"],),
    ).fetchone()
    conn.close()

    meu_recibo_id = row["meu_recibo"] if row and row["meu_recibo"] else None

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"colab": user, "meu_recibo_id": meu_recibo_id},
    )