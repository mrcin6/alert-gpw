# 📁 Rejestr Projektu & Pamięć Lokalna (Alert GPW & LPP Dashboard)

Ten dokument pełni rolę lokalnego rejestru stanu projektu oraz bazy wiedzy dla asystentów AI (Gemini CLI), umożliwiając natychmiastowe podjęcie prac w kolejnych iteracjach.

---

## 📌 Aktualny Stan Projektu (Stan na 23 Sierpnia 2026)

- **Status Wdrożenia**: Produkcja (`main` -> Streamlit.io) - **ZAKOŃCZONE POMYŚLNIE**
- **Ocena QA (Quality Gate)**: **SCORE: 5 / 5 (Doskonały)** (Zweryfikowano w `EVAL.md`)
- **Główna Gałąź Git**: `main` (Zsynchronizowana z repozytorium `https://github.com/mrcin6/alert-gpw.git`)

---

## 🛠️ Architektura Systemu i Komponenty

Aplikacja opiera się na **Wieloagentowej Pętli Dewelopersko-Audytowej (Quality Gate System)**, która automatycznie generuje strategie, wskaźniki techniczne, pisze kod, audytuje interfejs pod kątem praw UX oraz sprawdza poprawność matematyczną przed wypuszczeniem wersji na produkcję.

### 1. Struktura Plików w Projekcie
- `app.py` — Główny kod źródłowy aplikacji Streamlit (zawierający zaawansowane style CSS, integracje API i logikę wykresów).
- `run_pipeline.sh` — Skrypt orkiestrujący, który uruchamia 6 agentów w pętli zamkniętej aż do osiągnięcia `SCORE >= 4` w raporcie `EVAL.md`.
- `config/strategy.json` — Konfiguracja progów ryzyka (alerty: zielony, żółty, pomarańczowy, czerwony) i celów rynkowych.
- `config/watchlist.json` — Lista monitorowanych instrumentów (yfinance) i kanałów wiadomości RSS.
- `.gemini/prompts/` — Prompty systemowe dla 6 agentów:
  1. `strategy_po_prompt.md` -> Aktualizuje `PORTFOLIO_STRATEGY.md`
  2. `tech_researcher_prompt.md` -> Aktualizuje `DATA_SOURCES.md`
  3. `financial_expert_prompt.md` -> Aktualizuje `ANALYSIS_RULES.md`
  4. `coder_prompt.md` -> Poprawia i nadpisuje `app.py`
  5. `ux_prompt.md` -> Przeprowadza audyt UX i zapisuje w `UX_AUDIT.md`
  6. `qa_prompt.md` -> Weryfikuje poprawność, przypisuje `SCORE` (1-5) i delta poprawki w `EVAL.md`.

---

## 🧮 Kluczowe Reguły Merytoryczne i Poprawki (Iteracja zakończona)

1. **Wdrożenie Poprawki WIG20 (Kluczowa Poprawka)**:
   - **Problem**: Symbol `^WIG20` na Yahoo Finance jest zdelistowany/nieaktywny i zwracał puste ramki danych.
   - **Rozwiązanie**: Wszystkie zapytania w aplikacji zostały zaktualizowane do poprawnego, aktywnego tickera **`WIG20.WA`**. Pobieranie danych godzinowych i dziennych działa teraz z pełną stabilnością.
2. **Matematyczna Bezpieczeństwo Wskaźników**:
   - Zaimplementowano odporne na błędy (np. dzielenie przez zero, brak danych w seriach rynkowych) wskaźniki: **RSI (14)**, **EMA-20 % Distance** oraz **SMA-200 % Distance**.
   - Dodano walidację początkowej ceny równej zero podczas normalizacji wykresu.
3. **Prawa UX (Wdrożono 10 zmian w interfejsie)**:
   - Zoptymalizowano hierarchię wizualną (Header jest zawsze na górze, kontrolki czasu pod nagłówkiem).
   - Przebudowano selectbox do poziomych elementów `st.radio(horizontal=True)` dla zwiększenia szybkości wyboru.
   - Skonsolidowano pojedyncze expandery w jeden, zorganizowany panel edukacyjny (`st.tabs`) na dole aplikacji (eliminuje problem długiego przewijania na mobile).
   - Zamieniono widget `st.dataframe` w Zakładce 2 na spójną wizualnie tabelę HTML w kontenerze `<div data-testid="stTable">`.
   - Wdrożono czystą, giełdową zieleń `#2ecc71` dla kontrastu z żółtym neonem `#ecfa64`.
   - Karty KPI zyskały linearne gradienty, wewnętrzne obwódki i głębokie cienie (Glassmorphism effect).
   - Legenda Plotly została przesunięta pod wykres (`y=-0.15`), zapobiegając nakładaniu się na linie cenowe na mobile.
   - Wprowadzono wskaźnik świeżości danych (`st.caption` informujące o dokładnej sekundzie aktualizacji) pod przyciskami odświeżania.
   - Symmetria: Dodano warszawski zegar systemowy do Zakładki LPP S.A.

---

## 🚀 Jak Uruchomić Kolejną Iterację (Instrukcja dla AI / Dewelopera)

Gdy przystępujesz do kolejnej iteracji prac:
1. Skonsultuj się z użytkownikiem i wprowadź wymagane modyfikacje w plikach konfiguracyjnych:
   - `config/strategy.json` (np. zmiana poziomów alertów, kryteriów ryzyka).
   - `config/watchlist.json` (np. dodanie nowych tickerów, takich jak `EURPLN=X`, `mWIG40.WA` lub zmianę kanałów RSS).
2. Uruchom kompletną, automatyczną pętlę deweloperską z poziomu terminala:
   ```bash
   ./run_pipeline.sh
   ```
3. Skrypt automatycznie zaangażuje wszystkich 6 agentów, wygeneruje świeże raporty audytowe, nadpisze kod w `app.py` uwzględniając nowe wymagania i zalecenia UX, po czym podda kod testom QA.
4. Po udanej walidacji (`SCORE >= 4` w `EVAL.md`), zaktualizuj ten rejestr (`GEMINI.md`), zrób commit zmian i wypchnij je na GitHub, aby Streamlit.io automatycznie zaktualizował wersję produkcyjną:
   ```bash
   git add app.py config/ .gemini/ PORTFOLIO_STRATEGY.md DATA_SOURCES.md ANALYSIS_RULES.md UX_AUDIT.md EVAL.md run_pipeline.sh GEMINI.md .gitignore
   git commit -m "feat: <opis zmian w kolejnej iteracji>"
   git push origin main
   ```
