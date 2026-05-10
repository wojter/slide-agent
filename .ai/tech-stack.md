# Tech Stack - SlideAgent PoC

## Język i runtime

- **Python 3.12+**
- **uv** — zarządzanie zależnościami i venv (szybki, zastępuje pip+poetry)

## Orkiestracja

- **LangGraph** — StateGraph z kontrolą przepływu
  - `Send()` API do równoległego przetwarzania slajdów (fan-out/fan-in)
  - Conditional edges do retry loop (max 3 próby)
  - State per slajd zarządzany przez reducery (`Annotated[list, operator.add]`)
  - Nodes to zwykłe funkcje Pythona — bez wrapperów `langchain-openai`
  - Uwaga: LangGraph wymaga `langchain-core` jako transitive dependency (lekka, ~bazowe typy i interfejsy)

## LLM i generowanie obrazów

- **OpenAI SDK** (bezpośrednio, bez `langchain-openai` / `ChatOpenAI` wrapperów)
  - Generation Agent (decyzja + prompt): `gpt-5-nano` — tani, szybki, wystarczający do decyzji skip/generate i tworzenia promptów
  - Visual Critic (ocena obrazu): `gpt-5-nano` — obsługuje vision (analiza obrazu), wystarczający do oceny pass/fail; eskalacja do droższego modelu jeśli pass rate < 70%
  - Image generation: `client.images.generate()` z modelem `gpt-image-2` (najnowszy, lepsza jakość tekstu na obrazach)
  - Abstrakcja providera: prosty protokół/ABC dla image generator, umożliwiający przyszłą migrację

## Tracing / Obserwowalność

- **LangSmith** (free tier — 5k traces/miesiąc, 1 seat) — start na PoC
  - Zero-config z LangGraph: `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY`
  - Input/output każdego node'a, czas wykonania, koszty
  - Nie wymaga dodatkowego kodu — automatyczna instrumentacja
  - Migracja na **Langfuse** (open source, 50k obs/msc free, self-hosted) możliwa w ~10 min:
    `pip install langfuse` + `CallbackHandler()` + zmiana env vars

## CLI

- **Typer** — minimalny boilerplate, auto-generowany help, type hints
  - `slideagent parse input.md`
  - `slideagent run input.md`

## Generowanie PPTX

- **python-pptx** — jedyna dojrzała biblioteka w Pythonie
  - Obsługa szablonów (.pptx master slide)
  - Wstawianie obrazów i tekstu

## Modele danych i walidacja

- **Pydantic v2** — walidacja state, serializacja decision.json, structured output z OpenAI

## Markdown parser

- **Własna implementacja** (regex/str.split) — format jest prosty (`---`, `##`, `###`, `-`), nie potrzeba zewnętrznej biblioteki

## Zależności (requirements)

```
langgraph
openai
python-pptx
typer
pydantic
langsmith
```

## Decyzje architektoniczne

1. **OpenAI SDK bezpośrednio, nie przez LangChain wrappers** — mniej abstrakcji, pełna kontrola nad API calls, łatwiejszy debug
2. **LangGraph z minimalnym użyciem LangChain** — nodes to plain Python functions z OpenAI SDK; `langchain-core` jest wymagany jako transitive dep, ale nie używamy `ChatOpenAI` ani innych wrapperów
3. **LangSmith na start, Langfuse jako opcja docelowa** — LangSmith = zero-config na PoC; Langfuse = open source, self-hosted, większy free tier; migracja trywialna
4. **Jeden model LLM** — `gpt-5-nano` dla Generation Agent i Visual Critic (tani, obsługuje vision); eskalacja do droższego modelu per agent jeśli jakość niewystarczająca
5. **Pydantic v2 dla state** — walidacja, serializacja JSON, kompatybilność z OpenAI structured output
6. **uv zamiast poetry/pip** — szybszy, prostszy, nowoczesny

## Rozważone i odrzucone alternatywy

### Pure asyncio (odrzucone)
- ✅ Najszybsze MVP, idealny fit do deterministycznego pipeline
- ❌ Brak wbudowanego tracing, checkpointingu, state management
- ❌ Migracja do LangGraph i tak byłaby potrzebna przy rozbudowie
- **Werdykt:** szybsze na start, ale podwójna praca jeśli PoC się sprawdzi

### OpenAI Agents SDK (odrzucone)
- ✅ Lekki, wbudowany tracing na platform.openai.com, Python-first
- ❌ Zaprojektowany na LLM-driven loops (model decyduje o flow), nie deterministyczne pipelines
- ❌ Vendor lock-in do OpenAI — brak Langfuse/LangSmith, trudna migracja LLM providera
- **Werdykt:** wrong abstraction level — nasz pipeline jest deterministyczny

## Znane ryzyka i mitigacje

| Ryzyko | Prawdopodobieństwo | Mitigacja |
|--------|-------------------|----------|
| LangGraph breaking changes | Niskie (zamrożona wersja) | Pinujemy wersję w requirements, nie upgradeujemy w trakcie PoC |
| `langchain-core` transitive dep bloat | Niskie | Nie importujemy nic z langchain bezpośrednio, izolacja przez OpenAI SDK |
| LangSmith free tier limit (5k traces) | Niskie dla PoC | Wystarcza na ~500 runów; Langfuse jako backup |
| `gpt-image-2` koszty wyższe niż `gpt-image-1` | Niskie dla PoC | Używamy najniższej rozdzielczości i low quality; lepsza jakość tekstu na obrazach kompensuje koszt |
| python-pptx ograniczenia layoutu | Niskie | Proste layouty (tytuł + obraz); nie potrzebujemy zaawansowanych animacji |