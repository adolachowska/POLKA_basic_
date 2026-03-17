import os  # System operacyjny - pozwala czytać zmienne środowiskowe (np. klucze)
from azure.storage.blob import BlobServiceClient  # Główny "klient" do gadania z magazynem plików
import uuid  # Biblioteka do generowania losowych, unikalnych numerów (np. a1b2-c3d4...)
from dotenv import load_dotenv  # Biblioteka, która czyta plik .env

# 1. Ładowanie konfiguracji
load_dotenv()  # Szuka pliku .env i ładuje go do pamięci komputera

# Pobieramy tajny klucz połączenia z .env
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "raw-csv-uploads"  # Nazwa "folderu" w chmurze, gdzie wrzucamy pliki

# Bezpiecznik: Jeśli zapomniałaś wpisać klucza w .env, program tutaj krzyknie i się zatrzyma.
if not CONNECTION_STRING:
    raise ValueError("Brakuje AZURE_STORAGE_CONNECTION_STRING w pliku .env!")

# 2. Inicjalizacja Połączenia (Globalna)
# To wykonuje się TYLKO RAZ przy starcie programu.
# Otwieramy "tunel" do Azure/Azurite. Trzymamy to połączenie w zmiennej blob_service_client.
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)


# 3. Funkcja wysyłająca
def upload_file_to_blob(file_content: bytes, filename: str) -> str:
    """
    Bierze treść pliku (bajty) i nazwę.
    Wysyła do magazynu.
    Zwraca link (URL) do pliku.
    """

    # Generujemy unikalną nazwę, żeby nie nadpisać plików.
    # Np. jeśli wyślesz "dane.csv", a potem znowu "dane.csv", to bez tego drugi plik skasowałby pierwszy.
    # Teraz będzie: "550e8400-e29b_dane.csv"
    unique_filename = f"{uuid.uuid4()}_{filename}"

    # Tworzymy "uchwyt" do konkretnego pliku w kontenerze
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=unique_filename)

    # Fizyczne wysłanie danych (upload)
    blob_client.upload_blob(file_content, overwrite=True)

    # Zwracamy adres, pod którym plik jest dostępny (np. http://127.0.0.1:10000/...)
    return blob_client.url