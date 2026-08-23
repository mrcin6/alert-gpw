# 📈 Strategia Biznesowa i System Wczesnego Ostrzegania GPW

## 1. Cel Projektu & Value Proposition

**GPW Early Warning & LPP Sentiment Dashboard** to wysoce wyspecjalizowane narzędzie analityczno-strategiczne, którego głównym celem jest dostarczanie inwestorom i zarządzającym portfelami wczesnych sygnałów ostrzegawczych o potencjalnym odpływie kapitału z polskiego rynku finansowego (Giełdy Papierów Wartościowych w Warszawie – GPW). 

Projekt opiera się na dwóch filarach strategicznych:

1. **Główny cel strategiczny (Primary Target):** Detekcja wczesnych faz odpływu kapitału z GPW oparta na analizie korelacji z globalnym indeksem S&P 500 oraz zmienności kursu wymiany walutowej USD/PLN.
2. **Dodatkowy cel strategiczny (Secondary Target):** Zaawansowana analiza sentymentu rynkowego wobec spółki LPP S.A. (jednego z głównych motorów napędowych indeksu WIG20 i lidera polskiego sektora odzieżowego) z wykorzystaniem algorytmów analizy tekstu NLP (VADER) dostosowanych do polskiego słownictwa giełdowego i finansowego.

### Dlaczego monitorujemy te rynki? (Value Proposition)
Polski rynek giełdowy (GPW) jest rynkiem rozwijającym się (Emerging Markets), co oznacza, że wykazuje ogromną zależność od globalnej płynności i nastrojów instytucji zagranicznych. Gwałtowne tąpnięcia na rynkach rozwiniętych (USA) lub ucieczka od ryzyka (Risk-Off) przejawiają się natychmiastowym odpływem kapitału zagranicznego z GPW. Dashboard integruje w czasie rzeczywistym (odświeżanie co **300 sekund / 5 minut**) kluczowe wskaźniki makroekonomiczne, rynkowe oraz sentyment rynkowy, pozwalając na wyprzedzające dostosowanie struktury portfela inwestycyjnego przed wystąpieniem paniki na GPW.

---

## 2. Struktura Sygnałów Ostrzegawczych

System wczesnego ostrzegania klasyfikuje bieżące otoczenie rynkowe do jednego z czterech precyzyjnych stanów ryzyka. Reguły te zostały ustrukturyzowane w sposób hierarchiczny na podstawie twardych parametrów zdefiniowanych w konfiguracji systemu:

| Poziom Alertu | Status Ryzyka | Warunki Matematyczne Aktywacji | Strategiczne Znaczenie Rynkowe & Rekomendacja |
| :--- | :--- | :--- | :--- |
| **🔴 RED** | **Krytyczne Ryzyko Globalne** | `SP500 72h Drop` $\le -2.5\%$ <br> **LUB** `BTC 72h Drop` $\le -2.5\%$ <br> **LUB** `CNN Fear & Greed` $< 20$ pkt <br> **LUB** `Crypto Fear & Greed` $< 20$ pkt | **Sygnał głębokiej wyprzedaży globalnej.** Następuje panika na rynkach aktywów ryzykownych (akcje USA + kryptowaluty) oraz skrajny strach inwestorów. Bardzo wysokie prawdopodobieństwo tąpnięcia i panicznej wyprzedaży na GPW.<br>**Rekomendacja:** Redukcja pozycji lewarowanych, akumulacja gotówki, hedging. |
| **🟠 ORANGE**| **Lokalne Ryzyko Odpływu Kapitału** | `WIG20 24h Drop` $\le -1.5\%$ <br> **AND** `USD/PLN 24h Rise` $\ge +1.0\%$ | **Klasyczny odpływ kapitału zagranicznego.** Zagraniczni inwestorzy sprzedają polskie akcje (spadek WIG20) i natychmiast wymieniają złote na dolary (wzrost USD/PLN), osłabiając lokalną walutę.<br>**Rekomendacja:** Zacieśnienie zleceń obronnych dla spółek z WIG20, unikanie ekspozycji na polskie banki i blue-chips. |
| **⚠️ YELLOW** | **Globalne Ostrzeżenie / Niepewność** | `SP500 24h Drop` $\le -1.5\%$ <br> **LUB** `CNN Fear & Greed` $< 30$ pkt <br> **LUB** `Gold 24h Rise` $\ge +1.5\%$ | **Narastający niepokój makroekonomiczny.** Pierwsze korekty w USA, spadek nastrojów i ucieczka kapitału do bezpiecznej przystani (Gold). GPW może zareagować z opóźnieniem.<br>**Rekomendacja:** Weryfikacja i podciągnięcie poziomów obronnych (Stop-Loss), wstrzymanie się z nowymi zakupami akcji. |
| **🟢 GREEN** | **Otoczenie Stabilne** | Brak spełnienia powyższych warunków | **Normalne zachowanie rynku.** Zmienność mieści się w standardowych granicach. Przeważają czynniki mikroekonomiczne i analiza fundamentalna poszczególnych walorów.<br>**Rekomendacja:** Realizacja standardowej strategii portfelowej, poszukiwanie selektywnych okazji inwestycyjnych. |

