import os
import json
import base64
import requests
from openai import OpenAI

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def fetch_file_content(file_path):
    """Fetch file content from GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        content = response.json().get("content")
        if content:
            return base64.b64decode(content).decode("utf-8")
    return None

def analyze_code(file_name, code_content):
    """Send code to OpenAI for review and security checks."""
    prompt = f"""
You are an expert software security auditor. Review the following code for security vulnerabilities and suggest improvements:

File: {file_name}
```{code_content}```

Check for:
- SQL Injection
- Hardcoded credentials or secrets
- Insufficient input validation
- Cross-site scripting (XSS)
- Insecure API usage
- Any other security vulnerabilities

Provide detailed security recommendations.
"""
    
    response = client.chat.completions.create(
        model="openai/o3-mini",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer and security analyst."},
            {"role": "user", "content": prompt},
        ],
    )
    
    return response.choices[0].message.content

def post_github_comment(pr_number, file_name, feedback):
    """Post AI security feedback on GitHub PR."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{pr_number}/comments"
    comment = {"body": f"### 🛡️ Security Audit for `{file_name}`\n\n{feedback}"}
    requests.post(url, headers=HEADERS, json=comment)

def main():
    """Run AI security checks on changed files."""
    changed_files_env = os.getenv("CHANGED_FILES", "[]")
    
    # Ensure proper JSON format handling
    try:
        changed_files = json.loads(changed_files_env)
        if not isinstance(changed_files, list):
            raise ValueError("CHANGED_FILES must be a JSON array.")
    except json.JSONDecodeError:
        print(f"Error parsing CHANGED_FILES: {changed_files_env}")
        return

    for file in changed_files:
        if file.endswith((".js", ".ts", ".jsx", ".tsx", ".py", ".sol")):
            content = fetch_file_content(file)
            if content:
                feedback = analyze_code(file, content)
                post_github_comment(PR_NUMBER, file, feedback)


if __name__ == "__main__":
    main()
