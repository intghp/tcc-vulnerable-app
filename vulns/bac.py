"""
Broken Access Control — IDOR + Role bypass.
"""
from fastapi import APIRouter, Header, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from core import get_conn, get_current_user, templates

router = APIRouter(tags=["Operação"])

@router.get("/recibo/{doc_id}", response_class=HTMLResponse)
def read_document(
    doc_id: int,
    request: Request,
    authorization: str | None = Header(None),
):
    get_current_user(request, authorization)

    conn = get_conn()
    r = conn.execute(
        """
        SELECT d.*, u.nome AS colaborador, u.matricula
        FROM documents d
        JOIN users u ON u.id = d.user_id
        WHERE d.id = ?
        """,
        (doc_id,),
    ).fetchone()
    conn.close()

    if not r:
        return HTMLResponse("Recibo não encontrado", status_code=404)

    return templates.TemplateResponse(
        request, "receipt.html", {"req": dict(r)}
    )

@router.get("/admin/painel", response_class=HTMLResponse)
def painel_admin(
    request: Request,
    authorization: str = Header(None),
):
    user = get_current_user(request, authorization)

    conn = get_conn()
    rows = conn.execute(
        """
        SELECT r.id, r.equipamento, r.valor, r.status, r.data,
               u.nome AS colaborador, u.matricula
        FROM documents r
        JOIN users u ON u.id = r.user_id
        ORDER BY r.data DESC
        """
    ).fetchall()
    conn.close()

    return templates.TemplateResponse(
        request,
        "admin.html",
        {"colab": user, "reqs": [dict(x) for x in rows]},
    )