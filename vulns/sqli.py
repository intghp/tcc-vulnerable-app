"""
SQL Injection — Corrigido utilizando Consultas Parametrizadas (Parameterized Queries).
"""
from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import HTMLResponse

from core import get_conn, get_current_user, templates 

router = APIRouter(tags=["Consultas"])

@router.get("/inventario/buscar", response_class=HTMLResponse)
def buscar_inventario(
    request: Request, 
    termo: str = Query(""), 
    user: dict = Depends(get_current_user)
):
    conn = get_conn()
    query = "SELECT nome, valor, status FROM equipment WHERE nome LIKE ?"
    try:
        rows = conn.execute(query, (f"%{termo}%",)).fetchall()
    except Exception as e:
        conn.close()
        return HTMLResponse(f"Erro: {e}", status_code=400)
    conn.close()
    return templates.TemplateResponse(
        request,
        "inventory.html",
        {"colab": user, "termo": termo, "resultados": rows},
    )

@router.get("/relatorios/retiradas", response_class=HTMLResponse)
def relatorio_retiradas(
    request: Request, 
    nome: str = Query(""), 
    user: dict = Depends(get_current_user)
):
    conn = get_conn()
    query = (
        "SELECT r.id, r.equipamento, r.valor, r.data, u.nome "
        "FROM documents r JOIN users u ON u.id = r.user_id "
        "WHERE u.nome LIKE ? ORDER BY r.data"
    )
    try:
        rows = [dict(x) for x in conn.execute(query, (f"%{nome}%",)).fetchall()]
    except Exception as e:
        conn.close()
        return HTMLResponse(f"Erro: {e}", status_code=400)
    conn.close()
    return templates.TemplateResponse(
        request,
        "report.html",
        {"colab": user, "nome": nome, "resultados": rows},
    )