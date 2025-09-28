#!/usr/bin/env python3
# ./run D:\Lucas College\Purdue\Y4\ECE461\ECE-461-Project1-CLI\urls.txt
# ./run test
# ./run install
import sys
import json
import subprocess
from src.utils.check_url import checkURL
from src.classes.ScoreCard import ScoreCard
from src.utils.run_tests import run_testsuite
import traceback

def log_exception(e):
    # Full formatted traceback string (multi-line)
    tb_str = "".join(traceback.TracebackException.from_exception(e).format())

    # Last frame (where it blew up)
    tb_frames = traceback.extract_tb(e.__traceback__)
    last = tb_frames[-1] if tb_frames else None

    error_record = {
        "error_type": e.__class__.__name__,
        "message": str(e),
        "filename": getattr(last, "filename", None),
        "lineno": getattr(last, "lineno", None),
        "function": getattr(last, "name", None),
        "code": getattr(last, "line", None),
    }
    
    error_record["traceback"] = tb_str
    print(json.dumps(error_record, ensure_ascii=False), file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: ./run [install|test|URL_FILE]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install":
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            sys.exit(0)
        except Exception as e:
            print(f"[install] failed: {e}", file=sys.stderr)
            sys.exit(-1)

    elif command == "test":
        print("Running tests...")
        test_args = sys.argv[2:]
        try:
            sys.argv = [sys.argv[0]] + test_args
            run_testsuite()               # now its argparse won't see 'test'
            exit(0)
        except Exception as e:
            print(f"[tests] failed: {e}", file=sys.stderr)
            sys.exit(-1)

    else:
        # assume it's a file with URLs
        url_file = command
        try:
            with open(url_file, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: could not find file '{url_file}'", file=sys.stderr)
            sys.exit(1)

        for url in urls:
            if checkURL(url):
                try:
                    modelScore = ScoreCard(url)
                    modelScore.setTotalScore()
                    modelScore.printTotalScore()
                    modelScore.printSubscores()

                except Exception as e:
                    error_record = {
                        "url": url,
                        "error": str(e)
                    }
                    print(json.dumps(error_record), file=sys.stderr)
                    log_exception(e)
            else:
                # Non-HF URLs (GitHub, etc.) handled later
                record = {
                    "url": url,
                    "kind": "unknown",
                    "note": "not Hugging Face, skipping for now"
                }
                print(json.dumps(record))

if __name__ == "__main__":
    main()