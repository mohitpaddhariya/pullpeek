import logging
import os
import re
from typing import List
from datetime import datetime

# --- Import PyGithub ---
from github import Github, GithubException, UnknownObjectException
from github.Repository import Repository


# --- Import utilities and prompts ---
from llm_utils import get_llm_service
from prompts import PROMPT_LIBRARY, EXAMPLE_CHANGE_DESCRIPTION

# --- Import Pydantic ---
from pydantic import BaseModel, Field


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

def process_pr_url(pr_url: str, gh_token: str = None):
    '''
    Validates a GitHub PR URL and fetches its data using the PyGithub library.
    '''
    
    logging.info(f"Processing PR URL: {pr_url}")
    
    # --- URL Validation ---
    pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, pr_url)
    
    if not match:
        logging.error("Invalid GitHub PR URL format.")
        return None
    
    owner, repo_name, pr_number_str = match.groups()
    
    pr_number = int(pr_number_str)
    
    # --- Fetch PR metadata and commit histroy ---
    try:
        token = gh_token
        if not token:
            logging.warning("No GITHUB_TOKEN found. PyGithub works best with a token.")
            
        # Create a Github instance
        github = Github(token)
        
        logging.info("Fetching repository object...")
        repo = github.get_repo(f"{owner}/{repo_name}")

        logging.info(f"Fetching pull request #{pr_number}...")
        pr = repo.get_pull(pr_number)
        
        logging.info("Fetching commits for the PR...")
        commits = pr.get_commits()
    except UnknownObjectException as e:
        # This error is thrown for 404 Not Found
        logging.error("Repository or Pull Request not found. Check the URL.")
        return None
    except GithubException as e:
        # Handles other API-related errors (like rate limiting)
        logging.error(f"An error occurred with the GitHub API: {e}")
        return None
    
    # --- Store data in proper structures ---
    logging.info("Structuring PR metadata and commit data.")
    
    pr_metadata = {
        'title': pr.title,
        'author': pr.user.login,
        'status': pr.state,
        'body': pr.body,
        'url': pr.html_url,
        'commits_count': pr.commits,
        'changed_files': pr.changed_files,
        'additions': pr.additions,
        'deletions': pr.deletions,
    }
    
    structured_commits = []
    for commit in commits:
        structured_commits.append({
            'sha': commit.sha,
            'short_sha': commit.sha[:7],
            'message': commit.commit.message,
            'author_name': commit.commit.author.name,
            'date': commit.commit.author.date.isoformat(),
            'url': commit.html_url,
        })

    
    # --- Display fetched info for user ---
    print("\n--- PR Metadata ---")
    print(f"Title:    {pr_metadata['title']}")
    print(f"Author:   {pr_metadata['author']}")
    print("-------------------\n")
    
    print("--- Commit Timeline ---")
    for commit in structured_commits:
        message_first_line = commit['message'].split('\n')[0]
        print(f"- {commit['short_sha']}: {message_first_line} ({commit['author_name']})")
    print("-----------------------\n")
    
    return pr_metadata, structured_commits, repo

def select_individual_commits(all_commits: list):
    """
    Prompts the user to select individual commits by entering their short SHAs.

    Args:
        all_commits: A list of structured commit dictionaries.

    Returns:
        A new list containing only the user-selected commits.
    """

    logging.info("Awaiting user input for individual commit selection.")
    if not all_commits:
        logging.warning("No commits to select from.")
        return []
    
    commit_map = {c['short_sha']: c for c in all_commits}
    selected_commits = []

    while True:
        prompt = "Enter the short SHAs of the commits to include, separated by spaces: "
        user_input = input(prompt).strip().lower()
        
        if not user_input:
            logging.warning("No input provided. Please enter a valid short SHA or 'done'.")
            continue
        
        input_shas = user_input.split()
        
        # Validate all SHAs before proceeding
        valid_shas = []
        
        all_shas_are_valid = True
        
        for sha in input_shas:
            if sha in commit_map:
                valid_shas.append(sha)
            else:
                print(f"Error: SHA '{sha}' is not valid. Please try again.")
                all_shas_are_valid = False
                
        if all_shas_are_valid:
            for sha in valid_shas:
                selected_commits.append(commit_map[sha])
            break # Exit loop if all inputs were valid
        
    logging.info(f"User selected {len(selected_commits)} individual commits.")
    return selected_commits

