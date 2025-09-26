# All code that will be used in the logic for end to end function goes in src
# Utils folder will hold helper functions such as api calls and url checking
# All unittest code will go in test
# cliproject.toml holds the config to run the run.py file when the "run URL" command is used in terminal

# To Do List
# Lucas
- URL checking
- HF api to store model information (modify hf_api.py code) and store in cache
 - from functools import lru_cache just call api.get_info(url, False) again and results should already be cached in lru cache
- Use git metadata on HF model for metric
- Use Purdue GenAI studio api to get info (modify chatgpt_api.py)
- BusFactor: Web scraper, look at git metadata for hf repo and for the last 200 commits check # of unique contributors by id
# Eric
- RampUpTime: Use GenAI studio api, write a prompt to go to the model url's model card page and evaluate ease of use from the perspective of a junior dev
- Size: use "parameters" value from api

# Shriya
- ScoreCard: instantiate all submetrics and run scoring functions get to get full score and save submetric and total score values. Add function to print all results to CLI.
- AvailableDatasetAndCode: look for "tags" -> "dataset" "tags" -> "library_name"
- Dataset Quality: If dataset available, use hf api to get dataset info, check likes, downloads, license
- PerformanceClaims: use "model-index" from api to get eval results

# Mythrai
- Code Quality: if code available, use GenAI studio to assess code quality
- License: use "tags" -> "license:xxxx"
