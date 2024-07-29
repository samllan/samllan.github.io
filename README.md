# main_portfolio_repo

A new Flutter project.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.

## First time set up steps

git init  
git add .  
git commit -m "Initial commit"  
git remote add origin https://github.com/your-username/your-username.github.io.git  
git push -u origin main  

mkdir -p .github/workflows  
nano .github/workflows/deploy.yml  

git add .github/workflows/deploy.yml  
git commit -m "Add GitHub Action for deployment"  
git push origin main  

## Thereafter

git add .  
git commit -m "Describe your changes"  
git push origin main  

> ### GitHub Actions Trigger:
> 
> GitHub detects the push to the main branch.  
> The deploy.yml workflow is triggered.  
> 
> ### Workflow Steps:
> 
> Checkout the repository: Pulls the latest code from main.
> Set up Flutter: Installs the specified Flutter version.
> Install dependencies: Runs flutter pub get.
> Build web app: Executes flutter build web --release.
> Move build output: Moves the contents of build/web to the docs directory.
> Commit and push changes: Adds, commits, and pushes the changes to the docs directory back to the main branch.
