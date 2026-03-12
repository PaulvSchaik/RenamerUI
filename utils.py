import os
import re

def clean_filename(name):
    """Removes invalid characters for filenames."""
    # Remove characters like / \ : * ? " < > |
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

def format_filename(metadata):
    """Creates the final filename from metadata."""
    year_month = metadata.get("year_month", "unknown-date")
    party = clean_filename(metadata.get("party", "UnknownParty"))
    summary = clean_filename(metadata.get("summary", "Document"))
    
    return f"{year_month} - {party} - {summary}.pdf"

def rename_file(old_path, new_filename):
    """Safely renames a file."""
    directory = os.path.dirname(old_path)
    new_path = os.path.join(directory, new_filename)
    
    # Handle filename collisions
    counter = 1
    base, ext = os.path.splitext(new_path)
    while os.path.exists(new_path):
        new_path = f"{base}_{counter}{ext}"
        counter += 1
        
    try:
        os.rename(old_path, new_path)
        return new_path
    except Exception as e:
        print(f"Error renaming {old_path} to {new_path}: {e}")
        return None
