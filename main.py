from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite:///./jogos.db"  
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

origins = "web-production-f551c.up.railway.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],           
    allow_headers=["*"],          
)

class Base(DeclarativeBase):  
    pass

class JogoDB(Base):
    __tablename__ = "jogos"
    id     = Column(Integer, primary_key=True, index=True)
    nome   = Column(String,  nullable=False)
    tipo   = Column(String,  nullable=False)
    nota   = Column(Integer, nullable=False)
    review = Column(String,  nullable=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Game Library API")

VALID_TOKEN = "550e8400-e29b-41d4-a716-446655440000"

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in ("/login"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header[7:] != VALID_TOKEN:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=401, content={"detail": "Token inválido ou ausente"})

    return await call_next(request)

class LoginRequest(BaseModel):
    email: str
    password: str

class JogoBody(BaseModel):
    nome: str
    tipo: str
    nota: int
    review: str

@app.post("/login", status_code=200)
def login(body: LoginRequest):
    if body.email == "usuario@esoft.com" and body.password == "Abc123":
        return {"token": VALID_TOKEN}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.get("/jogos", status_code=200)
def listar_jogos(db: Session = Depends(get_db)):
    return db.query(JogoDB).all()

@app.get("/jogos/{id}", status_code=200)
def buscar_jogo(id: int, db: Session = Depends(get_db)):
    jogo = db.get(JogoDB, id)
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    return jogo

@app.post("/jogos", status_code=201)
def criar_jogo(body: JogoBody, db: Session = Depends(get_db)):
    novo = JogoDB(**body.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@app.put("/jogos/{id}", status_code=200)
def atualizar_jogo(id: int, body: JogoBody, db: Session = Depends(get_db)):
    jogo = db.get(JogoDB, id)
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    for campo, valor in body.model_dump().items():
        setattr(jogo, campo, valor)
    db.commit()
    db.refresh(jogo)
    return jogo

@app.delete("/jogos/{id}", status_code=204)
def deletar_jogo(id: int, db: Session = Depends(get_db)):
    jogo = db.get(JogoDB, id)
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    db.delete(jogo)
    db.commit()
    return None


