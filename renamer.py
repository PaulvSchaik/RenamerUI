import sys
import time
import argparse
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from metadata import extract_text_from_pdf, get_pdf_metadata
from utils import format_filename, rename_file

class PDFHandler(FileSystemEventHandler):
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        # To avoid infinite loops, keep track of files we've already renamed
        self.processed_files = set()

    def process_file(self, file_path):
        if not file_path.lower().endswith('.pdf'):
            return
            
        if file_path in self.processed_files:
            return

        print(f"[*] Processing: {os.path.basename(file_path)}...")
        
        # 1. Extract text
        text = extract_text_from_pdf(file_path)
        if not text:
            print(f"[!] No text extracted from {file_path}")
            return
            
        # 2. Get metadata from Gemini
        metadata = get_pdf_metadata(text)
        if not metadata:
            print(f"[!] Failed to get metadata for {file_path}")
            return
            
        # 3. Format new name
        new_name = format_filename(metadata)
        
        # 4. Rename
        if self.dry_run:
            print(f"[DRY-RUN] Would rename {os.path.basename(file_path)} to {new_name}")
        else:
            new_path = rename_file(file_path, new_name)
            if new_path:
                print(f"[+] Renamed: {os.path.basename(file_path)} -> {os.path.basename(new_path)}")
                self.processed_files.add(new_path)

    def on_created(self, event):
        if not event.is_directory:
            # Give the OS a moment to finish writing the file
            time.sleep(1)
            self.process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.process_file(event.dest_path)

def main():
    parser = argparse.ArgumentParser(description="RenamerPro: AI-Powered PDF Renamer")
    parser.add_argument("--watch", help="Directory to monitor for new PDF files")
    parser.add_argument("--once", help="Process all existing PDF files in this directory once")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without renaming")
    
    args = parser.parse_args()

    if not args.watch and not args.once:
        parser.print_help()
        sys.exit(1)

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("[!] ERROR: GOOGLE_API_KEY environment variable not set in .env")
        sys.exit(1)

    if args.once:
        target_dir = args.once
        if not os.path.isdir(target_dir):
            print(f"[!] {target_dir} is not a valid directory")
            sys.exit(1)
            
        print(f"[*] Scanning {target_dir}...")
        handler = PDFHandler(dry_run=args.dry_run)
        for filename in os.listdir(target_dir):
            if filename.lower().endswith('.pdf'):
                handler.process_file(os.path.join(target_dir, filename))

    if args.watch:
        watch_dir = args.watch
        if not os.path.isdir(watch_dir):
            print(f"[!] {watch_dir} is not a valid directory")
            sys.exit(1)
            
        print(f"[*] Monitoring {watch_dir} for new PDFs...")
        event_handler = PDFHandler(dry_run=args.dry_run)
        observer = Observer()
        observer.schedule(event_handler, watch_dir, recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    main()
