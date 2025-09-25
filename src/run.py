#!/opt/homebrew/opt/python@3.11/bin/python3.11 #this line is because my (Eric's) Mac will not update my Python to the most current version so this manually overwrites it

import sys
import json
import src.utils.hf_api as hf_api  # Hugging Face helper

def main():
    if len(sys.argv) < 2:
        print("Usage: ./run [install|test|URL_FILE]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install":
        print("Installing dependencies... (placeholder)")

    elif command == "test":
        print("Running tests... (placeholder)")
        # hook into pytest/unittest later

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
            if "huggingface.co" in url:
                try:
                    kind, repo_id = hf_api.parse_hf_url(url)
                    api_url = hf_api.build_api_url(kind, repo_id)
                    data = hf_api.fetch_json(api_url, token=None)

                    # Build JSON record
                    record = {
                        "url": url,
                        "kind": kind,
                        "repo_id": repo_id,
                        "api_url": api_url,
                        "downloads": data.get("downloads"),
                        "pipeline_tag": data.get("pipeline_tag"),
                        "lastModified": data.get("lastModified"),
                    }

                    # Print one JSON object per line
                    print(json.dumps(record))

                except Exception as e:
                    error_record = {
                        "url": url,
                        "error": str(e)
                    }
                    print(json.dumps(error_record), file=sys.stderr)
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