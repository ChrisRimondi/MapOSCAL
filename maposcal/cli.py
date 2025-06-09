import typer
from maposcal.analyzer.chunker import analyze_repo
from maposcal.embeddings.faiss_index import build_index
from maposcal.generator.oscal_writer import generate_component

app = typer.Typer()

@app.command()
def analyze(path: str, embedding_backend: str = "openai"):
    """Analyze repo and generate embeddings"""
    chunks = analyze_repo(path)
    build_index(chunks, backend=embedding_backend)
    typer.echo(f"Analyzed and indexed {len(chunks)} chunks.")

@app.command()
def generate(control: str, model: str = "openai"):
    """Generate OSCAL component for control"""
    yaml_text = generate_component(control, model)
    typer.echo(yaml_text)

if __name__ == "__main__":
    app()
