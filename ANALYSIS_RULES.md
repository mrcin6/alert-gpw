# 🧮 Algorytmy i Reguły Analityczne (Financial Engine)

Dokument określa standardy obliczeniowe, wzory matematyczne oraz metodologię interpretacji danych finansowych i sentymentu rynkowego w systemie **GPW Early Warning & LPP Dashboard**. Wszystkie wdrożone w systemie wskaźniki (zarówno techniczne, jak i NLP) muszą być ściśle zgodne z poniższą specyfikacją, co gwarantuje spójność analityczną oraz poprawność weryfikacji ilościowej.

---

## 1. Wskaźniki Techniczne (RSI, EMA, SMA)

Wskaźniki techniczne stanowią fundament oceny dynamiki cenowej obserwowanych aktywów oraz pomagają w identyfikacji stanów wykupienia i wyprzedania rynku.

### A. Wskaźnik Siły Względnej — RSI (Relative Strength Index)

Wskaźnik RSI mierzy prędkość i wielkość kierunkowych zmian cen w określonym okresie. W naszym silniku analitycznym stosujemy standardowy interwał **$N = 14$** sesji (lub godzin, w zależności od wybranego interwału).

#### Wzór Matematyczny:
Wyjściowy wzór na RSI opiera się na koncepcji siły względnej ($RS$):
$$RSI_t = 100 - \frac{100}{1 + RS_t}$$

Gdzie $RS$ (Relative Strength) definiuje się jako stosunek wykładniczych lub prostych średnich ruchów wzrostowych do ruchów spadkowych z ostatnich $N$ okresów. W naszej implementacji w bibliotece Pandas (`app.py`) stosujemy prostą średnią kroczącą (Simple Moving Average - SMA) zysków i strat z ostatnich 14 okresów jako spójne przybliżenie oryginalnego sformułowania Wildera:
$$RS_t = \frac{AvgGain_{14, t}}{AvgLoss_{14, t}}$$

#### Procedura Obliczeniowa:
1. Obliczamy zmianę ceny zamknięcia dla każdej sesji $t$:
   $$\Delta P_t = P_t - P_{t-1}$$
2. Wyodrębniamy ruchy wzrostowe ($U_t$) oraz ruchy spadkowe ($D_t$):
   $$U_t = \max(\Delta P_t, 0) = \begin{cases} \Delta P_t & \text{dla } \Delta P_t > 0 \\ 0 & \text{dla } \Delta P_t \le 0 \end{cases}$$
   $$D_t = \max(-\Delta P_t, 0) = \begin{cases} -\Delta P_t & \text{dla } \Delta P_t < 0 \\ 0 & \text{dla } \Delta P_t \ge 0 \end{cases}$$
3. Wyznaczamy proste średnie ruchów wzrostowych ($AvgGain$) oraz spadkowych ($AvgLoss$) z ostatnich $N=14$ okresów:
   $$AvgGain_{14, t} = \frac{1}{14} \sum_{i=0}^{13} U_{t-i}$$
   $$AvgLoss_{14, t} = \frac{1}{14} \sum_{i=0}^{13} D_{t-i}$$
4. Ostateczna uproszczona postać wzoru, eliminująca ryzyko dzielenia przez zero przy braku strat:
   $$RSI_t = 100 \times \frac{AvgGain_{14, t}}{AvgGain_{14, t} + AvgLoss_{14, t}}$$

#### Interpretacja i Progi Decyzyjne:
*   **🟢 $RSI < 30$ (Wyprzedanie / Oversold):** Sugeruje, że presja sprzedających sprowadziła cenę do skrajnie niskiego poziomu w relacji do historycznej zmienności. Aktywo staje się statystycznie niedowartościowane w krótkim okresie. Jest to sygnał potencjalnego wyczerpania podaży i zbliżającego się odbicia cenowego w górę (atrakcyjna cena zakupu).
*   **🔴 $RSI > 70$ (Wykupienie / Overbought):** Sugeruje, że presja kupujących wybiła cenę do poziomu przegrzania rynkowego. Istnieje wysokie ryzyko przesilenia popytu, realizacji zysków przez dużych graczy i nadejścia korekty spadkowej.
*   **⚪ Przedział Neutralny ($30 \le RSI \le 70$):** Rynek znajduje się w fazie konsolidacji lub stabilnego trendu, bez skrajnych anomalii popytowo-podażowych.

---

### B. Procentowe Odchylenie od Średniej EMA-20

