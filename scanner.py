# Import json module to load the signatures database
import json

# Import os module to work with file paths and folders
import os


# -------------------------
# LOAD SIGNATURE DATABASE
# -------------------------
def load_signatures(path="signatures.json"):
    """
    Opens the JSON file containing known file signatures
    (magic numbers) and loads it into a Python dictionary.
    """
    with open(path, "r", encoding="utf-8") as f:
        # json.load() converts JSON file into Python dictionary
        return json.load(f)


# -------------------------
# READ FIRST BYTES OF FILE
# -------------------------
def read_file_header_hex(file_path, max_bytes=16):
    """
    Opens a file in binary mode and reads the first few bytes.
    These bytes are converted to HEX format (uppercase string).
    """
    # "rb" means read in binary mode
    with open(file_path, "rb") as f:
        # Read first max_bytes (default 16 bytes)
        data = f.read(max_bytes)

    # Convert bytes to hexadecimal string and make uppercase
    return data.hex().upper()


# -------------------------
# DETECT FILE TYPE
# -------------------------
def detect_file_type(header_hex, signatures_db):
    """
    Compares the file's header hex against known signatures
    in the database.
    """

    # Loop through each file type in database
    # Example: "PNG", "JPG", "PDF"
    for filetype, meta in signatures_db.items():

        # Each file type may have multiple valid signatures
        for sig in meta["sigs"]:

            # Check if file header starts with that signature
            if header_hex.startswith(sig.upper()):
                # Return:
                # file type name
                # expected extension
                # confidence level
                return filetype, meta["ext"], "Exact"

    # If no match found
    return "Unknown", "", "None"


# -------------------------
# SCAN A SINGLE FILE
# -------------------------
def scan_file(file_path, signatures_db):
    """
    Scans one file:
    - Reads header
    - Detects real file type
    - Compares with file extension
    """

    # Extract just filename (without full path)
    name = os.path.basename(file_path)

    # Extract extension (example: ".jpg")
    ext = os.path.splitext(name)[1].lower()

    try:
        # Read first bytes as hex
        header_hex = read_file_header_hex(file_path)

        # Detect file type using signature database
        detected, expected_ext, confidence = detect_file_type(
            header_hex, signatures_db
        )

        # Check if extension mismatch exists
        mismatch = ""
        if detected != "Unknown" and expected_ext and ext != expected_ext:
            mismatch = (
                f"Extension mismatch (file is {expected_ext}, "
                f"name shows {ext})"
            )

        # Return results as dictionary
        return {
            "file": name,               # file name only
            "path": file_path,          # full path
            "extension": ext,           # extension from filename
            "detected": detected,       # detected real type
            "confidence": confidence,   # detection confidence
            "note": mismatch            # warning if mismatch
        }

    except Exception as e:
        # If any error occurs (permission denied, unreadable file, etc.)
        return {
            "file": name,
            "path": file_path,
            "extension": ext,
            "detected": "Error",
            "confidence": "None",
            "note": str(e)  # Store error message
        }


# -------------------------
# SCAN ENTIRE FOLDER
# -------------------------
def scan_folder(folder_path, signatures_db):
    """
    Recursively scans all files inside a folder.
    """

    results = []

    # os.walk goes through:
    # - root folder
    # - subfolders
    # - files
    for root, _, files in os.walk(folder_path):

        # Loop through each file in current folder
        for file in files:

            # Build full file path
            full_path = os.path.join(root, file)

            # Scan file and store result
            results.append(scan_file(full_path, signatures_db))

    return results
