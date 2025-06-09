import typer


app = typer.Typer()

@app.command()
def analyze(path: str, embedding_backend: str = "openai"):
    """Analyze repo and generate embeddings"""

    typer.echo(f"Analyzed and indexed {path}.")

@app.command()
def generate(control: str, model: str = "openai"):
    """Generate OSCAL component for control"""
    typer.echo("Placeholder for generate")

if __name__ == "__main__":
    app()
