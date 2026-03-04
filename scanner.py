import json
import os

def load_signatures(path="signatures.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_file_header_hex(file_path, max_bytes=16):
    with open(file_path, "rb") as f:
        data = f.read(max_bytes)
    return data.hex().upper()

def detect_file_type(header_hex, signatures_db):
    for filetype, meta in signatures_db.items():
        for sig in meta["sigs"]:
            if header_hex.startswith(sig.upper()):
                return filetype, meta["ext"], "Exact"
    return "Unknown", "", "None"

def scan_file(file_path, signatures_db):
    name = os.path.basename(file_path)
    ext = os.path.splitext(name)[1].lower()

    try:
        header_hex = read_file_header_hex(file_path)
        detected, expected_ext, confidence = detect_file_type(header_hex, signatures_db)

        mismatch = ""
        if detected != "Unknown" and expected_ext and ext != expected_ext:
            mismatch = f"Extension mismatch (file is {expected_ext}, name shows {ext})"

        return {
            "file": name,
            "path": file_path,
            "extension": ext,
            "detected": detected,
            "confidence": confidence,
            "note": mismatch
        }

    except Exception as e:
        return {
            "file": name,
            "path": file_path,
            "extension": ext,
            "detected": "Error",
            "confidence": "None",
            "note": str(e)
        }

def scan_folder(folder_path, signatures_db):
    results = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            results.append(scan_file(full_path, signatures_db))
    return results
    