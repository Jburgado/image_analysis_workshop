# Getting started (using VSCode)


## Clone this github repository to your own computer
* Fork this repository

Login into [github](https://github.com). On the [github image_analysis_workshop](https://github.com/UCSF-CALM/image_analysis_workshop) page find the "Fork" button (near the right top) and click it. Create the fork under your own githhub name ("your_github_name").  

* Start VSCode
* Clone your fork:
* Click the Source control ison (icon with 3 circles, in my case on the left side).  Short cut (on Windows): Ctrl+Shift+G).
* Click "Clone Repository"
* Select "Clone from Github"
* Sign int your Github account.
* Select your Fork of this repository (created during "Installation").
* Select a location where you will store your copy of the repository (suggestions: ~/projects).
* Open the repository when prompted
* Add the UCSF_CALM repository as the "upstream" repository:
```text
git remote add upstream https://github.com/UCSF-CALM/image_analysis_workshop.git
```

## Create a git branch where you will keep your own work
under the hood, git stores differences (diffs) between versions.  You create a new version by using the command ```git commit```.  However, you will want to add your own commits to your own "branch: (so that you can always go back to a pristine state).  To create your own branch, called "my_branch" 

