<!-- GETTING STARTED -->
## Running the App (Untested)
* Install Docker, Docker-Compose
* Clone this repo
* Inside the repo's root directory, run 'docker-compose up' to start download dependencies and start application
* Test application at localhost:8000

## Debugging the App (Untested)

Steps:
* Set a breakpoint anywhere in your code with the line 'import pdb; pdb.set_trace()'
* Open another tab in your command prompt, and run 'docker attach screendoor'
* In your browser window, get to where the breakpoint is specified in the code
* pdb should launch in the secondary window, allowing pdb to be used

## Frequent errors
* Django 'new migration' detection is imperfect, and will sometimes brick the application as a result. Delete your migrations folder to remove Django's cache, and rerun the migration process.

