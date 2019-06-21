<!-- GETTING STARTED -->
## Running the App (Untested)
* Install Docker, Docker-Compose
* Clone this repo
* Inside the repo's root directory, run `docker-compose up` to start downloading dependencies and start application
* Test application at localhost:8000

## Debugging the App (Untested)

Steps:
* Set a breakpoint anywhere in your code with the line `import pdb; pdb.set_trace()`
* Open another tab in your command prompt, and run 'docker attach screendoor'
* In your browser window, get to where the breakpoint is specified in the code
* pdb should launch in the secondary window, allowing pdb to be used

## Frequent errors
* Django 'new migration' detection is imperfect, and will sometimes brick the application as a result. Delete your migrations folder to remove Django's cache, and rerun the migration process.

## Celery and Async Functions
* This program uses Celery with RabbitMQ as a message broker to carry out scheduled and non-blocking tasks.
* Currently, this includes an instance of RabbitMQ, one Celery worker for async tasks, and one Celery Beat worker for scheduled tasks. Each is its own docker container.

### Scheduled Tasks
* Scheduled tasks have two components: the task and the scheduling.
* Like async tasks, scheduled tasks are defined as functions in tasks.py.
* The scheduled execution of those tasks is defined in screendoor_app/settings.py, under `CELERY_BEAT_SCHEDULE` using json formatting.
* The scheduled tasks follow the format:
```
'name_of_task': {
        'task': 'screendoor.tasks.function_name',
        'schedule': 60
    }
```
* The value for `'schedule'` can be seconds, or a `crontab()` value. For example, `crontab(minute=0, hour=0)` will carry out the task each day at midnight. Further documentation on crontab can be found at https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules.
* The application must be restarted if a new schedule is set or an existing schedule is changed.

### Async Tasks
* The execution of an async task is also defined in tasks.py.
* An async function existing in tasks.py, for example `process_applications()` can be imported to views.py and called from a view using the `delay()` function, e.g. `process_applications().delay`. This causes the task to be executed in the background by a celery worker, as opposed to immediately by the main Django process.
* Any parameters of the function in tasks.py should be passed into the `delay()` function, not the parent function.
* Task functions belonging to the entire application should be annotated with `@shared_task`, e.g.:
```
@shared_task
def async_function(optional_param):
    pass
```
* The `.ready()` method indicates if a task is completed, while the `.get()` method gets its return value, if any, e.g.:
```
if async_function.ready():
    result = async_function.get()
```
* The `.get()` method can be called without checking for `ready()` if a timeout value is set in the parameters of `.get()`, e.g. `result = async_function.get(timeout=60)`
* `current_task.update_state()` can be called inside a task function to specify the `state` value (`PENDING`, `STARTED`, `PROGRESS`, `SUCCESS`, `FAILURE`, `RETRY`, `RECEIVED`, etc) and any `meta` information, as a dictionary. e.g.: `meta = {'total': 25, 'completed': num_completed}`
* A task state can be queried at any time by calling `AsyncResult(task_id)`. Task id is a UUID found at `task.id`.

### Displaying task state/progress to users
* A user can be updated about task status in real time by returning `JsonResponse` objects or `json.dumps(data)` objects within an `HttpResponse`.
* This is done via an AJAX request by querying a Django URL in a JavaScript function that executes a view to check the status of the task, and returns JSON data. The JavaScript function will poll for the state of the task until it is complete.
* Below is a simple example of how this will work:
```
let queryUrl = '{% url 'task_status' task_id %}';
displayProgress(queryUrl);

function displayProgress(queryUrl) {
    fetch(queryUrl).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
        updateProgress(data.state, data.details);
        });
    });
}
```

### Monitoring via Flower
* Flower allows for the direct monitoring of Celery workers via a web dashboard. However, it is currently not properly configured and not working.