### Szczegółowy Opis Reguł Ryzyka:

#### 1. Poziom Czerwony (Krytyczne Ryzyko)
* **Wiadomość systemowa:** `🔴 Krytyczne ryzyko: Globalna wyprzedaż na rynkach akcji. Wysokie prawdopodobieństwo głębszych spadków na GPW.`
* **Analiza ekonomiczna:** Poziom czerwony chroni portfel przed tzw. czarnymi łabędziami i falami paniki globalnej. Korelacja GPW z rynkiem USA w trakcie krachów zbliża się do 1.0. Dodatkowo, włączenie Bitcoina jako wskaźnika płynności i apetytu na ryzyko pozwala wyłapywać momenty, w których kapitał spekulacyjny zaczyna gwałtownie opuszczać rynki alternatywne przed uderzeniem w rynek akcji.

#### 2. Poziom Pomarańczowy (Ryzyko Lokalne)
* **Wiadomość systemowa:** `🟠 Ryzyko lokalne: Odpływ kapitału z polskiego rynku. Kurs USD/PLN rośnie przy spadkach indeksu WIG20.`
* **Analiza ekonomiczna:** Jest to sygnał dedykowany specyfice rynków rozwijających się. Sama przecena WIG20 może być korektą techniczną, jednak jednoczesne osłabienie złotego do dolara o 1.0% w 24h świadczy o systemowej wyprzedaży dokonywanej przez fundusze zagraniczne (ang. *foreign capital flight*).

#### 3. Poziom Żółty (Ostrzeżenie)
* **Wiadomość systemowa:** `⚠️ Ostrzeżenie: Pogorszenie nastrojów globalnych. Zweryfikuj poziomy zabezpieczające (Stop-Loss).`
* **Analiza ekonomiczna:** Stan przejściowy, który ma na celu zasygnalizowanie powolnego przegrzania rynku. Złoto rosnące o co najmniej 1.5% w ciągu doby przy jednoczesnych spadkach S&P 500 wskazuje na aktywne przenoszenie kapitału do tzw. "bezpiecznych przystani" (Safe Havens).

#### 4. Poziom Zielony (Stabilność)
* **Wiadomość systemowa:** `🟢 Stabilne otoczenie: Rynek zachowuje się w normie. Brak istotnych sygnałów alarmowych.`
* **Analiza ekonomiczna:** Stan neutralny, brak anomalii rynkowych. Sygnalizuje możliwość kontynuacji trendów średnioterminowych.

---

## 3. Komponenty Monitorowane i Ich Rola Strategiczna