Średnia wykładnicza EMA-20 reprezentuje krótkoterminowy kierunek trendu i jest silniej zorientowana na najnowsze ceny dzięki zastosowaniu malejącej wagi historycznych punktów danych.

#### Wzór Matematyczny EMA:
Wartość $EMA$ dla okresu $S = 20$ w danej chwili $t$ oblicza się rekurencyjnie:
$$EMA_{20, t} = \alpha \cdot P_t + (1 - \alpha) \cdot EMA_{20, t-1}$$

Gdzie mnożnik wygładzający $\alpha$ wynosi:
$$\alpha = \frac{2}{S + 1} = \frac{2}{20 + 1} = \frac{2}{21} \approx 0.09524 \ (9.52\%)$$

#### Wzór na Odchylenie Procentowe ($\Delta\% EMA_{20}$):
Mierzy on względny dystans aktualnej ceny zamknięcia ($P_t$) od linii średniej wykładniczej:
$$\Delta\% EMA_{20} = \left( \frac{P_t}{EMA_{20, t}} - 1 \right) \times 100\%$$

#### Interpretacja Rynkowa:
*   **$\Delta\% EMA_{20} > 0$:** Cena aktywa znajduje się powyżej średniej krótkoterminowej. Potwierdza to lokalne momentum popytowe (krótkoterminowy trend wzrostowy).
*   **$\Delta\% EMA_{20} < 0$:** Cena znajduje się poniżej średniej. Świadczy to o słabości rynku i dominacji niedźwiedzi w krótkim terminie.

---

### C. Procentowe Odchylenie od Średniej SMA-200

Średnia prosta SMA-200 jest fundamentalnym wskaźnikiem trendu długoterminowego. Reprezentuje uśrednioną cenę aktywa z ostatnich 200 sesji i jest powszechnie obserwowana przez fundusze instytucjonalne.

#### Wzór Matematyczny SMA:
$$SMA_{200, t} = \frac{1}{200} \sum_{i=0}^{199} P_{t-i}$$

*Uwaga techniczna:* Wskaźnik ten wymaga bezwzględnego minimum 200 punktów danych w analizowanym szeregu czasowym (`len(series) >= 200`). Jeśli warunek ten nie jest spełniony (np. przy krótkiej historii notowań w ujęciu godzinowym), wskaźnik przyjmuje wartość `NaN`, a jego procentowy dystans jest bezpiecznie zerowany ($0.0\%$), co zapobiega błędom aplikacji.

#### Wzór na Odchylenie Procentowe ($\Delta\% SMA_{200}$):
$$\Delta\% SMA_{200} = \left( \frac{P_t}{SMA_{200, t}} - 1 \right) \times 100\%$$

#### Interpretacja Rynkowa:
*   **$\Delta\% SMA_{200} > 0$ (Rynek Byka / Bull Market):** Długoterminowy trend jest wzrostowy. Średnia SMA-200 działa jako kluczowa bariera wsparcia w momentach korekt.
*   **$\Delta\% SMA_{200} < 0$ (Rynek Niedźwiedzia / Bear Market):** Długoterminowy trend jest spadkowy. Średnia SMA-200 stanowi wówczas silny opór przy próbach powrotu do wzrostów.

---

## 2. Logika Normalizacji Ceny (%)

### Cel Biznesowy i Problem Skali:
W kokpicie porównujemy aktywa o skrajnie odmiennych cenach nominalnych (np. jedna akcja LPP S.A. kosztuje kilkanaście tysięcy złotych, podczas gdy kurs USD/PLN oscyluje wokół 4 złotych). Wykreślenie cen nominalnych na jednym wykresie zniszczyłoby czytelność instrumentów o mniejszej wartości nominalnej. Normalizacja sprowadza wszystkie instrumenty do wspólnego mianownika.

### Wzór Normalizacji:
Dla każdego aktywa posiadającego serię cen zamknięcia $P = [P_0, P_1, \dots, P_T]$ w wybranym oknie czasowym, znormalizowaną cenę $P^{norm}_t$ w punkcie $t$ obliczamy jako:
$$P^{norm}_t = \left( \frac{P_t}{P_0} \right) \times 100\%$$
Gdzie $P_0$ oznacza cenę zamknięcia w pierwszym punkcie czasowym wybranego przedziału analizy (np. pierwsza godzina dla widoku 72h lub pierwszy dzień dla widoku 30 dni).

