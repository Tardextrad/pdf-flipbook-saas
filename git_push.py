import os
import subprocess

def run_git_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def push_to_github():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("GitHub token not found in environment variables")
        return False

    commands = [
        'git config --global credential.helper store',
        'git config --global user.name "Replit User"',
        'git config --global user.email "replit@example.com"',
        'git init',  # Reinitialize the repository
        'git add -A',  # Add all files
        'git commit -m "Initial commit: Complete PDF Flipbook SaaS implementation" --allow-empty',  # Force a commit
        'git remote remove origin || true',  # Remove if exists
        f'git remote add origin "https://x-access-token:{token}@github.com/Tardextrad/pdf-flipbook-saas.git"',
        'git branch -M main',  # Rename current branch to main
        'git push -u origin main --force'  # Force push to overcome any conflicts
    ]
    
    for command in commands:
        if not run_git_command(command):
            return False
    return True

if __name__ == '__main__':
    success = push_to_github()
    print("Git push completed successfully" if success else "Git push failed")
