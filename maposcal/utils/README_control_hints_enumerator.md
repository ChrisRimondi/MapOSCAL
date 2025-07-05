# Control Hints Enumerator

This module provides an elegant solution for enumerating and searching control hints from the `control_hints.py` file. It replaces the previous hardcoded approach with a dynamic, language-agnostic system.

## Overview

The `control_hints_enumerator.py` module automatically discovers all control hints defined in the `control_hints.py` file, both generic and language-specific, and provides a unified interface for searching them.

## Key Features

- **Automatic Discovery**: Dynamically enumerates all control hints from the `control_hints.py` file
- **Language Support**: Supports Python, Golang, Java, and C++ with extensible design
- **Unified Interface**: Single function call to search all controls for any language
- **Backward Compatibility**: Maintains compatibility with existing code
- **Comprehensive Coverage**: Searches both generic and language-specific hints

## Usage

### Basic Usage

```python
from maposcal.utils.control_hints_enumerator import search_control_hints_in_content

# Search for control hints in file content
file_contents = "your file content here"
found_controls = search_control_hints_in_content(file_contents, "golang")
print(f"Found controls: {found_controls}")
```

### Advanced Usage

```python
from maposcal.utils.control_hints_enumerator import (
    get_all_control_hints,
    get_control_hints_for_language,
    get_control_hints_summary
)

# Get all control hints
all_hints = get_all_control_hints()

# Get hints for specific language
golang_hints = get_control_hints_for_language("golang")

# Get summary of all hints
summary = get_control_hints_summary()
```

## API Reference

### `search_control_hints_in_content(file_contents: str, language: str) -> List[str]`

Searches for control hints in file contents for a specific language.

**Parameters:**
- `file_contents` (str): The contents of the file to search
- `language` (str): The language to search for ('python', 'golang', 'java', 'cpp')

**Returns:**
- List of control IDs that were found in the content

### `get_all_control_hints() -> Dict[str, Dict[str, List[str]]]`

Enumerates all control hints from the control_hints module.

**Returns:**
- Dict mapping control IDs to their generic and language-specific hints

### `get_control_hints_for_language(language: str) -> Dict[str, List[str]]`

Get all control hints for a specific language.

**Parameters:**
- `language` (str): The language to get hints for

**Returns:**
- Dict mapping control IDs to their hints for the specified language

### `get_control_hints_summary() -> Dict[str, Dict[str, int]]`

Get a summary of all available control hints.

**Returns:**
- Dict with control IDs and counts of hints for each language

## Integration with Language Inspectors

### Before (Old Approach)

```python
# Hardcoded to specific controls
applicable_control_hints_strings = control_hints_strings_search(
    file_contents, control_hints.sc8, "SC-8"
)
applicable_control_hints_language_strings = control_hints_strings_search(
    file_contents, control_hints.sc8_golang, "SC-8"
)

if applicable_control_hints_strings or applicable_control_hints_language_strings:
    applicable_control_hints.append("SC-8")
```

### After (New Approach)

```python
# Searches all available controls automatically
found_controls = search_control_hints_in_content(file_contents, "golang")
applicable_control_hints.extend(found_controls)
```

## Supported Languages

- **Python**: `"python"`
- **Golang**: `"golang"`
- **Java**: `"java"`
- **C++**: `"cpp"`

## Control Hint Structure

The system expects control hints to follow this naming convention in `control_hints.py`:

```python
# Generic hints for control AC-10
ac10 = [
    "keyword1",  # comment
    "keyword2",  # comment
]

# Language-specific hints for control AC-10
ac10_python = [
    "python_keyword1",  # comment
    "python_keyword2",  # comment
]

ac10_golang = [
    "golang_keyword1",  # comment
    "golang_keyword2",  # comment
]

# ... and so on for other languages
```

## Benefits

1. **Scalability**: Automatically handles new controls without code changes
2. **Maintainability**: Single source of truth for control hint logic
3. **Consistency**: Uniform behavior across all language inspectors
4. **Extensibility**: Easy to add new languages or control types
5. **Performance**: Efficient searching with early termination

## Migration Guide

To migrate existing language inspectors:

1. Replace imports:
   ```python
   # Old
   from maposcal.utils.utilities import control_hints_strings_search
   import maposcal.utils.control_hints as control_hints
   
   # New
   from maposcal.utils.control_hints_enumerator import search_control_hints_in_content
   ```

2. Replace control hint search logic:
   ```python
   # Old
   found = control_hints_strings_search(file_contents, control_hints.sc8, "SC-8")
   
   # New
   found_controls = search_control_hints_in_content(file_contents, "golang")
   ```

3. Update result handling:
   ```python
   # Old
   if found:
       applicable_control_hints.append("SC-8")
   
   # New
   applicable_control_hints.extend(found_controls)
   ```

## Example Implementation

See `maposcal/inspectors/inspect_lang_python.py` for a complete example of how to use the new system in a language inspector. 