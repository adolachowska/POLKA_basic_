from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from pydantic import BaseModel
import csv
from io import StringIO
import numpy as np
import pandas as pd

#importy
from sql import SessionLocal, CountryDB, YearDataDB
from blob_service import upload_file_to_blob

app = FastAPI(title="POLKA – Political System Forecast API (Azure SQL Edition)")

# sesja bazy danych (otwrcie i zamknięcie)
def get_db():
    db = SessionLocal() #import sql
    try:
        yield db #wejście do biblioteki
    finally:
        db.close()


#pydantic Models
class PoliticalIndicators(BaseModel):
    press_free: float
    freedom_index: float
    gdp: float
    absence_of_violence: float
    civil_liberties: float
    gov_stability: float
    human_rights: float
    electoral_integrity: float
    system_index: float


class YearCreate(BaseModel):
    year: int
    indicators: PoliticalIndicators


class CountryCreate(BaseModel):
    name: str


# funkcje przeliczanie

def recalculate_metrics(db: Session, country_id: int):

    #dane - sesja - sql i pansa - liczy p/t - sql aktualizacja

    # dane z bazy do DataFrame, sprawdzanie rekordów bazy
    #querry - SELECT * FROM year_data ... gdzie country_id jest jak country_id
    records = db.query(YearDataDB).filter(YearDataDB.country_id == country_id).all()
    if not records:
        return

# konwersja SQL na listę słowników
    data_list = []
    for r in records:
        current_dict = {
            "id": r.id,
            "year": r.year,
            "p": r.p
        }

        data_list.append(current_dict)

    df = pd.DataFrame(data_list).sort_values("year")

#pandas
    df["p_lag_1"] = df["p"].shift(1)
    df["p_lag_3"] = df["p"].shift(3)

    if len(df) >= 5:
        df["p_trend"] = df["p"].rolling(5).apply(lambda x: x.iloc[-1] - x.iloc[0])
    else:
        df["p_trend"] = np.nan

#update
    df = df.replace({np.nan: None}) #zamiana na None w SQL

    for _, row in df.iterrows():
        db_record = next(r for r in records if r.id == row["id"])

        db_record.p_lag_1 = row["p_lag_1"]
        db_record.p_lag_3 = row["p_lag_3"]
        db_record.p_trend = row["p_trend"]

    db.commit()


def compute_p(indicators: PoliticalIndicators) -> float:
    values = [
        indicators.press_free, indicators.freedom_index,
        indicators.gdp, indicators.absence_of_violence, indicators.gov_stability,
        indicators.human_rights, indicators.civil_liberties,
    ]
    return float(np.mean(values))

# endpointy

#dodaj kraj
@app.post("/countries")
def create_country(payload: CountryCreate, db: Session = Depends(get_db)):
    existing = db.query(CountryDB).filter(CountryDB.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Country already exists")

    new_country = CountryDB(name=payload.name)
    db.add(new_country)
    db.commit()
    return {"status": "created", "country": payload.name}

#dodaj rok
@app.post("/countries/{name}/year")
def add_year(name: str, payload: YearCreate, db: Session = Depends(get_db)):
    country = db.query(CountryDB).filter(CountryDB.name == name).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    #czy rok już istnieje
    exists = db.query(YearDataDB).filter_by(country_id=country.id, year=payload.year).first()
    if exists:
        raise HTTPException(status_code=400, detail="Year already exists")


    #  nowy rekord do SQL
    new_data = YearDataDB(
        country_id=country.id,
        year=payload.year,
        **payload.indicators.dict(),  # Rozpakowanie wskaźników
        p=compute_p(payload.indicators)
        # p_lag i trend są na razie Null, policzymy je za chwilę
    )
    db.add(new_data)
    db.commit()

    # Przelicz wskaźniki historyczne (Features Engineering)
    recalculate_metrics(db, country.id)

    return {"status": "year added", "year": payload.year}

#data kraj
@app.get("/countries/{name}")
def get_country_data(name: str, db: Session = Depends(get_db)):
    country = db.query(CountryDB).filter(CountryDB.name == name).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    #sortowanie po roku
    data = db.query(YearDataDB).filter_by(country_id=country.id).order_by(YearDataDB.year).all()
    return data


@app.post("/countries/{name}/upload-csv")
async def upload_csv(name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    country = db.query(CountryDB).filter(CountryDB.name == name).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Not CSV file")

    #zapis do Azure Blob Storage
    file_content = await file.read()
    blob_url = await run_in_threadpool(upload_file_to_blob, file_content, file.filename)

    #bajty tekst
    csv_text = file_content.decode("utf-8")
    reader = csv.DictReader(StringIO(csv_text))

    years_added = 0

    # sprawdzenie kolumn
    required_columns = {"year", "press_free", "freedom_index", "gdp", "absence_of_violence",
                        "electoral_integrity","civil_liberties",
                        "gov_stability", "human_rights", "electoral_integrity", "system_index"}

    for col in required_columns:
        if col not in reader.fieldnames:
            raise HTTPException(status_code=400, detail=f"Missing column: {col}")


    for row in reader:
        # spr błędów bez zamykania kodu
        try:
            indicators = PoliticalIndicators(
                press_free=float(row["press_free"]),
                freedom_index=float(row["freedom_index"]),
                gdp=float(row["gdp"]),
                absence_of_violence=float(row["absence_of_violence"]),
                civil_liberties=float(row["civil_liberties"]),
                gov_stability=float(row["gov_stability"]),
                human_rights=float(row["human_rights"]),
                electoral_integrity=float(row["electoral_integrity"]),
                system_index=float(row["system_index"]),
            )
            year_val = int(row["year"])

            if not db.query(YearDataDB).filter_by(country_id=country.id, year=year_val).first():
                new_row = YearDataDB(
                    country_id=country.id,
                    year=year_val,
                    **indicators.model_dump(),
                    p=compute_p(indicators)
                )
                db.add(new_row)
                years_added += 1

        except ValueError as e:
            print(f"Skipping row due to error: {e}")
            continue

    db.commit()

    #lag compute
    if years_added > 0:
        recalculate_metrics(db, country.id)

    return {
        "status": "csv uploaded and processed",
        "rows_added": years_added,
        "backup_url": blob_url  # Zwracamy link do backupu w Blob Storage
    }