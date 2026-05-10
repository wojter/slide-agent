# Dokument wymagań produktu (PRD) - SlideAgent

## 1. Przegląd produktu

SlideAgent to narzędzie CLI automatyzujące generowanie grafik do prezentacji biznesowych. System analizuje prezentację w formacie Markdown, autonomicznie decyduje które slajdy wymagają grafiki, generuje je z wykorzystaniem AI i ocenia jakość, zwracając gotowy plik .pptx.

Produkt jest Proof of Concept (PoC) realizowanym jako prywatny projekt jednoosobowy. Celem jest walidacja koncepcji automatyzacji procesu tworzenia grafik prezentacyjnych z zachowaniem spójności wizualnej i kontrolą jakości.

Kluczowe założenia techniczne:
- Model LLM: GPT-5-nano (faza testowa), z możliwością eskalacji do droższego modelu
- Generator obrazów: gpt-image-generation (OpenAI SDK), docelowo migracja na alternatywny provider
- Orkiestracja: LangGraph z równoległością max 5 slajdów
- Output: plik .pptx z wstawionymi grafikami i tekstem
- Tracing: integracja z zewnętrznym narzędziem (LangSmith/Langfuse)

## 2. Problem użytkownika

Tworzenie prezentacji biznesowych jest czasochłonne ze względu na konieczność ręcznego wyszukiwania lub promptowania grafik dla każdego slajdu.

Istniejące rozwiązania generatywne AI:
- Wymagają ręcznego promptowania per slajd
- Nie zapewniają spójności wizualnej między slajdami
- Nie posiadają mechanizmu oceny jakości wygenerowanych grafik
- Przerzucają na użytkownika decyzję o akceptowalności wyniku

SlideAgent rozwiązuje te problemy poprzez:
- Automatyczną analizę prezentacji i decyzję o potrzebie grafiki per slajd
- Globalny styl wizualny zapewniający spójność całego decku
- Wbudowany Visual Critic oceniający jakość grafik
- Automatyczny retry loop z feedbackiem przy negatywnej ocenie
- Zwrot gotowego pliku .pptx bez dalszej interwencji użytkownika

## 3. Wymagania funkcjonalne

### 3.1 Parser Markdown

| ID | Wymaganie |
|----|-----------|
| F-001 | Parser rozbija prezentację na osobne slajdy po separatorze `---` |
| F-002 | Rozpoznaje tytuł slajdu oznaczony `##` |
| F-003 | Rozpoznaje punkty treści oznaczone `###` lub listą `-` |
| F-004 | Wykrywa komentarze/wskazówki w sekcji `##` (informacje dla agenta, speaker notes) |
| F-005 | Zapisuje rozparsowane slajdy jako `slide_01.md`, `slide_02.md`, etc. |

### 3.2 Generation Agent

| ID | Wymaganie |
|----|-----------|
| F-006 | Decyduje per slajd: skip (rozbudowana treść) vs generate (tylko tytuł lub komentarze) |
| F-007 | Tworzy prompt graficzny w języku angielskim |
| F-008 | Używa globalnego stylu wizualnego (hardcoded w system prompt) |
| F-009 | Reaguje na feedback Visual Critic i modyfikuje prompt przy retry |
| F-010 | Uwzględnia komentarze/wskazówki ze slajdu przy generowaniu promptu |

### 3.3 Image Generator

| ID | Wymaganie |
|----|-----------|
| F-011 | Integracja z gpt-image-generation (OpenAI SDK) |
| F-012 | Generuje obrazy w najniższej dostępnej rozdzielczości (faza testowa) |
| F-013 | Abstrakcja providera umożliwiająca przyszłą migrację |

### 3.4 Visual Critic

| ID | Wymaganie |
|----|-----------|
| F-014 | Ocenia jakość wygenerowanej grafiki: pass/fail |
| F-015 | Weryfikuje poprawność tekstu na obrazie (brak literówek, krzaków) |
| F-016 | Ocenia trafność semantyczną grafiki względem treści slajdu |
| F-017 | Sprawdza czytelność i brak artefaktów wizualnych |
| F-018 | Dostarcza feedback przy ocenie negatywnej (do retry loop) |

### 3.5 Retry Loop

