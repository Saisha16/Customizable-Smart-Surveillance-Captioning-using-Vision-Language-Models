# ISHTA Git Workflow Guide
## Integration, Feedback & System Lead

---

## 📋 Quick Reference

| Action | Command | Branch |
|--------|---------|--------|
| Start work | `git pull origin main` | main |
| Switch to feature | `git checkout integration-feedback` | integration-feedback |
| Commit work | `git commit -m "message"` | integration-feedback |
| Push changes | `git push origin integration-feedback` | integration-feedback |
| Create PR | Use GitHub UI | → main |

---

## 🌱 Branch Strategy

### `main` (Production-Ready)
- Stable, tested code only
- Never commit directly
- Updated via Pull Request merges only

### `integration-feedback` (ISHTA's Feature Branch)
- Your working branch for all changes
- Pulled from daily
- Changes to:
  - `io/input_handler.py`
  - `io/alert_formatter.py`
  - `feedback/feedback_manager.py`
  - `logs/logging_system.py`

### `rule-logic` (Isha's Feature Branch)
- Isha's rule evaluation engine
- Never edit by ISHTA
- Changes to:
  - `rules/rule_engine.py`
  - `rules/zone_evaluator.py`
  - `rules/rule_registry.py`

---

## 🔄 Daily Workflow

### Morning (Start of Work)
```powershell
# Step 1: Ensure main branch is up-to-date
git pull origin main

# Step 2: Switch to integration-feedback branch
git checkout integration-feedback

# Step 3: Sync with latest main changes
git merge main  # Optional, but recommended for latest fixes
```

### During Work (Make Changes)
```powershell
# Edit files in your workspace
# Make changes to:
# - io/input_handler.py
# - io/alert_formatter.py
# - feedback/feedback_manager.py
# - logs/logging_system.py

# Verify your changes work
python -m pytest tests/

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Implemented JSON input validation with schema checking"
# OR
git commit -m "Added RLHF feedback processor for rule weight adjustments"
```

### End of Work (Push Changes)
```powershell
# Push to remote integration-feedback branch
git push origin integration-feedback

# GitHub Actions will run automated tests
# You can monitor in GitHub Actions tab
```

---

## 📤 Creating a Pull Request

### When to Create PR
- Feature is complete and tested
- All tests pass locally
- Code follows project standards
- No conflicts with main branch

### Steps (Using GitHub Web UI)
1. Go to GitHub repository
2. Click "Pull Requests" tab
3. Click "New Pull Request"
4. Set:
   - **Base**: `main`
   - **Compare**: `integration-feedback`
5. Add title: `Integration: Implemented feedback manager`
6. Add description (see template below)
7. Click "Create Pull Request"

### PR Description Template
```markdown
## Description
Brief summary of changes made.

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Enhancement

## Changes Made
- Implemented JSON input validation
- Added RLHF feedback processor
- Enhanced error handling

## Testing
- [x] Unit tests pass
- [x] Manual testing done
- [x] No merge conflicts

## Files Changed
- io/input_handler.py
- feedback/feedback_manager.py

## Related Issues
Closes #123 (if applicable)
```

---

## ✅ Code Review Process

### When Isha Reviews Your PR
1. Isha (rule-logic branch owner) will review
2. Comments on specific lines
3. You respond and make fixes if needed
4. Once approved, Isha merges PR

### Your Responsibilities
- Respond to review comments promptly
- Make requested changes
- Push updates (no need for new PR)
- Ensure all checks pass

---

## 🚫 Important Rules

### ✋ DON'T Edit
```
rules/               # Isha's territory
├── rule_engine.py
├── zone_evaluator.py
└── rule_registry.py
```

### ✅ DO Edit (Your Territory)
```
io/                  # ISHTA's files
├── input_handler.py
└── alert_formatter.py

feedback/            # ISHTA's files
└── feedback_manager.py

logs/                # ISHTA's files
└── logging_system.py
```

### 📝 main.py (Shared - Pull Request Only)
- Minimal edits through PR only
- Coordinate with Isha before changes
- Document intentions clearly

---

## 🔧 Useful Commands

### Check Status
```powershell
# See current branch and changes
git status

# See all branches
git branch -a

# See commit history
git log --oneline -5
```

### Undo Changes
```powershell
# Discard all changes (WARNING: permanent)
git checkout .

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

### Sync with Main
```powershell
# Update integration-feedback with latest main
git fetch origin
git merge origin/main
```

### Resolve Conflicts
```powershell
# If merge has conflicts:
# 1. Edit conflicted files (resolve <<<< ==== >>>>)
# 2. Stage resolved files
git add <resolved-file>

# 3. Complete merge
git commit -m "Resolved merge conflicts"
```

---

## 📊 Example: Complete Workflow

```powershell
# ========== MORNING ==========
git pull origin main
git checkout integration-feedback

# ========== WORK ==========
# Edit io/input_handler.py to add new validation

# ========== TESTING ==========
python -m pytest tests/test_input_handler.py
# ✓ All tests pass

# ========== COMMIT ==========
git add io/input_handler.py
git commit -m "Added timestamp validation with ISO 8601 format checking"

# ========== PUSH ==========
git push origin integration-feedback

# ========== CREATE PR ==========
# Go to GitHub.com → New Pull Request
# Base: main ← Compare: integration-feedback
# Add description and submit

# ========== REVIEW & MERGE ==========
# Isha reviews and approves
# PR is merged into main automatically
# Your changes now in production
```

---

## 🆘 Troubleshooting

### "Cannot push - branch diverged"
```powershell
git pull origin integration-feedback
# Resolve any conflicts
git push origin integration-feedback
```

### "Accidentally worked on main"
```powershell
git checkout integration-feedback
git cherry-pick <commit-hash>  # Move your commit to correct branch
```

### "Need to see what changed"
```powershell
git diff integration-feedback main
# Shows all differences
```

---

## 📞 Contact & Support

**Shared File Questions** → Coordinate with Isha  
**Git Issues** → Check this guide first  
**Merge Conflicts** → Communicate with Isha immediately  

---

## ✨ Pro Tips

1. **Commit Often**: Small, focused commits are easier to review
2. **Write Clear Messages**: Future you will thank present you
3. **Test Before Push**: Run tests locally first
4. **Pull Before Work**: Always sync with main in morning
5. **Review Your PR**: Double-check before requesting review

---

**Last Updated**: 2026-01-28  
**Version**: 1.0
