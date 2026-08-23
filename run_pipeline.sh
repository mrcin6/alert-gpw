#!/bin/bash

# Multi-Agent Developer-Audit Loop Orchestration Script
# Custom-built for Alert GPW & LPP Dashboard

MAX_ITER=5
ITER=1
SCORE_QA=1

# ANSI Color Codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== 🤖 INICJALIZACJA WIELOAGENTOWEJ PĘTLI DEWELOPERSKIEJ ===${NC}"
echo -e "${BLUE}Cel: Osiągnięcie poziomu jakości SCORE >= 4 dla Dashboardu GPW & LPP S.A.${NC}\n"

# Backup original app.py before the pipeline begins
if [ -f app.py ] && [ ! -f app_backup.py ]; then
  echo -e "${YELLOW}[Backup] Tworzenie kopii zapasowej app.py jako app_backup.py...${NC}"
  cp app.py app_backup.py
fi

while [ "$SCORE_QA" -lt 4 ] && [ "$ITER" -le "$MAX_ITER" ]; do
  echo -e "\n${CYAN}================================================================${NC}"
  echo -e "${CYAN}   🔄 ITERACJA $ITER z $MAX_ITER${NC}"
  echo -e "${CYAN}================================================================${NC}"

  # ----------------------------------------------------------------
  # 1. STRATEGY PO AGENT
  # ----------------------------------------------------------------
  echo -e "${YELLOW}[1/6] Strategy PO Agent: Definiowanie celów i polityki ryzyka...${NC}"
  
  # Przygotowanie pliku wejściowego (system prompt + kontekst)
  cat .gemini/prompts/strategy_po_prompt.md > temp_po_ctx.txt
  echo -e "\n\n### WEJŚCIOWY KONTEKST STRATEGICZNY (config/strategy.json):\n" >> temp_po_ctx.txt
  cat config/strategy.json >> temp_po_ctx.txt
  echo -e "\n\n### POPRZEDNI RAPORT JAKOŚCI (EVAL.md):\n" >> temp_po_ctx.txt
  if [ -f EVAL.md ]; then
    cat EVAL.md >> temp_po_ctx.txt
  else
    echo "Brak poprzednich raportów. To jest pierwsza iteracja." >> temp_po_ctx.txt
  fi
  
  # Wykonanie zapytania i zapisanie rezultatu
  gemini -p "Zaktualizuj i wygeneruj nową treść pliku PORTFOLIO_STRATEGY.md na podstawie powyższych instrukcji i danych wejściowych." < temp_po_ctx.txt 2>/dev/null > PORTFOLIO_STRATEGY.md
  rm temp_po_ctx.txt
  echo -e "${GREEN}[✔] PORTFOLIO_STRATEGY.md został zaktualizowany.${NC}"

  # ----------------------------------------------------------------
  # 2. DATA & API RESEARCHER
  # ----------------------------------------------------------------
  echo -e "${YELLOW}[2/6] Data & API Researcher: Specyfikacja źródeł danych i odporności API...${NC}"
  
  cat .gemini/prompts/tech_researcher_prompt.md > temp_researcher_ctx.txt
  echo -e "\n\n### LISTA OBSERWOWANYCH AKTYWÓW (config/watchlist.json):\n" >> temp_researcher_ctx.txt
  cat config/watchlist.json >> temp_researcher_ctx.txt
  echo -e "\n\n### DOTYCHCZASOWA STRATEGIA BIZNESOWA (PORTFOLIO_STRATEGY.md):\n" >> temp_researcher_ctx.txt
  cat PORTFOLIO_STRATEGY.md >> temp_researcher_ctx.txt
  
  gemini -p "Opracuj pełną architekturę integracji i zapisz ją w DATA_SOURCES.md na podstawie powyższych danych." < temp_researcher_ctx.txt 2>/dev/null > DATA_SOURCES.md
  rm temp_researcher_ctx.txt
  echo -e "${GREEN}[✔] DATA_SOURCES.md został zaktualizowany.${NC}"

  # ----------------------------------------------------------------
  # 3. FINANCIAL SME (SUBJECT MATTER EXPERT)
  # ----------------------------------------------------------------
  echo -e "${YELLOW}[3/6] Financial SME: Tworzenie wzorów matematycznych i reguł analitycznych...${NC}"
  
  cat .gemini/prompts/financial_expert_prompt.md > temp_expert_ctx.txt
  echo -e "\n\n### ARCHITEKTURA INTEGRACJI DANYCH (DATA_SOURCES.md):\n" >> temp_expert_ctx.txt
  cat DATA_SOURCES.md >> temp_expert_ctx.txt
  
  gemini -p "Zdefiniuj reguły matematyczne, wskaźniki techniczne i sentymentu w ANALYSIS_RULES.md." < temp_expert_ctx.txt 2>/dev/null > ANALYSIS_RULES.md
  rm temp_expert_ctx.txt
  echo -e "${GREEN}[✔] ANALYSIS_RULES.md został zaktualizowany.${NC}"

  # ----------------------------------------------------------------
  # 4. QUANT & CODER AGENT
  # ----------------------------------------------------------------
  echo -e "${YELLOW}[4/6] Quant & Coder Agent: Aktualizacja kodu app.py...${NC}"
  
  cat .gemini/prompts/coder_prompt.md > temp_coder_ctx.txt
  echo -e "\n\n### REGULY ANALITYCZNE (ANALYSIS_RULES.md):\n" >> temp_coder_ctx.txt
  cat ANALYSIS_RULES.md >> temp_coder_ctx.txt
  echo -e "\n\n### RAPORT WALIDACJI (EVAL.md):\n" >> temp_coder_ctx.txt
  if [ -f EVAL.md ]; then
    cat EVAL.md >> temp_coder_ctx.txt
  else
    echo "To jest pierwsza iteracja. Brak raportu błędów. Zaimplementuj lub dostosuj kod zgodnie z regułami analitycznymi." >> temp_coder_ctx.txt
  fi
  echo -e "\n\n### AKTUALNA TREŚĆ APP.PY:\n" >> temp_coder_ctx.txt
  cat app.py >> temp_coder_ctx.txt
  
  gemini -p "Wygeneruj kompletny, zaktualizowany kod źródłowy pliku app.py. Nie używaj znaczników markdown (\`\`\`), wypisz wyłącznie czysty kod Python." < temp_coder_ctx.txt 2>/dev/null > app_temp.py
  rm temp_coder_ctx.txt
  
  # Walidacja czy wyjściowy plik nie jest pusty
  if [ -s app_temp.py ]; then
    mv app_temp.py app.py
    echo -e "${GREEN}[✔] app.py został pomyślnie zaktualizowany przez programistę.${NC}"
  else
    echo -e "${RED}[❌] Błąd: Programista zwrócił pusty kod! Przywracam dotychczasowy stan...${NC}"
    rm -f app_temp.py
  fi

  # ----------------------------------------------------------------
  # 5. UX & DASHBOARD AGENT
  # ----------------------------------------------------------------
  echo -e "${YELLOW}[5/6] UX & Dashboard Agent: Audyt interfejsu i czytelności danych...${NC}"
  
  cat .gemini/prompts/ux_prompt.md > temp_ux_ctx.txt
  echo -e "\n\n### KOD PROGRAMU (app.py):\n" >> temp_ux_ctx.txt
  cat app.py >> temp_ux_ctx.txt
  
  gemini -p "Przeprowadź audyt UX i czytelności na podstawie kodu źródłowego i zapisz raport w UX_AUDIT.md." < temp_ux_ctx.txt 2>/dev/null > UX_AUDIT.md
  rm temp_ux_ctx.txt
  echo -e "${GREEN}[✔] UX_AUDIT.md został zaktualizowany.${NC}"

  # ----------------------------------------------------------------
  # 6. QA & RISK AUDITOR
  # ----------------------------------------------------------------
  echo -e "${YELLOW}[6/6] QA & Risk Auditor: Weryfikacja kodu i ocena bramki jakości...${NC}"
  
  cat .gemini/prompts/qa_prompt.md > temp_qa_ctx.txt
  echo -e "\n\n### REGULY ANALITYCZNE (ANALYSIS_RULES.md):\n" >> temp_qa_ctx.txt
  cat ANALYSIS_RULES.md >> temp_qa_ctx.txt
  echo -e "\n\n### AUDYT UX (UX_AUDIT.md):\n" >> temp_qa_ctx.txt
  cat UX_AUDIT.md >> temp_qa_ctx.txt
  echo -e "\n\n### KOD PROGRAMU DO AUDYTU (app.py):\n" >> temp_qa_ctx.txt
  cat app.py >> temp_qa_ctx.txt
  
  gemini -p "Przeprowadź końcowy audyt i zapisz SCORE oraz STATUS w EVAL.md." < temp_qa_ctx.txt 2>/dev/null > EVAL.md
  rm temp_qa_ctx.txt
  echo -e "${GREEN}[✔] EVAL.md został zaktualizowany.${NC}"

  # ----------------------------------------------------------------
  # ODCZYT OCENY BRAMKI JAKOŚCI (Mac/Linux compatible)
  # ----------------------------------------------------------------
  SCORE_QA=$(grep -i "SCORE:" EVAL.md | tr -cd '1-5' | head -c 1)
  
  if [ -z "$SCORE_QA" ]; then
    SCORE_QA=1
  fi
  
  STATUS_QA=$(grep -i "STATUS:" EVAL.md | awk '{print $2}' | tr -d '\r\n')
  
  echo -e "\n${BLUE}--- WYNIK ITERACJI $ITER ---${NC}"
  echo -e "Ocena QA: ${YELLOW}$SCORE_QA / 5${NC}"
  echo -e "Status Bramki: ${YELLOW}$STATUS_QA${NC}"

  if [ "$SCORE_QA" -ge 4 ]; then
    echo -e "${GREEN}🎉 SUKCES: Projekt spełnia wysokie wymagania jakościowe (SCORE: $SCORE_QA >= 4).${NC}"
    echo -e "${GREEN}Zamykam pętlę deweloperską z powodzeniem!${NC}"
    break
  else
    echo -e "${RED}⚠️ REJECTED: Wynik $SCORE_QA < 4 jest niewystarczający.${NC}"
    echo -e "${YELLOW}Przechodzę do kolejnej iteracji i przekazuję listę DELTA do poprawek...${NC}"
    ((ITER++))
  fi
done

if [ "$ITER" -gt "$MAX_ITER" ] && [ "$SCORE_QA" -lt 4 ]; then
  echo -e "\n${RED}❌ OSTRZEŻENIE: Przekroczono limit iteracji ($MAX_ITER) bez osiągnięczenia celu jakościowego (SCORE: $SCORE_QA/5).${NC}"
fi