Aby zapewnić pełną widoczność procesów rynkowych, system monitoruje następujący zestaw instrumentów finansowych:

1. **WIG20.WA (Główny Indeks GPW):**
   * **Rola:** Główny wskaźnik polskiego rynku akcji, skupiający 20 największych i najbardziej płynnych spółek.
   * **Korekta Techniczna QA:** Błędny i nieaktywny ticker `^WIG20` zostaje bezwzględnie usunięty ze stosu technologicznego na rzecz stabilnego symbolu `WIG20.WA`.
2. **S&P 500 (`^GSPC`):**
   * **Rola:** Najważniejszy indeks giełdowy świata, odzwierciedlający kondycję 500 największych korporacji w USA. Barometr globalnej koniunktury gospodarczej.
3. **NASDAQ (`^IXIC`):**
   * **Rola:** Indeks grupujący amerykańskie spółki technologiczne. Służy do oceny globalnego poziomu innowacji oraz spekulacyjnego apetytu na ryzyko (Risk-On / Risk-Off).
4. **Złoto (`GC=F`):**
   * **Rola:** Tradycyjny instrument zabezpieczający przed inflacją i niepokojem geopolitycznym. Wzrost ceny jest kluczowym składnikiem ostrzegawczym poziomu Żółtego.
5. **Bitcoin (BTC-USD):**
   * **Rola:** Najbardziej płynne aktywo kryptowalutowe, stanowiące współczesny sensor globalnej płynności i nastrojów inwestorów detalicznych oraz funduszy.
6. **USD/PLN (Kurs wymiany walutowej):**
   * **Rola:** Termometr wiarygodności inwestycyjnej Polski. Gwałtowne umocnienie dolara względem złotego przy jednoczesnym spadku WIG20 to główny wskaźnik ewakuacji kapitału z GPW.
7. **LPP S.A. (`LPP.WA`):**
   * **Rola:** Kluczowy komponent indeksu WIG20 (reprezentant sektora handlu detalicznego i odzieżowego). Sentyment wokół spółki silnie rzutuje na zachowanie całego indeksu. System analizuje wiadomości prasowe wykorzystując spolonizowany algorytm NLP (VADER), łącząc sentyment ze wskaźnikami technicznymi RSI i EMA.

---

## 4. Mapa Drogowa Rozwoju (Roadmap) & Standardy Jakości UX

Aby produkt spełniał założenia biznesowe i przeszedł kontrolę jakości (zgodnie z wynikami audytu `EVAL.md`), zarządzanie projektem wymaga natychmiastowego zamknięcia długu technologicznego i wdrożenia poprawek w zakresie UX. 

### ETAP I: Natychmiastowe Wdrożenie Poprawek Jakościowych (Priorytet Krytyczny)
*Cel: Eliminacja błędów technicznych, usunięcie blokerów QA i wdrożenie standardów użyteczności.*