### Dowód Matematyczny Stałego Punktu Startowego (Baseline 100%):
Podstawiając $t = 0$ (moment startowy) do wzoru normalizacji:
$$P^{norm}_0 = \left( \frac{P_0}{P_0} \right) \times 100\% = 1 \times 100\% = 100\%$$

*Wniosek:* Niezależnie od wyjściowej wartości nominalnej aktywa (czy jest to $16\,000$ PLN, czy $3.85$ PLN), każde aktywo na wykresie znormalizowanym rozpoczyna bieg dokładnie z poziomu **$100\%$**.

### Związek z Skumulowaną Stopą Zwrotu (Cumulative Return):
Skumulowana stopa zwrotu $R_t$ z inwestycji od momentu $t=0$ do $t$ wynosi:
$$R_t = \frac{P_t - P_0}{P_0} = \frac{P_t}{P_0} - 1$$

Mnożąc stopę zwrotu przez $100\%$:
$$R_t \times 100\% = \left( \frac{P_t}{P_0} - 1 \right) \times 100\% = \left( \frac{P_t}{P_0} \right) \times 100\% - 100\%$$

Podstawiając wyjściowy wzór na znormalizowaną cenę $P^{norm}_t$:
$$R_t \times 100\% = P^{norm}_t - 100\% \implies P^{norm}_t = (R_t \times 100\%) + 100\%$$

*Wniosek:* Znormalizowany wykres odzwierciedla skumulowaną procentową stopę zwrotu z danego aktywa powiększoną o bazowe 100%. Umożliwia to bezpośrednią wizualną ocenę relatywnej siły, korelacji, zmienności i stóp zwrotu wszystkich ośmiu obserwowanych aktywów w tym samym czasie.

---

## 3. Metodologia Analizy NLP (VADER)

Analiza nastrojów wokół LPP S.A. opiera się na algorytmie **VADER (Valence Aware Dictionary and sEntiment Reasoner)**. VADER łączy słownik pojęć z zestawem reguł gramatycznych i interpunkcyjnych w celu wyznaczenia kierunku oraz siły ładunku emocjonalnego badanego tekstu.

### Wskaźnik Złożony (Compound Score)
Kluczowym parametrem wyjściowym analizatora VADER jest **Compound Score**. Jest to znormalizowany współczynnik, obliczany na podstawie sumy wag emocjonalnych (walencji) wszystkich słów w analizowanym tekście, poddany normalizacji za pomocą funkcji logistycznej (hiperbolicznej) do przedziału $[-1.0, 1.0]$:
$$Compound = \frac{S}{\sqrt{S^2 + \alpha}}$$

Gdzie:
*   $S$ to zagregowana, zmodyfikowana gramatycznie suma ocen walencyjnych słów w tekście.
*   $\alpha$ to parametr wygładzający/normalizacyjny (w standardowej bibliotece VADER wynosi on stałe $\alpha = 15$).

### Reguły Klasyfikacji Sentymentu
System dzieli nagłówki prasowe na trzy kategorie na podstawie wartości wskaźnika złożonego:
1.  🟢 **Sentyment Pozytywny (Bullish):** $Compound \ge 0.05$
2.  🔴 **Sentyment Negatywny (Bearish):** $Compound \le -0.05$
3.  ⚪ **Sentyment Neutralny:** $-0.05 < Compound < 0.05$

### Adaptacja do Polskich Nagłówków Prasowych (Polish Headline Adaptation Notes)
Model VADER został pierwotnie stworzony i wyszkolony na języku angielskim. Bezpośrednie stosowanie go do nagłówków pobieranych z Google News w języku polskim wymaga uwzględnienia istotnych założeń technicznych i rynkowych:

1.  **Słownik i Luka Językowa (Lexicon Gap):**
    Natywne polskie słowa (np. *wzrost, sukces, spadek, kryzys*) nie są bezpośrednio tłumaczone w pamięci VADER. Jednakże nagłówki rynkowe posiadają cechy ułatwiające detekcję emocji:
2.  **Rola Emotikonów i Emoji (Uniwersalny Sentyment):**
    VADER posiada wbudowane, silne wagi walencyjne dla emoji. Polskie nagłówki finansowe w serwisach informacyjnych oraz mediach społecznościowych są silnie nasycone emoji, co pozwala modelowi na precyzyjną ocenę:
    *   **Pozytywne ($Compound \ge 0.05$):** `🚀` (rakieta - symbol gwałtownego wzrostu), `📈` (wykres rosnący), `💎` (diament / wysoka wartość), `🏆` (puchar - sukces), `🔥` (ogień - hit rynkowy).
    *   **Negatywne ($Compound \le -0.05$):** `📉` (wykres spadający), `🔴` (czerwone koło - ostrzeżenie/spadek), `💥` (wybuch - załamanie), `⚠️` (trójkąt ostrzegawczy), `💔` (pęknięte serce).
