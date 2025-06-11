import typer
from maposcal.analyzer.analyzer import Analyzer

app = typer.Typer()

@app.command()
def analyze(repo_path: str, output_dir: str = ".oscalgen"):
    analyzer = Analyzer(repo_path=repo_path, output_dir=output_dir)
    analyzer.run()

@app.command()
def generate(control: str, model: str = "openai"):
    """Generate OSCAL component for control"""
    typer.echo("Placeholder for generate")

if __name__ == "__main__":
    app()
