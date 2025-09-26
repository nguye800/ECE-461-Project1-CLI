# Count unique contributors from Hugging Face without cloning
# pip install huggingface_hub
import os, re
from urllib.parse import urlparse
from collections import Counter
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError
import statistics
from dotenv import load_dotenv, dotenv_values
import requests

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

_GH_LINK_RE = re.compile(r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", re.I)

def find_github_links(model_id: str):
    api = HfApi()
    readme = getattr(api.model_card(model_id), "text", None) or api.model_card(model_id).content
    info = api.model_info(model_id)
    def walk(x):
        if isinstance(x, dict):
            for v in x.values(): yield from walk(v)
        elif isinstance(x, list):
            for v in x: yield from walk(v)
        elif isinstance(x, str):
            yield x
    from_readme = set(_GH_LINK_RE.findall(readme or ""))
    from_yaml = set(_GH_LINK_RE.findall("\n".join(walk(getattr(info, "cardData", {}) or {}))))
    return sorted(from_readme | from_yaml)

# --- Last-N commit authors from a GitHub repo (no token) ---
_BOT_RE = re.compile(r"(?:\[(?:bot)\]|bot$|^dependabot|^github-actions)", re.I)

def get_collaborators_github(github_url: str, n: int = 100, branch: str | None = None):
    m = re.match(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", github_url.strip())
    if not m: raise ValueError(f"Bad GitHub URL: {github_url}")
    owner, repo = m.group(1), m.group(2)

    per_page = max(1, min(100, n))
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={per_page}" + (f"&sha={branch}" if branch else "")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "commit-sampler-noauth/1.0"}
    commits = []

    # paginate until we collect n or hit rate limit
    while url and len(commits) < n:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 403 and "rate limit" in r.text.lower():
            break  # return partial results if rate-limited
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list): break
        commits.extend(data)
        # parse Link header for next
        link = r.headers.get("Link", "")
        nxt = None
        for part in link.split(","):
            if 'rel="next"' in part:
                nxt = part.split(";")[0].strip()[1:-1]  # strip <>
                break
        url = nxt
    commits = commits[:n]

    authors = {}
    for c in commits:
        a = (c.get("commit") or {}).get("author") or {}
        name, email = (a.get("name") or "").strip(), (a.get("email") or "").strip()
        if not name and not email:
            gh = c.get("author") or {}
            name, email = (gh.get("login") or gh.get("name") or "").strip(), ""
        if _BOT_RE.search(name): 
            continue
        key = f"{name} <{email}>" if name and email else (name or email)
        if not key: 
            continue
        authors[key] = authors.get(key, 0) + 1

    total = max(1, n)
    proportions = [cnt / total for cnt in authors.values()]
    average = sum(authors.values()) / total
    std = statistics.stdev(proportions) if len(proportions) > 1 else 0.0
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