1. **WIG20 Fix:** Natychmiastowe zaktualizowanie słownika mapowań tickerów na poprawny format: `WIG20.WA`. 
2. **Uporządkowanie Hierarchii Interfejsu (Prawo Jakoba):** Przeniesienie kontrolek filtrujących i sekcji wyboru pod główny nagłówek strony w pierwszej zakładce w celu zapewnienia prawidłowego przepływu informacji (od ogółu do szczegółu).
3. **Optymalizacja Mobilna i Czytelność (Prawo Hicka / WCAG):** Bezwarunkowe podniesienie wielkości czcionek w blokach CSS (`@media (max-width: 640px)`). Minimalne wielkości to `11px` dla etykiet `.uxr-metric-title`, `18px` dla wartości oraz minimum `18px` dla głównych nagłówków sekcji.
4. **Konsolidacja Sekcji Edukacyjnych (Prawo Bliskości):** Usunięcie rozpraszających paneli rozwijanych ("ℹ️ Poziomy", "ℹ️ WPŁYW") osadzonych w kluczowych blokach statystyk. Przeniesienie ich na sam dół interfejsu jako jeden wspólny, ustrukturyzowany przewodnik edukacyjny.
5. **Ujednolicenie Tabel i Interfejsu (Efekt Estetyka-Użyteczność):** Modernizacja i ostylowanie surowych tabel danych (szczególnie w zakładce LPP) dla zachowania wizualnej integracji z resztą kafelkowego widoku dashboardu (rezygnacja z domyślnego obiektu `st.dataframe` na rzecz stylizacji spójnej z zakładką pierwszą).
6. **Ergonomia Wyboru Czasu (Prawo Fittsa):** Zastąpienie ukrytego i wymagającego wielu kliknięć pola `st.selectbox` szybkim, jednowymiarowym elementem opartym o kontrolki radiowe: `st.radio(horizontal=True)`.
7. **Spójność i Kontrast Kolorów Wskaźników (WCAG):** Zmiana błędnie zastosowanego koloru dla wskaźników stabilności (obecnie `#cde200`) na wyraźny, głęboki odcień zieleni (rekomendowany `#2ecc71`) we wszystkich elementach sygnalizujących bezpieczeństwo i wzrosty.
8. **Modernizacja Wizualna (Depth Layering):** Wdrożenie zaleconych standardów graficznych dla elementów kafelkowych poprzez zastosowanie tła gradientowego (`linear-gradient(135deg, #1f2b40 0%, #172030 100%)`) oraz przestrzennych cieni typu `box-shadow`.
9. **Eliminacja Nakładania Legendy (Prawo Millera):** Przeparametryzowanie obiektu wykresów Plotly (`y=-0.2` dla legendy) w sposób uniemożliwiający przykrywanie danych przez legendę na ekranach urządzeń mobilnych.
10. **Asymetria i Spójność Zakładki LPP (Prawo Podobieństwa):** Rozbicie głównego nagłówka drugiej zakładki na dwie kolumny (proporcja `[4, 1]`) w celu symetrycznego zaimplementowania widżetu z aktualnym zegarem sesyjnym na wzór pierwszej zakładki.
11. **Redukcja Niepewności / Wskaźniki Aktualizacji:** Wdrożenie precyzyjnych etykiet tekstowych w interfejsie (`st.caption`), które bezpośrednio obok przycisków odświeżających poinformują użytkownika o dokładnym czasie ostatniego resetu bufora danych.

### ETAP II: Integracja Danych i Rozbudowa Analityki (Horyzont: 1-3 miesiące)
* **Powiadomienia Zewnętrzne (Push):** Automatyczna integracja z platformami Slack/Telegram – wysyłanie błyskawicznych notyfikacji do zarządzających w przypadku aktywacji alertów poziomu Pomarańczowego lub Czerwonego.
* **Rozszerzenie Listy Tickerów:** Poszerzenie monitoringu o polskie spółki surowcowe i wydobywcze (np. KGHM, Orlen) bezpośrednio korelujące z globalnymi rynkami surowców.
* **Integracja z Bezpośrednim API CNN:** Podłączenie autoryzowanego źródła dla danych o panice rynkowej, eliminujące ewentualne ryzyka błędów ekstrakcji metodami fall-back.

### ETAP III: Modele Predykcyjne NLP i Automatyzacja (Horyzont: 3-6 miesięcy)
* **Predykcja Sentymentu LPP oparta na Modelach Językowych (LLM):** Wdrożenie lokalnie trenowanego modelu transformerowego (np. zoptymalizowanego modelu BERT) zdolnego do głębokiego semantycznego rozumienia polskiego żargonu finansowego i kontekstu rynkowego.
* **Historyczny Backtesting:** Zaprojektowanie narzędzia do symulacji historycznych zysków i strat, badającego efektywność mechanizmu redukcji ekspozycji przy wystąpieniu alertów Orange/Red.
