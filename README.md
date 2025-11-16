# Configuration
The code requires Python >= 3.7 because of the version of `tldextract` used (3.5.0).
We recommend that you use the same version, but you can use other versions and modify the
source code accordingly using any relevant resources (official documentation, LLMs, StackOverflow, etc.).
Use the `requirements.txt` file as reference for the packages that need to be installed.

After installing the packages referenced in the `requirements.txt` file, you can use the `helper.ipynb` file
which provides a quickstart code to complete the class project. 
The functions already implemented help with parsing information about the companies, 
generating five different types of domain transformations, and generate a file in the format expected for submission to the public leaderboard.

# Included Data
The repository includes data about 37 Fortune 500 companies.
For the 27 companies included in the training dataset, we provide
information about the companies (`companies-training.jsonl`) and about the domain names that they disputed
(`disputes-training.json`).
Conversely, for the 10 remaining companies considered as part of the validation dataset that are 
used to validate your strategies on the public leaderboard, 
we only shared information about the companies in the `companies-validation.json` file.
