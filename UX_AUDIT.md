# 🎨 Audyt UX i Czytelności Dashboardu

## Ocena Ogólna (UX Rating)

| Prawo UX | Stan obecny i wyzwania | Ocena (1-5) |
| :--- | :--- | :--- |
| **Jakob’s Law** *(Prawo Jakoba)* | Interfejs wykorzystuje standardowe karty wskaźników, zakładki oraz boczny panel, co sprzyja szybkiej nauce obsługi. Jednak limonkowa kolorystyka stanów pozytywnych (`#cde200`) zbytnio zbiega się z neonowo-żółtym ostrzeżeniem (`#ecfa64`), naruszając intuicyjną semantykę kolorów giełdowych. | **3.8 / 5.0** |
| **Fitts’s Law & Hick’s Law** *(Prawo Fittsa i Hicka)* | Główne kontrolki wyboru okresu i odświeżania są łatwo dostępne. Jednak na urządzeniach mobilnych drastyczne zmniejszenie paddingów i rozmiarów fontów (np. tytuły metryk do `8px`) tworzy zbyt małe obszary dotykowe (touch targets), co utrudnia interakcję i łamie zalecenia dotyczące dostępności. | **3.2 / 5.0** |
| **Law of Proximity & Similarity** *(Prawo Bliskości i Podobieństwa)* | Informacje są logicznie ustrukturyzowane, lecz integracja expanderów ("ℹ️ Poziomy", "ℹ️ WPŁYW") bezpośrednio pod każdą kartą metryki w kolumnie rozbija wizualną spójność. Na telefonach komórkowych elementy te układają się w długi, nieczytelny i poszatkowany pionowy stos. | **3.0 / 5.0** |
| **Miller’s Law** *(Prawo Millera)* | Wykres znormalizowany i tabela wskaźników zawierają dokładnie 7 elementów, co idealnie mieści się w granicach pamięci roboczej człowieka (7 ± 2). Informacje nie przytłaczają, a dane są wysoce skanowalne. | **4.5 / 5.0** |
| **Aesthetic-Usability Effect** *(Efekt Estetyka-Użyteczność)* | Dashboard posiada nowoczesną, ciemną kolorystykę rynkową premium (tła: `#131f33`, `#111926`, `#1f2b40`) i profesjonalną typografię Poppins. Wadą jest niespójność tabelaryczna – Tabela 1 to statyczny, ostylowany element HTML, podczas gdy Tabela 2 to domyślny widget `st.dataframe` z zupełnie innym designem. | **4.0 / 5.0** |
| **Serial Position Effect** *(Efekt Pozycji Seryjnej)* | Najważniejsze alerty rynkowe znajdują się na samej górze strony, co natychmiast przyciąga uwagę. Poważnym błędem hierarchii jest natomiast umieszczenie paska kontrolnego (`ctrl_cols`) fizycznie *powyżej* głównego nagłówka strony w kodzie zakładki GPW. | **3.5 / 5.0** |

### **Skumulowana Ocena UX (Overall Score): 3.7 / 5.0**
*Aplikacja posiada doskonały fundament estetyczny i poprawnie wdraża kluczowe wskaźniki rynkowe, jednak cierpi na błędy w hierarchii elementów, poważne ograniczenia czytelności na urządzeniach mobilnych oraz nadmierną fragmentację komponentów informacyjnych.*

---

## Analiza Spójności Wizualnej i Brandingu

### 1. Typografia (Font & Scale)
- **Import i Rodzina:** Czcionka Google **Poppins** została zaimportowana prawidłowo. W definicjach CSS brakuje jednak bezpiecznych fontów rezerwowych (tzw. system fallback fonts). W przypadku problemów z siecią interfejs może nieoczekiwanie przełączyć się na domyślny font bezszeryfowy o innej szerokości znaków.
- **Skala Typograficzna:**
  - Nagłówek główny (`.cxr-title`): `30px` (optymalny na desktopie, zbyt dominujący na mobile przed zmniejszeniem).
  - Podnagłówki (`.cxr-subheader-text`): `20px` (doskonały akcent wizualny).
  - Wartości metryk (`.uxr-metric-value`): `26px` (wyraziste i czytelne).
  - Tytuły metryk (`.uxr-metric-title`): `11px` (nieco zbyt małe w stosunku do wartości, na mobile drastycznie zmniejszone do uniemożliwiających odczyt `8px`).

