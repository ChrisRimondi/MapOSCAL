import logging

logger = logging.getLogger()


def control_hints_strings_search(file_contents, search_strings, control_name):
    """
    Takes the contents of a Golang file and parses it for known strings associated with control mappings. If a
    match is found, the applicable flag is returned.

    Args:
        file_contents (str): The contents of a file or object that should be pattern matched to find strings.
        search_strings (list): A list of strings to search for inside of the file_contents.
        control_name (str): The identifier/name of the associated control (e.g., SC-8)
    Return:
        applicable_control_hints (list): A list of control hints that are deemed applicable by pattern matching.
    """
    control_hint_applicable = False

    # Parse into strings - utility
    identified_strings = parse_file_into_strings(file_contents)
    logger.info(
        f"Parsing contents for any hits from list of {len(search_strings)} defined strings related to control {control_name}"
    )

    #   This is where future magic has to happen to identify all the applicable control families, not just SC-8.
    # The current configuration is for example purposes only, scale requires a different model of storing these.

    #   Find hits - but we start with the smallest string set, which is the defined strings, not all the strings in
    # the file's contents.  This is really a job for Redis, etc., but sufficient as an example.
    for control_hit_string in search_strings:
        logger.debug(f"Searching for string ({control_hit_string})...")
        for lang_string in identified_strings:
            # Identify any hits
            if control_hit_string == lang_string.lower():
                #   We don't care about additional hits, the control hint is now active.  However, future work
                # might add weight to the findings based on the number of occurances...
                logger.info(
                    f"Identified ({control_name}) control applicability based on string ({control_hit_string})."
                )
                control_hint_applicable = True
                break

    return control_hint_applicable


def parse_file_into_strings(file_contents):
    """
    Takes a file's contents and returns it as a list of strings for quick pattern matching.

    Args:
        file_contents (string): Contents of a file (e.g. code or configuration file).
    Returns:
        strings (list): All strings identified in the file's contents

    """
    logger.debug("Beginning strings parsing.")
    listed_strings = []
    listed_strings = file_contents.strip().split()

    logger.debug(f"Identified ({len(listed_strings)}) strings in file contents.")

    return listed_strings
