import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
 
# ── Banco de dados ────────────────────────────────────────────────────────────
 
DB_FILE = "jogos.db"
 
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn
 
def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jogos (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                nome   TEXT NOT NULL,
                tipo   TEXT NOT NULL,
                nota   INTEGER NOT NULL,
                review TEXT NOT NULL
            )
        """)
        conn.commit()
 
init_db()
 
# ── App ───────────────────────────────────────────────────────────────────────
 
app = FastAPI(title="Game Library API")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ── Auth ──────────────────────────────────────────────────────────────────────
 
VALID_TOKEN = "550e8400-e29b-41d4-a716-446655440000"
 
# ── Modelos Pydantic ──────────────────────────────────────────────────────────
 
class LoginRequest(BaseModel):
    email: str
    password: str
 
class JogoBody(BaseModel):
    nome: str
    tipo: str
    nota: int
    review: str
 
# ── Endpoints ─────────────────────────────────────────────────────────────────
 
@app.post("/login", status_code=200)
def login(body: LoginRequest):
    if body.email == "usuario@esoft.com" and body.password == "Abc123":
        return {"token": VALID_TOKEN}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")
 
 
@app.get("/jogos", status_code=200)
def listar_jogos():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM jogos").fetchall()
    return [dict(r) for r in rows]
 
 
@app.get("/jogos/{id}", status_code=200)
def buscar_jogo(id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM jogos WHERE id = ?", (id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    return dict(row)
 
 
@app.post("/jogos", status_code=201)
def criar_jogo(body: JogoBody):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO jogos (nome, tipo, nota, review) VALUES (?, ?, ?, ?)",
            (body.nome, body.tipo, body.nota, body.review)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM jogos WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)
 
 
@app.put("/jogos/{id}", status_code=200)
def atualizar_jogo(id: int, body: JogoBody):
    with get_conn() as conn:
        exists = conn.execute("SELECT id FROM jogos WHERE id = ?", (id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Jogo não encontrado")
        conn.execute(
            "UPDATE jogos SET nome=?, tipo=?, nota=?, review=? WHERE id=?",
            (body.nome, body.tipo, body.nota, body.review, id)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM jogos WHERE id = ?", (id,)).fetchone()
    return dict(row)
 
 
@app.delete("/jogos/{id}", status_code=204)
def deletar_jogo(id: int):
    with get_conn() as conn:
        exists = conn.execute("SELECT id FROM jogos WHERE id = ?", (id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Jogo não encontrado")
        conn.execute("DELETE FROM jogos WHERE id = ?", (id,))
        conn.commit()
    return None