| ID | Wymaganie |
|----|-----------|
| F-019 | Automatyczna regeneracja przy ocenie negatywnej Visual Critic |
| F-020 | Maksymalnie 3 próby per slajd |
| F-021 | Przy 3x fail: użyj ostatniej wygenerowanej grafiki jako fallback |
| F-022 | Zapisz wszystkie próby (pass i fail) do folderu output |

### 3.6 Orkiestracja

| ID | Wymaganie |
|----|-----------|
| F-023 | LangGraph StateGraph z kontrolą przepływu |
| F-024 | Równoległa obróbka max 5 slajdów jednocześnie |
| F-025 | State per slajd: id, title, content, comment, decision, prompt, attempts, final_image, status |

### 3.7 PPTX Output

| ID | Wymaganie |
|----|-----------|
| F-026 | Generuje plik .pptx z wstawionymi grafikami i tekstem |
| F-027 | Layout: tytuł góra + grafika pełna szerokość pod spodem |
| F-028 | Obsługuje slajdy bez tytułu (pełna grafika) |
| F-029 | Obsługuje slajdy tylko z tekstem (skip grafiki) |
| F-030 | Oparty na bazowym szablonie .pptx (master slide) |

### 3.8 Zapis wyników

| ID | Wymaganie |
|----|-----------|
| F-031 | Struktura folderów per slajd w output |
| F-032 | Każdy folder zawiera: slide.md, decision.json, attempt_*.png |
| F-033 | decision.json zawiera: prompt, decyzję, oceny Visual Critic per próba, status |
| F-034 | Finalny plik presentation.pptx w katalogu output |

### 3.9 CLI

| ID | Wymaganie |
|----|-----------|
| F-035 | Komenda `slideagent parse` do parsowania prezentacji |
| F-036 | Komenda `slideagent run` do pełnego pipeline'u |

### 3.10 Tracing

| ID | Wymaganie |
|----|-----------|
| F-037 | Integracja z zewnętrznym narzędziem do logowania wywołań LLM |
| F-038 | Podstawowa obserwowalność: input/output każdego agenta |

## 4. Granice produktu

### W zakresie MVP

- Agent zarządzający workflowem
- Parser Markdown
- Generation Agent z decyzją skip/generate
- Image Generator (gpt-image-generation)
- Visual Critic z oceną pass/fail
- Retry loop (max 3 próby)
- Orkiestracja równoległa LangGraph (max 5 slajdów)
- PPTX output z szablonem
- Zapis wyników etapów do folderów
- CLI (parse, run)
- Tracing do zewnętrznego narzędzia
- Języki: polski (treść), angielski (prompty graficzne)

### Poza zakresem MVP

- Web UI / SaaS / multi-tenant
- Plugin do PowerPoint / Google Slides
- 3 propozycje grafik per slajd (tylko 1 w MVP)
- Multi-provider generacji (FLUX, Ideogram)
- Brand compliance CV (paleta, fonty, logo)
- Deterministic quality checks (OCR)
- HTML preview / interactive mode
- Checkpointing i resume po crashu
- MCP servers
- Historia runów / versionowanie
- Generowanie struktury/tekstu prezentacji
- Generowanie wykresów i infografik
- Integracje (SharePoint, Drive, Slack)
- Mobile i offline mode
- Cache wyników między runami
- Obsługa istniejących obrazów/linków w MD
- Wybór slajdów do generacji (--slides)
- Force/skip znaczniki w MD

## 5. Historyjki użytkowników

### US-001: Parsowanie prezentacji Markdown

Tytuł: Parsowanie prezentacji na slajdy

Opis: Jako użytkownik chcę rozparsować plik Markdown z prezentacją na osobne pliki per slajd, aby móc przejrzeć strukturę przed generowaniem grafik.

Kryteria akceptacji:
- Komenda `slideagent parse input.md` tworzy folder output
- Każdy slajd zapisany jako `slide_01.md`, `slide_02.md`, etc.
- Slajdy rozdzielone po separatorze `---`
- Tytuł slajdu (`##`) poprawnie rozpoznany
- Treść slajdu (`###`, `-`) poprawnie rozpoznana
- Komentarze/wskazówki wykryte i zapisane
- Pusty slajd (sam separator) traktowany jako slajd bez tytułu

### US-002: Generowanie prezentacji z grafikami

Tytuł: Uruchomienie pełnego pipeline generacji

