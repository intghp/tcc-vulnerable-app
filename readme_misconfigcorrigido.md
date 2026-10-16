# Correções Misconfiguration 
# Alterações
`debug=False` no FastAPI.
Swagger/OpenAPI desabilitados em runtime (`/docs`, `/redoc`, `/openapi.json`).
CORS restrito por `SGA_ALLOWED_ORIGINS`.
Métodos e headers CORS reduzidos ao necessário.
Cookie `sga_token` com `HttpOnly` e `SameSite=Lax`; `Secure` é ativado quando `SGA_USE_HTTPS=true`.
Cabeçalhos `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` e `Cache-Control` adicionados.
HSTS é enviado quando `SGA_USE_HTTPS=true`, evitando anunciar HSTS em HTTP local.
Endpoints `/debug/*` removidos do registro da aplicação.
Chave JWT retirada do código-fonte e lida de `SGA_SECRET_KEY`.
Senha de banco removida do módulo de configuração.
# Execução
PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:SGA_SECRET_KEY="COLE_AQUI_A_CHAVE_GERADA"
$env:SGA_ALLOWED_ORIGINS="http://localhost:8000"
$env:SGA_USE_HTTPS="false"
```
PowerShell:
```powershell
$env:SGA_SECRET_KEY = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
$env:SGA_ALLOWED_ORIGINS = "http://localhost:8000"
$env:SGA_USE_HTTPS = "false"
python run.py
```