3.  **Wielkość Liter i Interpunkcja:**
    VADER zwiększa wagę emocjonalną w przypadku użycia wielkich liter (*np. "REKORD", "KRACH"*) oraz wykrzykników (*"!"*), co jest powszechne w clickbaitowych nagłówkach prasowych.
4.  **Terminologia Międzynarodowa (Internacjonalizmy):**
    Polska publicystyka ekonomiczna obficie czerpie ze słownictwa anglosaskiego i międzynarodowego. Słowa te są częściowo rejestrowane przez leksykon VADER lub powiązane biblioteki: np. *krach, boom, hossa, bessa, lider, debiut, kryzys, redukcja, panika, optymizm, pesymizm*.

### Interpretacja Biznesowa dla LPP S.A. ($LPP)

Sentyment medialny wokół LPP S.A. (największego gracza odzieżowego na GPW) bezpośrednio przekłada się na zachowanie inwestorów i kurs akcji.

*   **Sygnały Bullish (Wzrostowe):**
    *   *Tematyka nagłówków:* Rekordowe przychody kwartalne, dynamiczny wzrost marży brutto na sprzedaży, dynamiczny rozwój e-commerce, udane otwarcia salonów flagowych Reserved w Europie Zachodniej (Londyn, Mediolan, Monachium), rekomendacje maklerskie typu "Kupuj".
    *   *Znaczenie finansowe:* Informuje o wysokiej sprawności operacyjnej, odporności na inflację i rosnącej pozycji międzynarodowej. Przyciąga na walory LPP zagraniczny kapitał instytucjonalny, co wzmacnia indeks WIG20.
*   **Sygnały Bearish (Spadkowe):**
    *   *Tematyka nagłówków:* Zaburzenia w globalnych łańcuchach dostaw (np. zatory transportu morskiego z Azji), skokowy wzrost kosztów frachtu, spadek marż wynikający z agresywnej polityki rabatowej, słabsza sprzedaż w kolekcjach sezonowych spowodowana anomaliami pogodowymi, oskarżenia wizerunkowe lub raporty funduszy shortujących (np. zarzuty o fikcyjne wyjście z rynku rosyjskiego).
    *   *Znaczenie finansowe:* LPP działa na rynku globalnym i ma bardzo wrażliwą strukturę kosztów logistycznych. Negatywne doniesienia medialne natychmiast wywołują wzrost niepewności, obniżenie wycen analitycznych i mogą stać się zarzewiem gwałtownej ucieczki kapitału (paniki sprzedażowej).

---

## 4. Weryfikacja Matematyczna

W celu zachowania bezwzględnej sprawności i poprawności obliczeń finansowych, silnik analityczny poddawany jest testom według poniższych scenariuszy weryfikacyjnych.

### A. Weryfikacja RSI (14)

Weryfikujemy działanie algorytmu na zadanym, uproszczonym 15-sesyjnym ciągu cen zamknięcia:
$$P = [100, 102, 104, 102, 100, 98, 96, 98, 100, 102, 104, 106, 108, 110, 112]$$

#### Obliczenia krok po kroku:
1.  **Różnice cenowe ($\Delta P_t$):**
    $[+2, +2, -2, -2, -2, -2, +2, +2, +2, +2, +2, +2, +2, +2]$ (razem 14 zmian)
2.  **Podział na zyski ($U$) i straty ($D$):**
    *   $U = [2, 2, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2]$ (suma zysków = $18$)
    *   $D = [0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0]$ (suma strat = $8$)
3.  **Obliczenie średnich ruchów (SMA dla okna $N = 14$):**
    *   $AvgGain = \frac{18}{14} \approx 1.2857$
    *   $AvgLoss = \frac{8}{14} \approx 0.5714$
4.  **Siła względna ($RS$):**
    *   $RS = \frac{AvgGain}{AvgLoss} = \frac{1.2857}{0.5714} = 2.25$
5.  **Obliczenie wskaźnika RSI:**
    *   $RSI = 100 - \frac{100}{1 + 2.25} = 100 - 30.77 = 69.23$
    *   *Zaokrąglona wartość rynkowa:* **$69.2$**

