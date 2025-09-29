# These URLs may be of the following three categories:
# • Model URL (e.g. https://huggingface.co/google/gemma-3-270m/tree/main)
# • Dataset URL: (e.g. https://huggingface.co/datasets/xlangai/AgentNet)
# • Code URL: ( e.g. https://github.com/SkyworkAI/Matrix-Game)
'''
from src.utils.hf_api import hfAPI

def checkURL(url):
    if "github" in url or "datasets" in url:
        return False
    else:
        api = hfAPI()
        api.get_info(url, False)
        return True
'''

# These URLs may be of the following three categories:
# • Model URL (e.g. https://huggingface.co/google/gemma-3-270m/tree/main)
# • Dataset URL: (e.g. https://huggingface.co/datasets/xlangai/AgentNet)
# • Code URL: ( e.g. https://github.com/SkyworkAI/Matrix-Game)
# src/utils/check_url.py

import re
from typing import Optional

# model URLs look like: https://huggingface.co/{org}/{model}[/tree/{branch}]
_MODEL_RE = re.compile(
    r"^https?://huggingface\.co/(?!datasets/)[A-Za-z0-9._-]+/[A-Za-z0-9._-]+(?:/tree/[A-Za-z0-9._/-]+)?/?$"
)

def checkURL(url: Optional[str]) -> bool:
    """
    Return True iff `url` looks like a Hugging Face *model* URL.
    Return False for dataset links, GitHub/GitLab/code links, invalid/missing.
    This function is intentionally offline (no network calls).
    """
    if not isinstance(url, str) or not url.strip():
        return False

    u = url.strip()

    # Explicit negatives first
    if "github.com" in u or "gitlab.com" in u:
        return False
    if "/datasets/" in u:
        return False

    # Positive: model URL pattern
    return bool(_MODEL_RE.match(u))
