#!/usr/bin/env python3
# ./run D:\Lucas College\Purdue\Y4\ECE461\ECE-461-Project1-CLI\urls.txt
# ./run test
# ./run install
import sys
import json
import subprocess
from src.utils.run_tests import run_testsuite
import traceback
import os
import datetime
from dotenv import load_dotenv, dotenv_values

# Read environment config
load_dotenv()
LOG_FILE = os.getenv("LOG_FILE", "run.log")
try:
    LOG_LEVEL = int(os.getenv("LOG_LEVEL", "0"))
except ValueError:
    LOG_LEVEL = 0  # fallback

def print_full_exception(e):
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

def log(msg, level=1):
    """
    level=1 -> info, level=2 -> debug
    """
    if LOG_LEVEL >= level:
        ts = datetime.utcnow().isoformat()
        record = {"time": ts, "level": level, "msg": msg}
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

def log_exception(e, url=None):
    tb_str = "".join(traceback.TracebackException.from_exception(e).format())
    tb_frames = traceback.extract_tb(e.__traceback__)
    last = tb_frames[-1] if tb_frames else None

    error_record = {
        "error_type": e.__class__.__name__,
        "message": str(e),
        "filename": getattr(last, "filename", None),
        "lineno": getattr(last, "lineno", None),
        "function": getattr(last, "name", None),
        "code": getattr(last, "line", None),
        "traceback": tb_str,
    }
    if url:
        error_record["url"] = url
    if LOG_LEVEL >= 1:  # errors show up if verbosity ≥ info
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_record, ensure_ascii=False) + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: ./run [install|test|URL_FILE]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install":
        log("Installing dependencies...", level=1)
        # print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            sys.exit(0)
        except Exception as e:
            log_exception(e)
            # print(f"[install] failed: {e}", file=sys.stderr)
            sys.exit(1)
           
    elif command == "test":
        log("Running tests...", level=1)
        test_args = sys.argv[2:]
        # forward args to your unittest runner
        sys.argv = [sys.argv[0]] + test_args
        try:
            code = run_testsuite()   # ← get the real exit code
        except Exception as e:
            log_exception(e)
            code = 1                 # on exception, fail the run
        sys.exit(code)

    else:
        # assume it's a file with URLs
        from src.utils.check_url import checkURL
        from src.classes.ScoreCard import ScoreCard

        url_file = command
        try:
            urls = []
            with open(url_file, "r") as f:
                for line in f:
                    line = line.strip()
                    url_list = line.split(",")
                    for url in url_list:
                        urls.append(url.strip())
        except FileNotFoundError as e:
            log_exception(e)
            # print(f"Error: could not find file '{url_file}'", file=sys.stderr)
            sys.exit(1)

        recentGhURL = None
        recentDatasetURL = None
        for url in urls:
            if url and checkURL(url):
                try:
                    modelScore = ScoreCard(url)
                   
                    if recentDatasetURL:
                        modelScore.setDatasetURL(recentDatasetURL)
                    if recentGhURL:
                        modelScore.setGithubURL(recentGhURL)

                    modelScore.setTotalScore()
                    modelScore.printScores()

                except Exception as e:
                    error_record = {
                        "url": url,
                        "error": str(e)
                    }
                    log_exception(e)
                    # print(json.dumps(error_record), file=sys.stderr)
                    # print_full_exception(e)
                    sys.exit(1)
            else:
                # Non-HF URLs (GitHub, etc.) handled later
                if "dataset" in url:
                    recentDatasetURL = url
                elif "github" in url:
                    recentGhURL = url
        sys.exit(0)

if __name__ == "__main__":
    main()