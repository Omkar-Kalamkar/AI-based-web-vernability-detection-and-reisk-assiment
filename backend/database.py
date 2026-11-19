from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config

connect_args = {"check_same_thread": False} if Config.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(Config.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    from models.user import User  # noqa: F401
    from models.session import AuthSession  # noqa: F401
    from models.scan import Scan  # noqa: F401
    from models.vulnerability import Vulnerability  # noqa: F401
    from models.setting import UserSetting  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
