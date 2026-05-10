# SlideAgent — Plan implementacji

## Struktura projektu

```
slide-agent/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   └── slideagent/
│       ├── __init__.py
│       ├── cli.py                  # Typer CLI (parse, run)
│       ├── config.py               # Pydantic Settings (.env)
│       ├── models.py               # Pydantic models (SlideData, SlideDecision, AttemptResult, etc.)
│       ├── parser.py               # Markdown parser (regex/split)
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── generator.py        # Generation Agent (skip/generate + prompt creation)
│       │   ├── critic.py           # Visual Critic (pass/fail + feedback)
│       │   └── prompts.py          # Prompt loader (YAML frontmatter + Markdown body)
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py             # ImageProvider ABC/Protocol
│       │   └── openai_provider.py  # OpenAI gpt-image-2 implementation
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── state.py            # LangGraph state definition + reducery
│       │   ├── nodes.py            # Graph node functions (thin wrappers na agentów)
│       │   └── workflow.py         # StateGraph assembly (Send, conditional edges)
│       └── output/
│           ├── __init__.py
│           ├── pptx_builder.py     # PPTX generation (python-pptx)
│           └── results.py          # Output folder structure + decision.json
├── prompts/
│   ├── generation_system.md        # Generation Agent system prompt (rola, zasady)
│   ├── generation_user.md          # Generation Agent user msg (slide → decision + prompt, z opcjonalnym {retry_context})
│   ├── retry_context.md            # Fragment: wzbogaca feedback Critica instrukcjami retry (bez frontmatter)
│   ├── critic_system.md            # Visual Critic system prompt (kryteria oceny)
│   ├── critic_user.md              # Visual Critic user msg (obraz + prompt + treść → ocena)
│   └── visual_style.md             # Reużywalny fragment globalnego stylu wizualnego (bez frontmatter)
├── templates/
│   └── base.pptx                   # Master slide template
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_models.py
│   ├── test_prompts.py
│   └── fixtures/
│       └── sample.md
└── example-presentation.md
```

## Format promptów

Pliki `.md` z YAML frontmatter:

```markdown
---
model: gpt-5-nano
temperature: 0.7
max_tokens: 1024
response_format: json
---

Treść promptu w czystym Markdown.
Zmienne w formacie {variable_name}.
```

- `visual_style.md` — bez frontmatter, to fragment includowany do innych promptów
- `retry_context.md` — bez frontmatter, to fragment wzbogacający feedback Critica instrukcjami retry
- Loader w `agents/prompts.py` parsuje frontmatter → `PromptConfig`, body → template string
- Jeden plik = jeden prompt = jego konfiguracja modelu
- `generation_user.md` zawiera `{retry_context}` — pusty na 1. próbie, wypełniony z `retry_context.md` na retry

## Fazy implementacji

### Faza 0: Scaffolding projektu

| ID   | Zadanie                                           | Priorytet |
|------|---------------------------------------------------|-----------|
| 0.1  | `pyproject.toml` + `uv init` (src layout, deps)  | high      |
| 0.2  | Struktura pakietu `src/slideagent/` z `__init__`  | high      |
| 0.3  | `.env.example` + `config.py` (Pydantic Settings)  | high      |
| 0.4  | `README.md` z instrukcją uruchomienia             | medium    |

### Faza 1: Modele, Parser, CLI (zero zależności API)

| ID   | Zadanie                                           | Priorytet |
|------|---------------------------------------------------|-----------|
| 1.1  | Pydantic models (`PresentationMeta`, `SlideData`, `SlideDecision`, `AttemptResult`, `PipelineState`) | high |
| 1.2  | Markdown parser + walidacja inputu (F-001→F-005, US-013) | high |
| 1.3  | Testy parsera (edge cases, example-presentation.md) | high |
| 1.4  | CLI skeleton: Typer `parse` + `run` (stub)        | high      |
| 1.5  | Prompt loader (YAML frontmatter parser + PromptConfig) | high |

### Faza 2: Agenci i providerzy (integracja OpenAI)

| ID   | Zadanie                                           | Priorytet |
|------|---------------------------------------------------|-----------|
| 2.1  | ImageProvider ABC/Protocol + OpenAI implementation | high     |
| 2.2  | Generation Agent (skip/generate + prompt gen) (F-006→F-010) | high |
| 2.3  | Image Generator wrapper na `client.images.generate()` (F-011→F-012) | high |
| 2.4  | Visual Critic (pass/fail + feedback) (F-014→F-018) | high    |
| 2.5  | Pliki promptów w `prompts/*.md` z frontmatter     | high      |
| 2.6  | Unit testy agentów (mocked OpenAI)                | medium    |

### Faza 3: Orkiestracja LangGraph

