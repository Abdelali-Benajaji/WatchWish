# Git & GitHub Guide for WatchWish

## Initial Setup

### 1. Initialize Git Repository

```bash
cd WatchWish
git init
```

### 2. Add Remote Repository

```bash
git remote add origin <your-github-repo-url>
```

### 3. Initial Commit

```bash
git add .
git commit -m "feat: initial project setup with Django, MongoDB, and Docker"
git branch -M main
git push -u origin main
```

## Branch Strategy

### Main Branches

- **main**: Production-ready code
- **develop**: Development integration branch

### Supporting Branches

- **feature/**: New features
- **bugfix/**: Bug fixes
- **hotfix/**: Urgent production fixes
- **release/**: Release preparation

### Branch Naming Convention

```
feature/WISH-XX-short-description
bugfix/WISH-XX-short-description
hotfix/WISH-XX-short-description
```

Example:
```bash
feature/WISH-85-git-github-setup
feature/WISH-86-docker-architecture
```

## Workflow

### Creating a Feature Branch

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/WISH-85-git-setup

# Work on your changes...
git add .
git commit -m "feat(git): setup git repository and configuration"

# Push to remote
git push -u origin feature/WISH-85-git-setup
```

### Merging Back to Main

```bash
# Update your branch
git checkout feature/WISH-85-git-setup
git pull origin main
git merge main

# Resolve conflicts if any
# Then push
git push

# Create Pull Request on GitHub
# After approval, merge and delete branch
git checkout main
git pull origin main
git branch -d feature/WISH-85-git-setup
```

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples

```bash
# Simple feature
git commit -m "feat(movies): add movie import command"

# Bug fix with body
git commit -m "fix(api): resolve pagination issue

Movies API was returning incorrect page numbers
when filtering by year. Updated the queryset
to properly handle pagination."

# Breaking change
git commit -m "feat(api)!: change movie serializer structure

BREAKING CHANGE: Movie API response structure has changed.
The 'genres' field is now an array of objects instead of strings."
```

## Useful Git Commands

### Status and Changes

```bash
# Check status
git status

# View changes
git diff

# View staged changes
git diff --staged

# View commit history
git log --oneline --graph --all

# Beautiful log
git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
```

### Stashing Changes

```bash
# Stash current changes
git stash

# List stashes
git stash list

# Apply latest stash
git stash apply

# Apply and remove stash
git stash pop
```

### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- <file>

# Unstage file
git reset HEAD <file>

# Amend last commit
git commit --amend

# Reset to previous commit (careful!)
git reset --hard HEAD~1
```

### Branch Management

```bash
# List branches
git branch

# List all branches (including remote)
git branch -a

# Delete local branch
git branch -d <branch-name>

# Delete remote branch
git push origin --delete <branch-name>

# Rename current branch
git branch -m <new-name>
```

## .gitignore

The project already includes a comprehensive `.gitignore` file that excludes:

- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments
- Django static files and database
- Environment files (`.env`)
- IDE files
- Docker overrides
- MongoDB data files

### Adding More Ignores

Edit `.gitignore`:

```bash
# Add your patterns
echo "my-local-file.txt" >> .gitignore
git add .gitignore
git commit -m "chore: update gitignore"
```

## GitHub Best Practices

### Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
Brief description of changes

## Related Issues
Closes #XX

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows project style
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No console errors
```

### Issue Template

Create `.github/ISSUE_TEMPLATE.md`:

```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS:
- Browser:
- Version:
```

## Collaboration Tips

### Before Starting Work

```bash
# Always pull latest changes
git checkout main
git pull origin main
git checkout -b feature/your-feature
```

### While Working

```bash
# Commit frequently
git add .
git commit -m "feat: add specific functionality"

# Push regularly
git push origin feature/your-feature
```

### Before Submitting PR

```bash
# Update from main
git checkout main
git pull origin main
git checkout feature/your-feature
git merge main

# Resolve conflicts
# Run tests
docker-compose exec web python manage.py test

# Push
git push origin feature/your-feature
```

## Task Tracking (WISH-84 Subtasks)

### WISH-85: Git & GitHub
```bash
git checkout -b feature/WISH-85-git-github
# Setup git, create repo, configure
git commit -m "feat(git): complete WISH-85 git and github setup"
```

### WISH-86: Architecture
```bash
git checkout -b feature/WISH-86-architecture
# Setup directory structure
git commit -m "feat(structure): complete WISH-86 repository architecture"
```

### WISH-87: Docker Configuration
```bash
git checkout -b feature/WISH-87-docker-config
# Setup Docker and docker-compose
git commit -m "feat(docker): complete WISH-87 docker configuration"
```

### WISH-88: Dependencies
```bash
git checkout -b feature/WISH-88-dependencies
# Setup requirements.txt
git commit -m "feat(deps): complete WISH-88 dependency management"
```

### WISH-89: Gitignore Setup
```bash
git checkout -b feature/WISH-89-gitignore
# Configure .gitignore
git commit -m "feat(git): complete WISH-89 gitignore configuration"
```

## Helpful Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --graph --oneline --all
    amend = commit --amend --no-edit
```

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