def get_combined_diff(repo: Repository, selected_commits: list):
    """
    Calculates and returns the combined diff for a list of selected commits.
    """
    if not selected_commits:
        logging.warning("No commits selected, cannot generate a diff.")
        return None

    logging.info("Generating combined diff for selected commits.")
    
    selected_commits.sort(key=lambda x: x['date'])
    start_commit_sha = selected_commits[0]['sha']
    end_commit_sha = selected_commits[-1]['sha']

    try:
        base_commit = repo.get_commit(sha=start_commit_sha)
        if not base_commit.parents:
            logging.error(f"Commit {start_commit_sha} has no parents, cannot create a diff.")
            return None
        base_sha = base_commit.parents[0].sha
        
        logging.info(f"Comparing base '{base_sha[:7]}' with head '{end_commit_sha[:7]}'")
        comparison = repo.compare(base=base_sha, head=end_commit_sha)
        
        text_diffs = []
        non_text_files_changed = []
        
        # --- OPTIMIZATION: Combine filtering and collection into a single loop ---
        for file in comparison.files:
            is_binary = not file.patch
            
            if not is_binary:
                _, extension = os.path.splitext(file.filename)
                if extension.lower() in BINARY_EXTENSIONS:
                    is_binary = True
                    
            if is_binary:
                non_text_files_changed.append(f"{file.status.capitalize()}: {file.filename}")
            else:
                text_diffs.append(file.patch)
                
        logging.info(f"Diff analysis complete. Found {len(text_diffs)} text files and {len(non_text_files_changed)} non-text files.")

        return {
            "text_diff": "\n".join(text_diffs),
            "non_text_files_changed": non_text_files_changed
        }

    except GithubException as e:
        logging.error(f"Failed to generate diff from GitHub API: {e}")
        return None

def clean_diff_text(raw_diff: str):
    """
    Removes Git metadata headers from a raw diff string to prepare it for an LLM.
    """
    if not raw_diff:
        return ""
        
    cleaned_lines = []
    for line in raw_diff.splitlines():
        # Exclude the file and hunk headers
        if (
            not line.startswith("diff --git") and
            not line.startswith("index ") and
            not line.startswith("--- a/") and
            not line.startswith("+++ b/") and
            not line.startswith("@@ ")
        ):
            cleaned_lines.append(line)
            
    logging.info("Successfully cleaned raw diff text by removing headers.")
    return "\n".join(cleaned_lines)

def generate_change_description(cleaned_diff: str):
    """
    Generates a change description using the LLM based on the cleaned diff.
    """
    
    if not cleaned_diff:
        logging.warning("No cleaned diff provided for change description generation.")
        return None
    
    # 1. Get the prompt templates for our desired task
    task = "change_description"
    prompt_template = PROMPT_LIBRARY.get(task)
    
    if not prompt_template:
        logging.error(f"No prompt template found for task '{task}'.")
        return None
    
    # 2. Get the LLM service instance
    llm = get_llm_service()
    
    # 3. Format the user prompt
    user_prompt = prompt_template["user"].format(cleaned_diff=cleaned_diff)

    logging.info("Making LLM call for change description generation.")

    # 4. Call the LLM with the correct prompts
    change_description = llm.get_response(
        user_prompt=user_prompt,
        system_prompt=prompt_template["system"]
    )

    if change_description:
        print("\n--- AI-Generated Change Description ---")
        print(change_description)
        print("-------------------------------------")

    return change_description

def build_context_json(pr_metadata: dict, selected_commits: list, diff_data: dict, change_description: str):
    """
    Aggregates all collected data into a structured and validated JSON blueprint.
    """
    logging.info("Aggregating and validating the final context blueprint...")
    try:
        # Combine all data into one dictionary
        full_context_data = {
            "pr_summary": pr_metadata,
            "selected_commits": selected_commits,
            "changes": {
                **diff_data,  # Unpacks text_diff and non_text_files_changed
                "ai_summary": change_description
            }
        }
        
        # Validate the data against the Pydantic model
        validated_blueprint = ContextBlueprint.model_validate(full_context_data)
        
        # Return a pretty-printed JSON string
        logging.info("Blueprint validation successful.")
        return validated_blueprint.model_dump_json(indent=2)
        
    except Exception as e:
        logging.error(f"Failed to build or validate the JSON blueprint: {e}")
        return None

# --- Main Execution ---
if __name__ == "__main__":
    sample_pr_url = "https://github.com/monkeytypegame/monkeytype/pull/6698"
    pr_data, all_commits, repo_obj = process_pr_url(sample_pr_url)

    if all_commits:
        selected_commits = select_individual_commits(all_commits)
        
        print("\n--- You have selected the following commits ---")
        if selected_commits:
            for commit in selected_commits:
                print(f"- {commit['short_sha']}: {commit['message'].splitlines()[0]}")
        else:
            print("No commits were selected.")
        print("-------------------------------------------\n")
        
        # Call the new function to get the diff
        diff_data = get_combined_diff(repo_obj, selected_commits)
            
        if diff_data:

                # Clean the diff text for LLM usage
                cleaned_diff = clean_diff_text(diff_data["text_diff"])
            
                # print("\n--- Non-Text Files Changed ---")
                # if diff_data["non_text_files_changed"]:
                #     for item in diff_data["non_text_files_changed"]:
                #         print(f"- {item}")
                # else:
                #     print("None")
                # print("------------------------------")

                # print("\n--- Cleaned Diff for LLM ---")
                # print(cleaned_diff)
                # print("----------------------------")
                
                if cleaned_diff:
                    # Generate the change description
                    change_description = generate_change_description(cleaned_diff)
                    
                    if change_description:
                        # --- FINAL STEP ---
                        final_context = build_context_json(
                            pr_metadata=pr_data,
                            selected_commits=selected_commits,
                            diff_data=diff_data,
                            change_description=change_description
                        )
                        
                        if final_context:
                            print("\n✅ --- Final Context Blueprint Generated --- ✅")
                            print(final_context)
                            # This 'final_context' string is the final output of this component.
                            # It can now be saved or passed to the next service.
