from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./foodtopia.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# 這段其實看不太懂，只知道是用來產生 session 的，然後在 router 裡面用 Depends(get_session) 來取得 session
# 而 session 是用來跟資料庫互動的，像是新增、查詢、更新、刪除資料等等 來避免 overload   
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