### 2. Paleta Kolorystyczna (Color Palette)
- **Tła systemowe:**
  - Główny obszar roboczy (`#131f33`) oraz panel boczny/karty (`#111926`, `#1f2b40`) tworzą profesjonalny, trójwymiarowy efekt głębi (depth layering), który zmniejsza zmęczenie wzroku podczas nocnej pracy.
- **Akcenty i Sygnalizatory:**
  - Neonowy żółto-zielony (`#ecfa64`) jest używany do wyróżnień.
  - Limonkowy (`#cde200`) oznacza wartości pozytywne.
  - Bliskość tonalna `#ecfa64` i `#cde200` zmniejsza kontrast semantyczny. Kolory te zlewają się w percepcji użytkownika, co osłabia szybkość rozpoznawania alertów.

### 3. Obramowania i Separatory
- **Spójność:** Elementy takie jak pasek zakładek i expandery posiadają bardzo cienkie obramowanie o niskim poziomie krycia (`1px solid rgba(255,255,255,0.05)`). Jest to bardzo elegancki zabieg.
- **Niespójność:** Karty metryk mają jedynie grube lewe obramowanie (`8px`), co kontrastuje z pełnym obramowaniem innych kontenerów i sprawia, że karty wydają się "niedokończone" z pozostałych trzech stron.

---

## Kompatybilność Mobilna i Responsywność

Chociaż kod zawiera dedykowane media query `@media (max-width: 640px)`, wdrożone rozwiązania wprowadzają krytyczne problemy z użytecznością (usability issues) na smartfonach:

1. **Drastyczny spadek czytelności (Micro-Typography):**
   - Zmniejszenie czcionki tytułów metryk do `8px` i danych w tabeli do `10px` sprawia, że interfejs staje się całkowicie nieakceptowalny pod kątem dostępności (WCAG AA wymaga minimalnego czytelnego stopnia pisma na ekranach mobilnych wynoszącego ok. `11-12px`).
2. **Problem "Stosu" w Kolumnach (Column Stacking Chaos):**
   - Streamlit na urządzeniach mobilnych automatycznie układa kolumny pionowo jedna pod drugą. W rezultacie struktura kolumnowa metryk i expanderów:
     ```
     Karta KPI 1 -> Expander 1 -> Karta KPI 2 -> Expander 2 -> ...
     ```
     zamienia się w niekończącą się przewijaną listę. Użytkownik widzi najpierw jedną metrykę, potem jej obszerny opis rynkowy, a dopiero głęboko na dole kolejną metrykę. Całkowicie niszczy to możliwość szybkiego, zbiorczego porównania parametrów "jednym rzutem oka".
3. **Zatarcie Hierarchii Tytułów:**
   - Zmniejszenie czcionki głównego tytułu z `30px` do `15px` powoduje, że staje się on mniejszy niż podnagłówki sekcji (`20px`), co wywraca hierarchię ważności informacji do góry nogami.

---

## 10 Głównych Rekomendacji UX (Skorygowane o Prawa UX)

Poniżej znajduje się 10 precyzyjnych i natychmiastowych zaleceń wdrożeniowych dla dewelopera (Codera), mających na celu doprowadzenie dashboardu do standardu produkcyjnego premium.

### 1. Przywrócenie prawidłowej hierarchii czytania (Serial Position Effect / Jakob's Law)
- **Problem:** Pasek kontrolny `ctrl_cols` (wybór zakresu czasowego oraz przycisk "Odśwież") znajduje się nad głównym nagłówkiem strony w kodzie pierwszej zakładki, co zaburza strukturę czytania od góry do dołu.
- **Instrukcja dla Kodera:** Wewnątrz `with tab_risk:` należy przenieść blok kodu odpowiedzialny za definicję i renderowanie `ctrl_cols` (linie z `st.columns([3, 1])` dla czasu i przycisku) bezpośrednio *poniżej* kodu generującego główny nagłówek strony (`cxr-header-group`). Nagłówek z ikoną 📊 musi być bezwzględnie pierwszym elementem widocznym na ekranie.