Opis: Jako użytkownik chcę uruchomić pełny proces generowania grafik dla prezentacji, aby otrzymać gotowy plik .pptx.

Kryteria akceptacji:
- Komenda `slideagent run input.md` uruchamia pełny pipeline
- System parsuje prezentację na slajdy
- Generation Agent decyduje per slajd: skip lub generate
- Dla slajdów z decyzją generate: grafika jest generowana
- Visual Critic ocenia każdą grafikę
- Przy fail: automatyczny retry (max 3 próby)
- Finalny plik `presentation.pptx` w folderze output
- Plik otwiera się w PowerPoint i LibreOffice bez błędów

### US-003: Automatyczna decyzja o grafice

Tytuł: Decyzja skip/generate per slajd

Opis: Jako użytkownik chcę, aby agent autonomicznie decydował które slajdy potrzebują grafiki, abym nie musiał ręcznie oznaczać każdego slajdu.

Kryteria akceptacji:
- Slajd z tylko tytułem → decyzja generate
- Slajd z tytułem i komentarzem/wskazówką → decyzja generate (prompt na podstawie komentarza)
- Slajd z rozbudowaną treścią (bulletów) → decyzja skip
- Slajd bez tytułu z komentarzem → decyzja generate (pełna grafika)
- Decyzja zapisana w decision.json

### US-004: Generowanie promptu graficznego

Tytuł: Tworzenie promptu dla Image Generator

Opis: Jako użytkownik chcę, aby Generation Agent tworzył trafne prompty graficzne w języku angielskim, zachowując spójność stylu.

Kryteria akceptacji:
- Prompt wygenerowany w języku angielskim
- Prompt uwzględnia treść/tytuł slajdu
- Prompt uwzględnia komentarze/wskazówki jeśli obecne
- Prompt zawiera globalny styl wizualny
- Prompt zapisany w decision.json

### US-005: Ocena jakości grafiki

Tytuł: Visual Critic ocenia wygenerowaną grafikę

Opis: Jako użytkownik chcę, aby Visual Critic automatycznie oceniał jakość grafik, abym otrzymał tylko akceptowalne wyniki.

Kryteria akceptacji:
- Visual Critic otrzymuje: obraz, prompt, treść slajdu
- Ocena pass: grafika akceptowana
- Ocena fail: szczegółowy feedback (co jest nie tak)
- Weryfikacja poprawności tekstu na obrazie
- Weryfikacja trafności semantycznej
- Weryfikacja braku artefaktów
- Wynik oceny zapisany w decision.json

### US-006: Retry przy negatywnej ocenie

Tytuł: Automatyczna regeneracja grafiki

Opis: Jako użytkownik chcę, aby przy negatywnej ocenie Visual Critic system automatycznie ponowił generację z poprawionym promptem.

Kryteria akceptacji:
- Przy fail: feedback przekazany do Generation Agent
- Generation Agent modyfikuje prompt na podstawie feedbacku
- Nowa grafika generowana
- Maksymalnie 3 próby per slajd
- Każda próba zapisana jako `attempt_1.png`, `attempt_2.png`, etc.
- Po 3x fail: użyta ostatnia grafika jako fallback

### US-007: Równoległa obróbka slajdów

Tytuł: Równoczesna generacja dla wielu slajdów

Opis: Jako użytkownik chcę, aby system przetwarzał wiele slajdów równolegle, aby skrócić czas generacji.

Kryteria akceptacji:
- Maksymalnie 5 slajdów przetwarzanych jednocześnie
- Każdy slajd niezależnie przechodzi przez pipeline
- Błąd jednego slajdu nie blokuje pozostałych
- Stan każdego slajdu śledzony w orchestratorze

### US-008: Slajd tylko z tekstem

Tytuł: Obsługa slajdów bez grafiki

Opis: Jako użytkownik chcę, aby slajdy z rozbudowaną treścią trafiały do prezentacji tylko z tekstem, bez generowania grafiki.

Kryteria akceptacji:
- Generation Agent decyduje skip dla slajdów z dużą ilością treści
- Slajd w PPTX zawiera tytuł i treść tekstową
- Brak placeholdera graficznego
- decision.json zawiera `decision: "skip"`

### US-009: Slajd z pełną grafiką

Tytuł: Obsługa slajdów bez tytułu

