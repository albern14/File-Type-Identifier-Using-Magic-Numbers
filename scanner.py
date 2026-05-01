# Import json module to load the signatures database
import json

# Import os module to work with file paths and folders
import os


# -------------------------
# LOAD SIGNATURE DATABASE
# -------------------------
def load_signatures(path="signatures.json"):
    # Open JSON file containing known file signatures
    with open(path, "r", encoding="utf-8") as f:

        # Convert JSON into Python dictionary and return it
        return json.load(f)


# -------------------------
# READ FIRST BYTES OF FILE
# -------------------------
def read_file_header_hex(file_path, max_bytes=16):
    # Open file in binary read mode
    with open(file_path, "rb") as f:

        # Read first max_bytes from file
        data = f.read(max_bytes)

    # Convert bytes to uppercase hexadecimal string
    return data.hex().upper()


# -------------------------
# DETECT FILE TYPE
# -------------------------
def detect_file_type(header_hex, signatures_db):
    # Loop through every file type in signatures database
    for filetype, meta in signatures_db.items():

        # Some file types may have multiple valid signatures
        for sig in meta["sigs"]:

            # Check if file header starts with known signature
            if header_hex.startswith(sig.upper()):

                # Return detected file type information
                return filetype, meta["ext"], "Exact"

    # If no signature matched
    return "Unknown", "", "None"


# -------------------------
# SCAN SINGLE FILE
# -------------------------
def scan_file(file_path, signatures_db):
    # Extract filename from full path
    name = os.path.basename(file_path)

    # Extract file extension and convert to lowercase
    ext = os.path.splitext(name)[1].lower()

    try:
        # Read file header as hexadecimal
        header_hex = read_file_header_hex(file_path)

        # Detect real file type using signature database
        detected, expected_ext, confidence = detect_file_type(
            header_hex,
            signatures_db
        )

        # Default mismatch note is blank
        mismatch = ""

        # Check if detected file type does not match file extension
        if detected != "Unknown" and expected_ext and ext != expected_ext:
            mismatch = (
                f"Extension mismatch "
                f"(file is {expected_ext}, name shows {ext})"
            )

        # Return scan result as dictionary
        return {
            "file": name,               # Filename only
            "path": file_path,          # Full file path
            "extension": ext,           # Extension from filename
            "detected": detected,       # Real detected file type
            "confidence": confidence,   # Detection confidence
            "note": mismatch            # Warning message if mismatch
        }

    except Exception as e:
        # Return error information if scan fails
        return {
            "file": name,
            "path": file_path,
            "extension": ext,
            "detected": "Error",
            "confidence": "None",
            "note": str(e)
        }


# -------------------------
# SCAN ENTIRE FOLDER
# -------------------------
def scan_folder(folder_path, signatures_db):
    # Create list to store all scan results
    results = []

    # Walk through folder and all subfolders recursively
    for root, _, files in os.walk(folder_path):

        # Loop through every file found
        for file in files:

            # Build full path to current file
            full_path = os.path.join(root, file)

            # Scan file and store result
            results.append(scan_file(full_path, signatures_db))

    # Return all scan results
    return results
