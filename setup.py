from azure.storage.blob import BlobServiceClient #kom azurite
import pyodbc #kom sql

# 1. Kontener - tworzenie kontenera dl csv
try:
    svc = BlobServiceClient.from_connection_string("UseDevelopmentStorage=true") #UseDevelopmentStorage=true lokalna sieć
    #możliwość kom z obsługa klienta aka service
    svc.create_container("raw-csv-uploads") #kontener na csv
    print("✅ Kontener utworzony.")
except Exception:
    print("✅ Kontener już istnieje.")

# 2. Baza Danych (SQL Server)
#Tworzy relacyjną bazę danych: Druga część kodu (od pyodbc) łączy się z Twoim lokalnym serwerem SQL i upewnia się, że istnieje tam pusta baza danych o nazwie polka_db.#
try:
    # Konfiguracja połączenia z serwerem:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'   # Używamy sterownika ODBC 18 (tego, który instalowałaś)
        'SERVER=localhost\\SQLEXPRESS;'             # Adres Twojego serwera na dysku
        'DATABASE=master;'                          # Ważne! Łączymy się z bazą systemową 'master' ("główna dyrekcja"), bo polka_db może jeszcze nie istnieć
        'Trusted_Connection=yes;'                   # Logujemy się Twoim kontem Windows (bez hasła)
        'TrustServerCertificate=yes;',              # Ufamy lokalnemu certyfikatowi
        autocommit=True                             # Mówimy bazie: "Każde polecenie wykonuj natychmiast". Wymagane przy tworzeniu nowej bazy.
    )

    # cursor() -> Tworzymy "kursor" (wirtualne pióro w ręku Pythona)
    # execute() -> Pióro pisze polecenie SQL i wysyła je do serwera
    # Treść SQL: Sprawdź w spisie (sys.databases) czy jest 'polka_db'. JEŚLI NIE MA -> STWÓRZ JĄ.
    conn.cursor().execute("IF NOT EXISTS(SELECT * FROM sys.databases WHERE name='polka_db') CREATE DATABASE polka_db")

    print("✅ Baza SQL utworzona (lub już istniała).")
    conn.close() # Zamykamy połączenie z master, bo zrobiliśmy swoje

except Exception as e:
    print(f"⚠️ Info o bazie: {e}")

    #http://127.0.0.1:8000/docs
    #python -m uvicorn main:app --reload

#