### 2. Korekta minimalnych rozmiarów czcionek na mobile (Hick's Law / Dostępność / WCAG)
- **Problem:** Czcionki o rozmiarze `8px` i `10px` na urządzeniach mobilnych uniemożliwiają wygodną konsumpcję danych.
- **Instrukcja dla Kodera:** Wewnątrz bloku `<style>`, w sekcji `@media (max-width: 640px)`, należy zmodyfikować reguły CSS, zmieniając:
  - `.uxr-metric-title` z `font-size: 8px !important;` na `font-size: 11px !important;`
  - `.uxr-metric-value` z `font-size: 16px !important;` na `font-size: 18px !important;`
  - `.cxr-title` z `font-size: 15px !important;` na `font-size: 18px !important;`
  - `div[data-testid="stTable"] th, div[data-testid="stTable"] td` z `font-size: 10px !important;` na `font-size: 12px !important;`

### 3. Konsolidacja rozproszonych expanderów edukacyjnych (Law of Proximity / Column Stacking)
- **Problem:** Pojedyncze expandery pod każdym kaflem KPI tworzą chaos i wymuszają przewijanie ekranu na mobile.
- **Instrukcja dla Kodera:** 
  1. Usunąć bloki `with st.expander("ℹ️ Poziomy")` oraz `with st.expander("ℹ️ WPŁYW")` znajdujące się wewnątrz pętli generującej kolumny kafli KPI.
  2. Przenieść te informacje do jednego, zbiorczego expandera edukacyjnego umieszczonego pod sekcją kafli, łącząc je z istniejącym już przewodnikiem interpretacji wskaźników technicznych. Dzięki temu metryki będą stały bezpośrednio obok siebie, co ułatwi ich porównywanie.

### 4. Ujednolicenie designu tabel (Law of Similarity / Aesthetic-Usability Effect)
- **Problem:** Tabela w Zakładce 1 jest silnie ostylowana w czystym HTML/CSS, natomiast Tabela w Zakładce 2 (`st.dataframe`) ma surowy, domyślny wygląd Streamlit, co psuje wrażenie spójności aplikacji premium.
- **Instrukcja dla Kodera:** Zamiast domyślnego komponentu `st.dataframe` w Zakładce 2, należy wykorzystać stylizację HTML zbliżoną do Zakładki 1 lub dodać globalną regułę CSS nadpisującą tła, nagłówki i czcionki dla kontenerów tabelarycznych Streamlit za pomocą selektorów `div[data-testid="stDataFrame"]` lub `div[data-testid="stTable"]`, aby obie tabele miały ten sam kolor wierszy parzystych/nieparzystych, czcionkę Poppins oraz identyczne obramowanie.

### 5. Optymalizacja wyboru zakresu czasowego (Fitts's Law / Hick's Law)
- **Problem:** Standardowy `st.selectbox` wymaga dwóch interakcji (rozwiń -> kliknij) i ukrywa alternatywny wybór przed wzrokiem użytkownika.
- **Instrukcja dla Kodera:** Zastąpić komponent `st.selectbox("Przedział czasowy analizy", ...)` za pomocą poziomego przełącznika radiowego `st.radio(..., horizontal=True)` lub nowszego `st.segmented_control` (jeśli biblioteka na to pozwala). Umieszczenie opcji bezpośrednio na ekranie skraca czas reakcji (Hick's Law) i zmniejsza wysiłek fizyczny potrzebny do zmiany widoku (Fitts's Law).

### 6. Zwiększenie kontrastu semantycznego alertów statusu (Jakob's Law)
- **Problem:** Limonkowy zielony `#cde200` (pozytywny) i neonowy żółty `#ecfa64` (ostrzeżenie) są zbyt blisko siebie w spektrum barwnym, co spowalnia rozpoznawanie stanów rynku przez tradera.
- **Instrukcja dla Kodera:** 
  - W klasach CSS `.uxr-metric-card-positive` oraz `.uxr-metric-delta-positive` zmienić kolor z `#cde200` na żywszą, standardową zieleń giełdową: `#2ecc71` lub `#00e676`.
  - W klasie `.cxr-alert-green` zmienić `border-left-color: #cde200 !important;` na `border-left-color: #2ecc71 !important;`.
  - Dzięki temu utrzymujemy wyraźny podział: zielony = spokój/wzrosty, żółto-neonowy = uwaga, pomarańczowy = ryzyko, czerwony = niebezpieczeństwo.

