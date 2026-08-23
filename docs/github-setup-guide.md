# GitHub setup guide for the team

This guide assumes everyone is new to GitHub and already has Git and Visual Studio Code installed.

## 1. Create GitHub accounts

Each person goes to [github.com](https://github.com), selects **Sign up**, verifies their email address, and chooses a username. Share your GitHub username with the team leader.

## 2. Team leader: create the public repository

1. Sign in to GitHub and select the **+** menu, then **New repository**.
2. Choose an owner (the leader's personal account is fine for a class project).
3. Enter a repository name, such as `team-project`.
4. Set the visibility to **Public**.
5. Select **Create repository**. Do not add a README if the team already has this local project folder.
6. Copy the repository HTTPS URL from the **Code** button.

## 3. Team leader: publish the local project with VS Code

1. Open this project folder in VS Code.
2. Select the **Source Control** icon in the left sidebar.
3. Stage `README.md`, `minutes.md`, and any initial project files by selecting **+** next to each file.
4. Enter the commit message `Initial team project structure` and select **Commit**.
5. Select **Publish Branch**. If asked, sign in to GitHub and select the new public repository.
6. Confirm on GitHub that the repository is public and that the README is visible.

If **Publish Branch** is not offered, open the VS Code terminal and run:

```powershell
git remote add origin https://github.com/LEADER-USERNAME/REPOSITORY-NAME.git
git branch -M main
git push -u origin main
```

## 4. Invite teammates

On GitHub, open the repository, choose **Settings → Collaborators**, then invite each teammate by GitHub username. Teammates accept their invitation by email or GitHub notification.

## 5. Each teammate: add a README profile

1. In VS Code, choose **Source Control → … → Pull** (or **Sync Changes**) to update `main`.
2. Select the branch name in the bottom-left corner, choose **Create new branch**, and name it `member/your-name-readme`.
3. Edit only your own section of `README.md`.
4. In Source Control, stage `README.md`, commit with `Add <name> team profile`, then select **Publish Branch**.
5. On GitHub, choose **Compare & pull request**, write a short description, and create the pull request.
6. The team leader reviews and merges the pull request into `main`.

## 6. Team rules

- Work in a branch; do not commit directly to `main` unless you are the leader making initial setup changes.
- Pull or sync before beginning work and after a teammate’s change is merged.
- Use meaningful commit messages.
- Only the team leader edits `minutes.md`.
- Store code in `src/`, tests in `tests/`, slides in `slides/`, and other documents in `docs/`.
