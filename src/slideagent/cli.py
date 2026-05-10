import logging
from pathlib import Path

import typer

from slideagent.parser import parse_presentation

app = typer.Typer(
    name="slideagent",
    help="AI-powered presentation image generator — from Markdown to PPTX.",
    no_args_is_help=True,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


@app.command()
def parse(
    input_file: Path = typer.Argument(..., help="Path to the Markdown presentation file."),
    output_dir: Path = typer.Option(Path("output"), help="Directory to write parsed slides."),
) -> None:
    """Parse a Markdown presentation into individual slide files."""
    result = parse_presentation(input_file)

    output_dir.mkdir(parents=True, exist_ok=True)

    meta_path = output_dir / "presentation.json"
    meta_path.write_text(result.meta.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(f"Metadata → {meta_path}")

    for slide in result.slides:
        slide_dir = output_dir / f"{slide.index:02d}"
        slide_dir.mkdir(exist_ok=True)

        slide_md = slide_dir / "slide.md"
        slide_md.write_text(slide.raw_markdown, encoding="utf-8")

        slide_json = slide_dir / "slide.json"
        slide_json.write_text(slide.model_dump_json(indent=2), encoding="utf-8")

    typer.echo(f"Parsed {len(result.slides)} slides → {output_dir}/")


@app.command()
def run(
    input_file: Path = typer.Argument(..., help="Path to the Markdown presentation file."),
    output_dir: Path = typer.Option(Path("output"), help="Directory to write results."),
) -> None:
    """Run the full pipeline: parse → generate images → build PPTX."""
    typer.echo("Not implemented yet — coming in Phase 2+3.")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