### 7. Dodanie głębi wizualnej do kart metryk (Aesthetic-Usability Effect)
- **Problem:** Karty metryk posiadają płaskie, jednokolorowe tło `#1f2b40` i grube lewe obramowanie, co nadaje im nieco przestarzały charakter.
- **Instrukcja dla Kodera:** Zmodyfikować klasę CSS `.uxr-metric-card` dodając do niej delikatny gradient liniowy tła oraz subtelną poświatę (cień zewnętrzny):
  ```css
  .uxr-metric-card {
      background: linear-gradient(135deg, #1f2b40 0%, #172030 100%) !important;
      border: 1px solid rgba(255, 255, 255, 0.03) !important;
      border-left: 6px solid #DCDCDC !important; /* nieznacznie cieńsza linia */
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
  }
  ```
  Zabieg ten nada kartom nowoczesny, szklany wygląd (glassmorphism/depth layer) zgodny z estetyką interfejsów premium.

### 8. Zapobieganie nachodzeniu legendy Plotly na ekranach mobilnych (Miller's Law / Responsywność)
- **Problem:** Pozioma legenda wykresu Plotly zawierająca aż 7 pozycji nakłada się na dane wykresu na ekranach telefonów o szerokości poniżej 640px.
- **Instrukcja dla Kodera:** In Plotly `fig.update_layout` dodać mechanizm, który wykrywa szerokość okna lub upraszcza legendę. Alternatywnie, ustawić pozycję legendy pod wykresem w układzie kolumnowym dla lepszej czytelności na smartfonach, modyfikując parametry layoutu:
  ```python
  fig.update_layout(
      legend=dict(
          orientation="h",
          yanchor="top",
          y=-0.2, # Przeniesienie legendy pod wykres
          xanchor="center",
          x=0.5
      )
  )
  ```

### 9. Wprowadzenie wskaźnika świeżości danych (Hick's Law / Redukcja Niepewności)
- **Problem:** Przycisk odświeżania danych nie informuje użytkownika o tym, jak stare są aktualnie wyświetlane dane, dopóki nie spojrzy on na dół strony na stopkę. To zmusza do szukania informacji (cognitive overhead).
- **Instrukcja dla Kodera:** Bezpośrednio obok przycisków odświeżania ("🔄 Odśwież dane" w Zakładce 1 oraz "🔄 Odśwież LPP" w Zakładce 2) dodać mały, jasnoszary podpis tekstowy informujący o dacie ostatniej udanej aktualizacji (np. `Ostatni odczyt: 14:32:05`). Można to osiągnąć, umieszczając przycisk i informację w jednej kolumnie przy użyciu `st.caption`.

### 10. Pełne ujednolicenie struktury i estetyki nagłówków zakładek (Law of Similarity)
- **Problem:** Zakładka 2 ("LPP S.A.") nie posiada podziału na kolumny w nagłówku, przez co brakuje w niej zegara systemowego z czasem warszawskim, który jest obecny w Zakładce 1. Tworzy to niespójność funkcjonalną.
- **Instrukcja dla Kodera:** Przebudować strukturę nagłówka w Zakładki 2, odwzorowując rozwiązanie z Zakładki 1. Zastosować podział na kolumny:
  ```python
  header_col1_lpp, header_col2_lpp = st.columns([4, 1])
  with header_col1_lpp:
      # Renderowanie cxr-header-group dla LPP
  with header_col2_lpp:
      # Renderowanie zegara systemowego (⏱️ get_poland_time().strftime('%H:%M:%S'))
  ```
  Dzięki temu nawigacja między zakładkami będzie płynna, a elementy kontrolne i informacyjne znajdą się dokładnie w tych samych miejscach na ekranie.
