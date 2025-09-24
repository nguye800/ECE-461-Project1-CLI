# Given the url for a huggingface model get git metadata on the model repository
# Track the last 200 commits and save all unique usernames to find number of recent collaborators
# https://huggingface.co/google/gemma-3-270m/tree/main
import os
import re
import tempfile
import subprocess
from urllib.parse import urlparse

def parse_hf_repo(url: str) -> str:
    # Accept forms like:
    # https://huggingface.co/namespace/repo
    # https://huggingface.co/namespace/repo/tree/main  (any trailing path ignored)
    p = urlparse(url)
    parts = [seg for seg in p.path.split("/") if seg]
    if len(parts) < 2:
        raise ValueError("Invalid HF URL; expected https://huggingface.co/<owner>/<repo>")
    owner, repo = parts[0], parts[1]
    return f"https://huggingface.co/{owner}/{repo}.git"

def getCollaborators(hf_url: str, n: int = 200):
    repo_url = parse_hf_repo(hf_url)

    # Avoid pulling large LFS files and interactive env
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "echo"
    env["GCM_INTERACTIVE"] = "Never"
    env["GIT_LFS_SKIP_SMUDGE"] = "1"

    # temporarily saves the repo to check for names then deletes afterwards
    with tempfile.TemporaryDirectory() as tmp:
        # Shallow, blob-less clone (fast)
        # --filter=blob:none avoids downloading file contents
        # --no-checkout speeds up further (we just want log)
        subprocess.check_call(
            [
                "git",
                "-c", "credential.helper=",
                "-c", "credential.interactive=never",
                "clone",
                "--filter=blob:none",   # avoid file contents
                "--no-checkout",        # we only want history
                "--depth", str(n),      # shallow history
                repo_url, tmp
            ],
            env=env,
        )

        # Get last n commits with author info through the log
        fmt = "%H|%an|%ae|%ad|%s"  # hash|author_name|author_email|date|subject
        out = subprocess.check_output(
            ["git", "-C", tmp, "log", f"-n{n}", f"--pretty=format:{fmt}"],
            text=True,
            env=env,
        )

    authors = set()

    # Try to extract usernames from common noreply patterns; fall back to author name.
    username_from_email = re.compile(
        r"""
        ^(?:
            (?P<ghuser>.+)\+.+@users\.noreply\.github\.com|     # GitHub pattern 12345+user
            (?P<ghuser2>.+)@users\.noreply\.github\.com|        # GitHub plain
            (?P<hfuser>.+)@users\.noreply\.huggingface\.co|     # (possible HF pattern)
            (?P<plain>[^@]+)@[^@]+                              # anything@domain
        )$
        """,
        re.X | re.I,
    )

    for line in out.splitlines():
        try:
            commit, author_name, author_email, date, subject = line.split("|", 4)
        except ValueError:
            # Malformed line; skip
            continue

        m = username_from_email.match(author_email.strip())
        user = None
        if m:
            user = (
                m.group("ghuser")
                or m.group("ghuser2")
                or m.group("hfuser")
                or m.group("plain")
            )
        # Normalize: prefer something non-empty and readable
        candidate = (user or author_name or "").strip()
        if candidate:
            authors.add(candidate)

    return len(authors)

if __name__ == "__main__":
    url = "https://huggingface.co/google/gemma-3-270m/tree/main"
    num_collaborators = getCollaborators(url, n=200)
    print("Number of unique Collaborators: ", num_collaborators)
