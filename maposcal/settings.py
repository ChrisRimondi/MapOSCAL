"""
This modules is only intended for the storage of various global settings.
"""

# LLM Provider configurations
LLM_PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY"
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY"
    }
}

# Default LLM configurations for each command
DEFAULT_LLM_CONFIGS = {
    "analyze": {
        "provider": "openai",
        "model": "gpt-4.1-mini"  # Fast, cost-effective for analysis
    },
    "summarize": {
        "provider": "openai",
        "model": "gpt-4.1"  # High quality for summaries
    },
    "generate": {
        "provider": "openai",
        "model": "gpt-4.1"  # High quality for OSCAL generation
    },
    "evaluate": {
        "provider": "openai",
        "model": "gpt-4.1"  # High quality for evaluation
    }
}

# Legacy settings for backward compatibility
global openai_model
global openai_base_url
global tiktoken_encoding
global local_embeddings_model
global ignored_file_extensions
global ignored_filename_patterns
global config_file_extensions

# Legacy OpenAI settings (deprecated - use LLM_PROVIDERS and DEFAULT_LLM_CONFIGS)
openai_model = "gpt-4o-mini"
openai_base_url = "https://api.openai.com/v1"
tiktoken_encoding = "cl100k_base"
local_embeddings_model = "all-MiniLM-L6-v2"

ignored_file_extensions = [
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".svg",
    ".ico",
    ".webp",  # Images
    ".1",
    ".meta",
    ".tgz",
    ".s2",  # Misc files
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".app",  # Executables and binaries
    ".gitignore",
    ".idx",
    ".pack",
    ".lock",  # Git and lock files
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",  # Archives
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",  # Documents
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",  # Media files
    ".log",
    ".tmp",
    ".temp",
    ".cache",  # Temporary and log files
    ".min.js",
    ".min.css",  # Minified files
    ".map",  # Source maps
    ".pem",
    ".key",
    ".crt",
    ".cer",
    ".der",
    ".p12",
    ".pfx",
    ".p7b",
    ".p7c",  # SSL/TLS certificates and keys
    ".id_rsa",
    ".id_dsa",
    ".id_ecdsa",
    ".id_ed25519",
    ".ssh",  # SSH keys
    ".env",
    ".env.local",
    ".env.production",
    ".env.staging",
    ".env.development",  # Environment files
    ".secret",
    ".secrets",
    ".private",
    ".priv",  # Generic secret files
    ".jks",
    ".keystore",
    ".truststore",  # Java keystores
    ".gpg",
    ".asc",
    ".pgp",  # GPG/PGP files
    ".p8",
    ".p12",
    ".mobileprovision",
    ".pem",  # Apple certificates and keys
    ".p7s",
    ".p7m",  # PKCS#7 files
]
ignored_filename_patterns = [
    "test",
    "mock",
    "example",
    "sample",
    ".golangci.yml",
    ".golangci.yaml",
    ".goreleaser.yml",
    ".goreleaser.yaml",
]

ignored_directory_patterns = [
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",  # Dependencies and build artifacts
    ".git",
    ".svn",
    ".hg",
    ".github",  # Version control
    ".vscode",
    ".idea",
    ".vs",  # IDE files
    "coverage",
    ".nyc_output",  # Test coverage
    "logs",
    "log",  # Log directories
    "cache",
    ".cache",  # Cache directories
    "tmp",
    "temp",  # Temporary directories
    "uploads",
    "downloads",  # User upload/download directories
    ".terraform",
    "terraform.tfstate",  # Terraform files
    "migrations",  # Database migrations
    "seeds",
    "fixtures",
    "test",  # Test data
]

# Default configuration file extensions
config_file_extensions = [
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".conf",
    ".properties",
]

if __name__ == "__main__":
    print("This module not intended for interactive use.  Pleaes use cli.py.")
