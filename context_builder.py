'''
    @file: context-builder.py
    @brief: This module orchestrates the process of building a context blueprint from a GitHub PR.
    It fetches PR metadata, commits, generates diffs, cleans them, and uses AI to summarize changes.
    
    @usage:
    1. Initialize the ContextBuilder with a PR URL and optional GitHub token.
    2. Call the `build()` method to run the entire process.
    3. The final context blueprint is returned as a JSON string.
'''

import logging
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- Import PyGithub ---
from github import Github, GithubException, UnknownObjectException
from github.Repository import Repository


# --- Import utilities and prompts ---
from llm_utils import get_llm_service
from prompts import PROMPT_LIBRARY

# --- Import Pydantic ---
from pydantic import BaseModel, Field
import json


# --- Pydantic Schemas for Validation ---
class CommitModel(BaseModel):
    sha: str
    short_sha: str
    message: str
    author_name: str
    date: str
    url: str

class PRMetadataModel(BaseModel):
    title: str
    author: str
    description: Optional[str] = None # Optional description
    url: str

class ChangesModel(BaseModel):
    ai_summary: str
    non_text_files: List[str] = Field(..., alias="non_text_files_changed")
    raw_diff: str = Field(..., alias="text_diff")

class ContextBlueprint(BaseModel):
    pr_summary: PRMetadataModel
    selected_commits: List[CommitModel]
    changes: ChangesModel
    generation_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())



# --- Define AI Client ---
llm = get_llm_service()

# Filters
# --- (NEW) Define common binary file extensions ---
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp', # Image files
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', # Document files
    '.zip', '.tar', '.gz', '.rar', '.7z', # Archive files
    '.exe', '.dll', '.so', '.jar', '.class', # Executable and library files
    '.mp4', '.mov', '.avi', '.mp3', '.wav', # Media files
    '.svg',  # Vector images (can be text, but often treated as binary)
    '.psd', '.ai', '.eps',  # Adobe/graphics files
    '.ttf', '.otf', '.woff', '.woff2',  # Fonts
    '.bin', '.dat',  # Generic binary/data files
    '.apk', '.ipa',  # Mobile app packages
    '.dmg', '.iso',  # Disk images
    '.pkl', '.joblib',  # Python serialized objects
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class ContextBuilder:
    """
    A class to orchestrate the entire process of building a context blueprint from a GitHub PR.
    """
    
    def __init__(self, pr_url: str, gh_token: str = None):
        """
        Initializes the builder with the PR URL and GitHub token.
        """
        self.pr_url = pr_url
        self.gh_token = gh_token or os.getenv("GITHUB_TOKEN")
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize state attributes
        self.repo: Optional[Repository] = None
        self.pr_metadata: Dict[str, Any] = {}
        self.all_commits: List[Dict[str, Any]] = []
        self.selected_commits: List[Dict[str, Any]] = []
        self.diff_data: Dict[str, Any] = {}
        self.cleaned_diff: str = ""
        self.change_description: str = ""
        self.final_blueprint: Optional[str] = None
        
    def build(self) -> Optional[str]:
        """
        The main public method to run the entire context building workflow.
        """
        self.logger.info(f"Starting context build for {self.pr_url}")
        
        if not self._fetch_pr_data(): return None
        self._select_commits()
        if not self.selected_commits: return None
        
        self._get_diff()
        if not self.diff_data or not self.diff_data.get("text_diff"):
            self.logger.warning("No text diff generated. Stopping process.")
            return None
        
        self._clean_diff()
        self._generate_ai_summary()
        
        if not self.change_description: return None
        self._build_final_json()
        return self.final_blueprint
    
    def _fetch_pr_data(self) -> bool:
        """
        Fetches the PR metadata and commit history from GitHub.
        Returns True if successful, False otherwise.
        """
        
        self.logger.info("Step 1: Fetching PR metadata and commits...")
        pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.match(pattern, self.pr_url)
        if not match:
            self.logger.error("Invalid GitHub PR URL format.")
            return False
        
        owner, repo_name, pr_number = match.groups()


        try:
            github = Github(self.gh_token)
            self.repo = github.get_repo(f"{owner}/{repo_name}")
            pr = self.repo.get_pull(int(pr_number))
            commits_paginated_list = pr.get_commits()

            self.pr_metadata = {'title': pr.title, 'author': pr.user.login, 'description': pr.body, 'url': pr.html_url}
            for commit in commits_paginated_list:
                self.all_commits.append({
                    'sha': commit.sha, 'short_sha': commit.sha[:7], 'message': commit.commit.message,
                    'author_name': commit.commit.author.name, 'date': commit.commit.author.date.isoformat(),
                    'url': commit.html_url
                })

            print(f"\n--- PR Metadata ---\nTitle:    {self.pr_metadata['title']}\nAuthor:   {self.pr_metadata['author']}\n-------------------\n")
            print("--- Commit Timeline ---")
            for commit in self.all_commits:
                print(f"- {commit['short_sha']}: {commit['message'].splitlines()[0]} ({commit['author_name']})")
            print("-----------------------\n")
            return True
        except (UnknownObjectException, GithubException) as e:
            self.logger.error(f"API Error during fetch: {e}")
            return False

    def _select_commits(self):
        self.logger.info("Step 2: Awaiting user selection of commits...")
        self.selected_commits = select_individual_commits(self.all_commits) # Using the standalone function
        if self.selected_commits:
            print("\n--- You have selected the following commits ---")
            for commit in self.selected_commits:
                print(f"- {commit['short_sha']}: {commit['message'].splitlines()[0]}")
            print("-------------------------------------------\n")
            
    def _get_diff(self):
        self.logger.info("Step 3: Generating combined diff...")
        self.diff_data = get_combined_diff(self.repo, self.selected_commits) # Using the standalone function

    def _clean_diff(self):
        self.logger.info("Step 4: Cleaning diff text...")
        self.cleaned_diff = clean_diff_text(self.diff_data.get("text_diff", "")) # Using the standalone function

    def _generate_ai_summary(self):
        self.logger.info("Step 5: Generating AI summary from diff...")
        task = "change_description"
        prompt_template = PROMPT_LIBRARY.get(task)
        if prompt_template and self.cleaned_diff:
            llm = get_llm_service()
            user_prompt = prompt_template["user"].format(pr_description=self.pr_metadata.get("description", ""), cleaned_diff=self.cleaned_diff)
            self.change_description = llm.get_response(user_prompt, prompt_template["system"])

    def _build_final_json(self):
        self.logger.info("Step 6: Aggregating and validating final blueprint...")
        try:
            full_context = {
                "pr_summary": self.pr_metadata,
                "selected_commits": self.selected_commits,
                "changes": {"ai_summary": self.change_description, **self.diff_data}
            }
            validated_blueprint = ContextBlueprint.model_validate(full_context)
            self.final_blueprint = validated_blueprint.model_dump_json(indent=2)
            self.logger.info("Blueprint validation successful.")
        except Exception as e:
            self.logger.error(f"Failed to build or validate the JSON blueprint: {e}")
            
    
