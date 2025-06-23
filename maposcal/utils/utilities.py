def parse_file_into_strings(file_contents):
    """
    Takes a file's contents and returns it as a list of strings for quick pattern matching.

    Args:
        file_contents (string): Contents of a file (e.g. code or configuration file).
    Returns:
        strings (list): All strings identified in the file's contents

    """
    logger.debug(f"Beginning strings parsing.")
    listed_strings = []
    listed_strings = file_contents.strip().split()
    
    logger.info(f"Identified ({len(listed_strings)}) strings in file contents.")

    return listed_strings
