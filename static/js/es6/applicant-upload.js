/* Div containing progress information */
const progressBlock = document.getElementById("progress-div");

/* Div containing progress bar within progressBlock */
const progressBar = document.getElementById("progress-bar");

/* Span containing text describing upload progress */
const progressText = document.getElementById("progress-text");

/* Button to close upload modal */
const cancelUploadButton = document.getElementById("cancel-upload-applications");

/* Hidden input containing current task ID */
const taskId = document.getElementById("task-id");

/* URL for current position to reload upon completing upload */
const reloadUrl = document.getElementById("reload-url").value;

/* TaskData dictionary to sent with AJAX request */
const taskData = Object.create(null);
taskData["taskId"] = taskId.value;

/* Variable representing ajax request timer */
let updateTimer = null;

/* Update the text describing upload progress */
const updateProgressText = function(total, current) {
  progressText.innerHTML = document.getElementById("progress-text-value").value;
  document.getElementById("current-number").innerHTML = current;
  document.getElementById("total-number").innerHTML = total;
};

/* Update loading bar progress */
const updateLoadingBarProgress = function(total, current) {
  progressBar.style.width = Math.floor(current * 100 / total) + "%";
};

/* Show progress bar */
const showProgressBar = function() {
  progressBlock.classList.remove("hide");
};

/* Hide progress bar */
const hideProgressBar = function() {
  progressBlock.classList.add("hide");
};

/* Update all progress */
const updateProgress = function(state, meta) {
  let total = meta.total;
  let current = meta.current;
  updateLoadingBarProgress(total, current);
  updateProgressText(total, current);
};

/* Display error message on applicant upload modal */
const displayError = function() {
  console.error();
  clearInterval(updateTimer);
  progressText.innerHTML = document.getElementById("upload-error-text").value;
};

/* Define what message displays on the applicant uploading modal */
const displayProgress = function(queryUrl) {
  fetch(queryUrl, {
    method: "POST",
    body: JSON.stringify(taskData), // data can be `string` or {object}!
    headers:{
      "Content-Type": "application/json"
    }
  }).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      if (data.state == "PENDING") {
        progressText.innerHTML = document.getElementById("calculating-applicants-text").value + ": " + data.meta.total;
      } else if (data.state == "PROGRESS") {
        showProgressBar();
        updateProgress(data.state, data.meta);
      } else if (data.state == "SUCCESS") {
        clearInterval(updateTimer);
        uploadModal.close(); // from sd-modal.js
        window.location.assign(reloadUrl);
      } else if (data.state == "FAILURE") {
        displayError();
      }
    }).catch(error => console.error());
  });
};

/* Execute and run timer if applicant file upload is taking place */
const initializeApplicantUploadProgress = function() {
  document.getElementById("files-processing").innerHTML = localStorage.getItem("applicationFiles");
  clearExceptSidebar(); // from localstorage.js
  uploadModal.openInstant(); // from sd-modal.js
  const queryUrl = new URL(document.getElementById("task-url").value, "http://localhost");
  try {
    displayProgress(queryUrl.href);
    updateTimer = setInterval(function() {
      displayProgress(queryUrl.href);
    }, 1000);
  } catch (e) {
    clearInterval(updateTimer);
  }
};

/* Show upload progress if there is a valid task ID */
window.addEventListener("load", function() {
  cancelUploadButton.addEventListener("click", () => {
    document.getElementById("upload-applications-error-text").style.display = "none";
  });

  if (document.getElementById("upload-applications-error-text") && document.getElementById("upload-applications-error-text").value != "None") {
    uploadApplicantModal.openInstant(); // from sd-modal.js
  }
  if (document.getElementById("task-id") && document.getElementById("task-id").value != "None") {
    initializeApplicantUploadProgress();
  } else {
    hideProgressBar();
  }
});