**Kryterium akceptacji:** Kod w `app.py` uruchomiony z powyższym wektorem testowym musi zwrócić wartość **$69.2$** (z dokładnością do jednego miejsca po przecinku).

---

### B. Weryfikacja Odchylenia EMA-20

Mierzymy poprawność dystansu od krótkookresowej średniej wykładniczej.

#### Dane testowe:
*   Aktualna cena zamknięcia ($P_t$): $105.00$
*   Bieżąca wartość średniej ($EMA_{20, t}$): $100.00$

#### Obliczenie:
$$\Delta\% EMA_{20} = \left( \frac{105.00}{100.00} - 1 \right) \times 100\% = (1.05 - 1) \times 100\% = 0.05 \times 100\% = +5.00\%$$

**Kryterium akceptacji:** Tabela wskaźników technicznych w systemie musi wyświetlić wartość **$+5.00\%$** dla obserwowanego aktywa.

---

### C. Weryfikacja Odchylenia SMA-200

Mierzymy odporność obliczeń długoterminowych.

#### Dane testowe:
*   Aktualna cena zamknięcia ($P_t$): $120.00$
*   Bieżąca wartość średniej ($SMA_{200, t}$): $150.00$

#### Obliczenie:
$$\Delta\% SMA_{200} = \left( \frac{120.00}{150.00} - 1 \right) \times 100\% = (0.80 - 1) \times 100\% = -0.20 \times 100\% = -20.00\%$$

**Kryterium akceptacji:** Tabela wskaźników w kokpicie musi wyświetlić dystans **$-20.00\%$**. Przy szeregu czasowym o długości krótszej niż 200 punktów, system musi zwrócić **$0.0\%$** (brak błędu wykonania).

---

### D. Weryfikacja Normalizacji Ceny na Wykresie

Mierzymy stabilność punktu startowego dla wspólnej skali procentowej.

#### Dane testowe:
*   Cena zamknięcia na początku wybranego zakresu ($P_0$): $150.00$ PLN
*   Aktualna cena zamknięcia w badanej chwili ($P_t$): $180.00$ PLN

#### Obliczenie:
$$P^{norm}_t = \left( \frac{180.00}{150.00} \right) \times 100\% = 1.20 \times 100\% = 120.00\%$$

**Kryterium akceptacji:** Wykres Plotly w trybie znormalizowanym musi uplasować punkt serii na wysokości poziomej osi wartości równej dokładnie **$120.0$**.

---

### E. Weryfikacja Klasyfikacji Sentymentu NLP VADER

Testujemy reakcję słownika i reguł normalizacyjnych VADER na reprezentatywne nagłówki:

1.  **Przypadek Testowy A (Sygnał Popytowy - Pozytywny):**
    *   *Nagłówek:* `"LPP S.A. ma świetne wyniki finansowe i zapowiada dalszą ekspansję! 🚀"`
    *   *Analiza:* Obecność uniwersalnego pozytywnego emoji `🚀`, wykrzyknika `!` oraz pozytywnej polaryzacji internacjonalizmu "ekspansję".
    *   *Oczekiwany wynik:* $Compound \ge 0.05 \implies$ **Sentyment Pozytywny** (oznaczenie zieloną kropką `🟢`).
2.  **Przypadek Testowy B (Sygnał Podażowy - Negatywny):**
    *   *Nagłówek:* `"Spadek marż i gwałtowne załamanie sprzedaży w salonach LPP. 🔴"`
    *   *Analiza:* Obecność negatywnego, uniwersalnego symbolu `🔴` oraz brak jakichkolwiek sformułowań pozytywnych.
    *   *Oczekiwany wynik:* $Compound \le -0.05 \implies$ **Sentyment Negatywny** (oznaczenie czerwoną kropką `🔴`).
3.  **Przypadek Testowy C (Sygnał Neutralny):**
    *   *Nagłówek:* `"LPP S.A. publikuje raport okresowy za I półrocze."`
    *   *Analiza:* Suchy komunikat giełdowy, brak nacechowania emocjonalnego, brak emoji oraz brak interpunkcji wzmacniającej.
    *   *Oczekiwany wynik:* $-0.05 < Compound < 0.05 \implies$ **Sentyment Neutralny** (oznaczenie białą kropką `⚪`).

**Kryterium akceptacji:** Wszystkie nagłówki zaklasyfikowane przez analizator w module `fetch_lpp_news()` muszą otrzymać odpowiednie ikony wizualne na liście wzmianek w panelu bocznym.