Opis: Jako użytkownik chcę, aby slajdy bez tytułu (lub z samą wskazówką) miały grafikę na pełnym slajdzie.

Kryteria akceptacji:
- Slajd bez nagłówka `##` rozpoznany
- Jeśli zawiera komentarz: generuj grafikę na jego podstawie
- Grafika zajmuje pełny slajd w PPTX
- Brak pola tekstowego na slajdzie

### US-010: Zapis wyników etapów

Tytuł: Struktura folderów z wynikami

Opis: Jako użytkownik chcę mieć dostęp do wyników każdego etapu pipeline, abym mógł debugować i analizować proces.

Kryteria akceptacji:
- Folder output utworzony przy uruchomieniu
- Podfolder per slajd: `01/`, `02/`, etc.
- Każdy folder zawiera: `slide.md`, `decision.json`, `attempt_*.png`
- decision.json zawiera: prompt, decyzję, oceny per próba, status
- Wszystkie grafiki (pass i fail) zachowane

### US-011: Obsługa błędów generacji

Tytuł: Fallback przy niepowodzeniu wszystkich prób

Opis: Jako użytkownik chcę, aby przy niepowodzeniu wszystkich 3 prób system użył ostatniej grafiki jako fallback, aby prezentacja była kompletna.

Kryteria akceptacji:
- Po 3x fail Visual Critic: ostatnia grafika użyta w PPTX
- Status w decision.json: `status: "fallback"`
- Wszystkie 3 próby zapisane w folderze
- Pipeline kontynuuje dla pozostałych slajdów
- Użytkownik może ręcznie przejrzeć i podmienić grafikę

### US-012: Tracing wywołań LLM

Tytuł: Logowanie do zewnętrznego narzędzia

Opis: Jako użytkownik chcę mieć obserwowalność wywołań LLM w zewnętrznym narzędziu, abym mógł debugować i optymalizować prompty.

Kryteria akceptacji:
- Każde wywołanie LLM logowane
- Input i output agenta widoczny w narzędziu
- Czas wykonania rejestrowany
- Koszty per wywołanie widoczne (jeśli narzędzie wspiera)

### US-013: Walidacja pliku wejściowego

Tytuł: Obsługa niepoprawnego pliku Markdown

Opis: Jako użytkownik chcę otrzymać czytelny komunikat błędu gdy plik wejściowy jest niepoprawny.

Kryteria akceptacji:
- Brak pliku: błąd "File not found: {path}"
- Pusty plik: błąd "Empty input file"
- Brak separatorów `---`: ostrzeżenie "No slide separators found, treating as single slide"
- Błąd parsowania: szczegółowy komunikat z linią problemu

### US-014: Konfiguracja globalnego stylu

Tytuł: Styl wizualny w agencie

Opis: Jako użytkownik chcę, aby wszystkie grafiki były generowane w spójnym stylu wizualnym.

Kryteria akceptacji:
- Globalny styl hardcoded w system prompt Generation Agent
- Styl aplikowany do każdego promptu graficznego
- Grafiki zachowują spójność wizualną między slajdami

## 6. Metryki sukcesu

| Metryka | Target | Sposób mierzenia |
|---------|--------|------------------|
| PPTX validity | 100% | Automatyczny test: otwieranie w LibreOffice i PowerPoint bez błędów |
| Crash rate | < 1% | Telemetria z zewnętrznego narzędzia logowania |
| Czas generacji 10-slide deck | < 5 min (p95) | Timestamp start/end w logach, percentyl z próbek |
| Koszt 10-slide deck | < 2$ | Sumowanie kosztów z API responses (LLM + Image Gen) |
| Pass rate Visual Critic | >= 70% | Licznik: pass na pierwszej próbie / total slajdów z decyzją generate |

### Dodatkowe metryki operacyjne (do śledzenia)

| Metryka | Opis |
|---------|------|
| Średnia liczba prób per slajd | Ile prób potrzeba do uzyskania pass |
| Fallback rate | % slajdów gdzie użyto ostatniej grafiki po 3x fail |
| Skip rate | % slajdów z decyzją skip (bez grafiki) |
| Średni czas per slajd | Czas od rozpoczęcia do zakończenia obróbki slajdu |
| Koszt per slajd | Średni koszt API per slajd |
