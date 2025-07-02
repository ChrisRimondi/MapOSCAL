"""
This modules is only intended for the storage of various global settings.
"""

global openai_model
global openai_base_url
global tiktoken_encoding
global local_embeddings_model
global ignored_file_extensions
global ignored_filename_patterns
global config_file_extensions

openai_model = "gpt-4.1-mini"
openai_base_url = "https://api.openai.com/v1"
tiktoken_encoding = "cl100k_base"
local_embeddings_model = "all-MiniLM-L6-v2"
ignored_file_extensions = [
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp",  # Images
    ".1", ".meta", ".tgz", ".s2", # Misc files
     ".exe", ".dll", ".so", ".dylib", ".bin", ".app",  # Executables and binaries
     ".gitignore", ".idx", ".pack", ".lock",  # Git and lock files
     ".zip", ".tar", ".gz", ".rar", ".7z",  # Archives
     ".pdf", ".doc", ".docx", ".xls", ".xlsx",  # Documents
     ".mp3", ".mp4", ".avi", ".mov", ".wav",  # Media files
     ".log", ".tmp", ".temp", ".cache",  # Temporary and log files
     ".min.js", ".min.css",  # Minified files
     ".map",  # Source maps
]
ignored_filename_patterns = [
    "test", "mock", "example", "sample",
    ".golangci.yml", ".golangci.yaml",
".goreleaser.yml", ".goreleaser.yaml"
]

ignored_directory_patterns = [
     "node_modules", "vendor", "dist", "build", "target",  # Dependencies and build artifacts
     ".git", ".svn", ".hg", ".github",  # Version control
     ".vscode", ".idea", ".vs",  # IDE files
     "coverage", ".nyc_output",  # Test coverage
     "logs", "log",  # Log directories
     "cache", ".cache",  # Cache directories
     "tmp", "temp",  # Temporary directories
     "uploads", "downloads",  # User upload/download directories
     ".terraform", "terraform.tfstate",  # Terraform files
     "migrations",  # Database migrations
     "seeds", "fixtures", "test",  # Test data
 ]

# Default configuration file extensions
config_file_extensions = [
    ".yaml", ".yml", ".json", ".toml", ".ini", ".conf", ".properties"
]

if __name__ == "__main__":
    print("This module not intended for interactive use.  Pleaes use cli.py.")

