<!-- GETTING STARTED -->
## Running the App (Untested)
* Install Docker, Docker-Compose
* Clone this repo
* Inside the repo's root directory, run 'docker-compose up' to start download dependencies and start application
* Test application at localhost:8000

## Debugging the App (Untested)
* Debugging the app is done through a python module called Wdb (web debugger)
* Wdb is a seperate server that launches with the app, and allows for interactive viewing/stepping of code, under a free liscence
* https://github.com/Kozea/wdb

Steps:
* Set a breakpoint anywhere in your code with the line 'import wdb; wdb.set_trace()'
* When your tab gets to that line, it will hang. You should see a message in your commandprompt akin to 'you can now launch your browser at ...'
* In a new tab, navigate to localhost:1984
* Click on the session id that the commandprompt specified

## Frequent errors
* Django 'new migration' detection is imperfect, and will sometimes brick the application as a result. Delete your migrations folder to remove Django's cache, and rerun the migration process.
* If a message akin to "no module named wdb" appears, run 'pip install -r requirements.txt' in the docker web shell, in another commandprompt while the instance is running. Then retry.
