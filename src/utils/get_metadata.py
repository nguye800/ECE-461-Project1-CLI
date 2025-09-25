# Count unique contributors from Hugging Face without cloning
# pip install huggingface_hub
import os, re
from urllib.parse import urlparse
from collections import Counter
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError
import statistics
from dotenv import load_dotenv, dotenv_values

BOT_RE = re.compile(r"(bot|ci|action|autobot|dependabot|github-actions)", re.I)

def _repo_id_from_url(url: str) -> str:
    p = urlparse(url)
    parts = [seg for seg in p.path.split("/") if seg]
    if len(parts) < 2:
        raise ValueError("Invalid HF URL; expected https://huggingface.co/<owner>/<repo>")
    return f"{parts[0]}/{parts[1]}"

def _normalize_author(label: str | None) -> str | None:
    if not label:
        return None
    label = re.sub(r"<[^>]+>", "", label).strip()  # drop emails
    if not label or label.lower() == "system" or BOT_RE.search(label):
        return None
    return label

def getCollaborators(hf_url: str, n: int = 100, branch: str | None = None) -> int:
    """Return # of unique human authors among the last n commits."""
    repo_id = _repo_id_from_url(hf_url)

    # Use token if available (needed for gated/private repos), else anonymous.
    load_dotenv()
    tok = os.getenv("HF_TOKEN")
    api = HfApi(token=tok or False)

    try:
        commits = api.list_repo_commits(repo_id, revision=branch)[:n]
    except HfHubHTTPError as e:
        # Common causes: repo is gated/private and you didn't supply HF_TOKEN,
        # or you haven't accepted the license.
       print(f"Unable to list commits for {repo_id}: {e}")
       return -1, -1, -1

    authors = {}
    for c in commits:
        # Prefer the first human author string if present
        author = None
        if getattr(c, "authors", None):
            for a in c.authors:
                a = _normalize_author(a)
                if a:
                    author = a
                    break
        if author and author in authors:
            authors[author] += 1
        elif author and author not in authors:
            authors[author] = 1

    # get proportion of commits for each author
    average = 0
    proportions = []
    for writers in authors:
        proportions.append(authors[writers] / n)
        average += authors[writers]
    
    std = statistics.stdev(proportions)
    average = average / n

    return average, std, authors

if __name__ == "__main__":
    url = "https://huggingface.co/google-bert/bert-base-uncased"
    avg, std, authors = getCollaborators(url, n=100)
    if avg == -1 or std == -1 or authors == -1:
        print("Unable to access Repo")
    else:
        print("Unique collaborators (last 100):", len(authors))
        print("Average percentage of commits by individuals: ", avg)
        print("Standard deviation of commit percentage by individuals: ", std)