| ID   | Zadanie                                           | Priorytet |
|------|---------------------------------------------------|-----------|
| 3.1  | LangGraph state z reducerami (`Annotated[list, operator.add]`) | high |
| 3.2  | Graph nodes (decision, generate, critique, retry) | high      |
| 3.3  | Workflow assembly: `Send()` fan-out/fan-in, conditional edges, max 3 retry | high |
| 3.4  | Concurrency control: max 5 slajdów równolegle (F-024) | high |

### Faza 4: Output

| ID   | Zadanie                                           | Priorytet |
|------|---------------------------------------------------|-----------|
| 4.1  | Output manager (folder structure per slajd, `decision.json`) (F-031→F-033) | high |
| 4.2  | PPTX builder — 3 layouty: title+image, full image, text only (F-026→F-030) | high |
| 4.3  | Base PPTX template `templates/base.pptx`          | medium    |

### Faza 5: Integracja i polish

| ID   | Zadanie                                           | Priorytet |
|------|---------------------------------------------------|-----------|
| 5.1  | End-to-end wiring: CLI `run` → parser → graph → PPTX | high   |
| 5.2  | LangSmith tracing setup (env vars, weryfikacja) (F-037→F-038) | medium |
| 5.3  | Error handling + graceful fallback (US-011, US-013) | medium   |
| 5.4  | Integration test z example-presentation.md        | medium    |

## Przepływ danych (Data Flow)

```
MD File → Parser → PresentationMeta + list[SlideData]
                          ↓
                   LangGraph State (in-memory)
                          ↓
              ┌───────────┼───────────┐
              ↓           ↓           ↓        (max 5 concurrent)
         Slide 1     Slide 2     Slide N
         ┌────┐      ┌────┐      ┌────┐
         │ GA │      │ GA │      │ GA │       GA = Generation Agent
         │ IG │      │ IG │      │ IG │       IG = Image Generator
         │ VC │      │ VC │      │ VC │       VC = Visual Critic
         └────┘      └────┘      └────┘       (retry loop wewnątrz)
              ↓           ↓           ↓
                   LangGraph State (wyniki)
                          ↓
              ┌───────────┼───────────┐
              ↓                       ↓
       Output Manager          PPTX Builder
    (folders, JSON, PNG)    (presentation.pptx)
```

**Kluczowa zasada: agenci NIE czytają plików.** Dane płyną przez LangGraph state:
- Parser wczytuje MD → tworzy obiekty Pydantic (`PresentationMeta`, `SlideData`)
- LangGraph state trzyma wszystko w pamięci (slajdy, decyzje, obrazy jako bytes)
- Agenci dostają `SlideData` jako argument node'a — zero I/O
- Output manager zapisuje artefakty na dysk **na końcu** (debug + finalny PPTX)
- Pliki na dysku (slide_01.md, decision.json) to artefakty debugowe, nie input dla agentów

## PresentationMeta

Parser wyciąga z nagłówka MD:
```python
class PresentationMeta(BaseModel):
    title: str              # z `# Tytuł`
    description: str        # z `**Description:**`
    keywords: list[str]     # z `**Słowa kluczowe:**`
    visual_theme: str       # z `**Motyw wizualny:**`
```

Każdy `SlideData` ma referencję do `PresentationMeta` — Generation Agent używa `visual_theme` przy tworzeniu promptu.

## Kluczowe decyzje architektoniczne

1. **src layout** — izolacja od testów, poprawne importy
2. **Prompty w Markdown z YAML frontmatter** — jeden plik = prompt + config modelu, czytelne, git-friendly
3. **`agents/prompts.py` jako loader** — jedno miejsce do ładowania i renderowania promptów
4. **`retry_context.md` jako fragment wzbogacający feedback** — instrukcje retry tunowalne bez dotykania kodu
5. **`providers/base.py` ABC** — podmiana providera w jednej linii
6. **`graph/` oddzielony od logiki biznesowej** — nodes to cienkie wrappery, logika w agents/
7. **Pydantic Settings** z `.env` — bezpieczne zarządzanie kluczami API
8. **State-based data flow** — agenci NIE czytają plików, dane płyną przez LangGraph state
9. **PresentationMeta** — metadata prezentacji (tytuł, opis, motyw) parsowane z nagłówka MD
10. **Fazy niezależne od API** (0+1) pozwalają weryfikować parser/modele offline
11. **Pipeline deterministyczny** — parse zawsze pierwszy krok, LLM decyduje tylko skip/generate per slajd

## Zależności między fazami

```
Faza 0 (scaffolding) → Faza 1 (models, parser, CLI)
                            ↓
                      Faza 2 (agents, providers)
                            ↓
                      Faza 3 (LangGraph orchestration)
                            ↓
                      Faza 4 (output: PPTX, folders)
                            ↓
                      Faza 5 (integration, tracing, tests)
```
