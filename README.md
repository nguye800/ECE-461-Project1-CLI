# All code that will be used in the logic for end to end function goes in src
# Utils folder will hold helper functions such as api calls and url checking
# All unittest code will go in test
# cliproject.toml holds the config to run the run.py file when the "run URL" command is used in terminal

# To Do List
- URL checking
- HF api to store model information (modify hf_api.py code) and store in cache
 - from functools import lru_cache
- Use git metadata on HF model for metric
- Use Purdue GenAI studio api to get info (modify chatgpt_api.py)
- ScoreCard:
- Size: add function to pull model parameter 
- RampUpTime:
- PerformanceClaims:
- License:
- DatasetQuality:
- Code Quality:
- BusFactor:
- AvailableDatasetAndCode: