from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.trade import TradeDeclaration, RiskScore, Importer  # noqa: E402, F401
