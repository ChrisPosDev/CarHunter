# CarHunter

System do monitorowania nowych ogłoszeń motoryzacyjnych z wielu portali (np. Otomoto) w czasie rzeczywistym.

## Funkcje

*   **Powiadomienia na Discord** o nowych ogłoszeniach i spadkach cen.
*   **Architektura modułowa**: Portale są konfigurowane przez pliki YAML (`config/portals/*.yaml`). Nie ma potrzeby zmiany kodu w większości przypadków zmiany budowy strony.
*   **Strategie pobierania**: System przechodzi płynnie z API (JSON) na parsowanie HTML, jeśli API ulegnie zmianie.
*   **Deduplikacja**: Wbudowana baza SQLite pamięta ogłoszenia (lokalnie, brak zależności na Redis itp.).

## Instalacja i uruchomienie (Windows / macOS / Linux)

Projekt używa narzędzia `uv` do zarządzania zależnościami i środowiskiem (jest super szybki).

1.  **Zainstaluj uv** (jeśli jeszcze nie masz):
    *   macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    *   Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

2.  **Skonfiguruj projekt**:
    *   Skopiuj plik `.env.example` do `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Wklej swój webhook z Discorda do pliku `.env`.

3.  **Dostosuj wyszukiwania**:
    *   Zajrzyj do `config/settings.yaml`, by zmienić częstotliwość odświeżania lub adres URL wyszukiwania na Otomoto (wklej cały link po ustawieniu filtrów).

4.  **Uruchom aplikację**:
    Narzędzie `uv run` automatycznie pobierze wymagane zależności (httpx, pydantic, itp.) w izolowanym środowisku `.venv` i odpali kod.
    ```bash
    uv run python -m carhunter
    ```

## Konfiguracja nowego portalu

Dodanie nowego portalu (np. OLX) polega na utworzeniu pliku `config/portals/olx.yaml`. Ustawiasz tam ścieżki do danych używając prostego DSL do transformacji typów, np: `cena_xpath | price`.