# --- Standalone helper functions used by the class ---
def select_individual_commits(all_commits: list):
    if not all_commits: return []
    commit_map = {c['short_sha']: c for c in all_commits}
    selected_commits = []
    while True:
        prompt = "Enter the short SHAs of the commits to include, separated by spaces: "
        user_input = input(prompt).strip().lower()
        if not user_input: continue
        input_shas = user_input.split()
        valid_shas, all_valid = [], True
        for sha in input_shas:
            if sha in commit_map:
                valid_shas.append(sha)
            else:
                print(f"Error: SHA '{sha}' is not valid. Please try again.")
                all_valid = False
        if all_valid:
            for sha in valid_shas:
                selected_commits.append(commit_map[sha])
            break
    return selected_commits

def get_combined_diff(repo: Repository, selected_commits: list):
    if not selected_commits: return None
    selected_commits.sort(key=lambda x: x['date'])
    start_commit_sha, end_commit_sha = selected_commits[0]['sha'], selected_commits[-1]['sha']
    try:
        base_commit = repo.get_commit(sha=start_commit_sha)
        if not base_commit.parents: return None
        base_sha = base_commit.parents[0].sha
        comparison = repo.compare(base=base_sha, head=end_commit_sha)
        text_diffs, non_text_files = [], []
        for file in comparison.files:
            is_binary = not file.patch or os.path.splitext(file.filename)[1].lower() in BINARY_EXTENSIONS
            if is_binary: non_text_files.append(f"{file.status.capitalize()}: {file.filename}")
            else: text_diffs.append(file.patch)
        return {"text_diff": "\n".join(text_diffs), "non_text_files_changed": non_text_files}
    except GithubException: return None

def clean_diff_text(raw_diff: str):
    if not raw_diff: return ""
    lines = [line for line in raw_diff.splitlines() if not (line.startswith("diff --git") or line.startswith("index ") or line.startswith("--- a/") or line.startswith("+++ b/") or line.startswith("@@ "))]
    return "\n".join(lines)


# --- Example usage ---
# Uncomment the following lines to run the example usage directly.
# This is useful for testing the context builder in isolation.


# if __name__ == "__main__":
#     # --- Example Usage ---
#     # 1. Ensure API keys are set as environment variables (GITHUB_TOKEN, GEMINI_API_KEY, etc.)
    
#     pr_to_analyze = "https://github.com/apache/beam/pull/35564"
    
#     # 2. Create an instance of the builder
#     builder = ContextBuilder(pr_url=pr_to_analyze)
    
#     # 3. Run the entire process with a single method call
#     final_json_blueprint = builder.build()

#     if final_json_blueprint:
        
#         # store the final blueprint in context.json
#         with open("context.json", "w") as f:
#             f.write(final_json_blueprint)
        
#         print("\n✅ --- Final Context Blueprint Generated --- ✅")
#         blueprint_dict = json.loads(final_json_blueprint)
#         print(blueprint_dict["changes"]["ai_summary"])
#         # You can now save this to a file or pass it to the next service.
#     else:
#         print("\n❌ Failed to build the context blueprint. Check logs for details.")