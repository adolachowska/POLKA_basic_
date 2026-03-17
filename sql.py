import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey #(tworzenie bazy)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship #(relacje)
from dotenv import load_dotenv
# Connection String do Azure SQL (zmienne środowiskowe w produkcji!)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Brakuje DATABASE_URL w pliku .env!")

engine = create_engine(DATABASE_URL)
#silnik bazy sql
#nowa sesja dla każdego okienka
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#autocommit - automatyczny zapis, False 10 zmian session.commit()/session.rollback()
#autoflush - kiedy kod leci do bazy
#bind=engine - z jaką bazą danych się łączymy

Base = declarative_base() #baza matka, dziedziczenie

#tabela krajów
class CountryDB(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)

    years = relationship("YearDataDB", back_populates="country", cascade="all, delete-orphan")
    # info lista powiązań w YearDataDB", cascade = usunięcie wierszy danej wartości years z całej bazy

#atbela lat
class YearDataDB(Base):
    __tablename__ = "political_data"

    id = Column(Integer, primary_key=True, index=True) #id wpisu
    year = Column(Integer, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))

    country = relationship("CountryDB", back_populates="years")

    # Wskaźniki surowe
    press_free = Column(Float)
    freedom_index = Column(Float)
    gdp = Column(Float)
    absence_of_violence = Column(Float)
    civil_liberties = Column(Float)
    gov_stability = Column(Float)
    human_rights = Column(Float)
    electoral_integrity = Column(Float)
    system_index = Column(Float)

    # Wskaźniki wyliczane (p i lagi)
    p = Column(Float)
    p_lag_1 = Column(Float, nullable=True)
    p_lag_3 = Column(Float, nullable=True)
    p_trend = Column(Float, nullable=True)


# Tworzenie tabel
Base.metadata.create_all(bind=engine) #połączenie z Azune, tworzenie kolumn, komenda,