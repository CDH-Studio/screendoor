"use strict";

/* DOM constants */
var uploadCard = document.getElementById("upload-applications-modal");
var progressBlock = document.getElementById("progress-div");
var currentNumberSpan = document.getElementById("current-number");
var totalNumberSpan = document.getElementById("total-number");
var progressBar = document.getElementById("progress-bar");
var progressText = document.getElementById("progress-text");
var loadingEllipses = document.getElementById("loading-ellipses");
var cancelUploadButton = document.getElementById("cancel-upload-applications");

/* Constants derived from Django variables in hidden inputs */
var queryUrl = new URL(document.getElementById("task-url").value, window.location.protocol + window.location.hostname);
var taskId = document.getElementById("task-id");
var reloadUrl = document.getElementById("reload-url").value;
var taskData = Object.create(null);
taskData["taskId"] = taskId.value;

/* Variable representing ajax request timer */
var updateTimer = null;

var updateProgressText = function updateProgressText(total, current) {
  progressText.innerHTML = document.getElementById("progress-text-value").value;
  document.getElementById("current-number").innerHTML = current;
  document.getElementById("total-number").innerHTML = total;
};

var updateLoadingBarProgress = function updateLoadingBarProgress(total, current) {
  progressBar.style.width = Math.floor(current * 100 / total) + "%";
};

var showEllipses = function showEllipses() {
  loadingEllipses.classList.add("loading");
};

var hideEllipses = function hideEllipses() {
  loadingEllipses.classList.remove("loading");
};

var showProgressBar = function showProgressBar() {
  progressBlock.classList.remove("hide");
};

var hideProgressBar = function hideProgressBar() {
  progressBlock.classList.add("hide");
};

var updateProgress = function updateProgress(state, meta) {
  var total = meta.total;
  var current = meta.current;
  updateLoadingBarProgress(total, current);
  updateProgressText(total, current);
};

/* Display error message on applicant upload modal */
var displayError = function displayError() {
  console.error();
  clearInterval(updateTimer);
  progressText.innerHTML = document.getElementById("upload-error-text").value;
};

/* Define what message displays on the applicant uploading modal */
var displayProgress = function displayProgress(queryUrl) {
  fetch(queryUrl, {
    method: "POST",
    body: JSON.stringify(taskData), // data can be `string` or {object}!
    headers: {
      "Content-Type": "application/json"
    }
  }).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      if (data.state == "PENDING") {
        progressText.innerHTML = document.getElementById("calculating-applicants-text").value + ": " + data.meta.total;
      } else if (data.state == "PROGRESS") {
        showProgressBar();
        updateProgress(data.state, data.meta);
      } else if (data.state == "SUCCESS") {
        clearInterval(updateTimer);
        uploadModal.close();
        window.location.assign(reloadUrl);
      } else if (data.state == "FAILURE") {
        displayError();
      }
    }).catch(function (error) {
      return console.error();
    });
  });
};

/* Execute and run timer if applicant file upload is taking place */
var initializeApplicantUploadProgress = function initializeApplicantUploadProgress() {
  document.getElementById("files-processing").innerHTML = localStorage.getItem("applicationFiles");
  clearExceptSidebar();
  uploadModal.openInstant();
  try {
    displayProgress(queryUrl.href);
    updateTimer = setInterval(function () {
      displayProgress(queryUrl.href);
    }, 1000);
  } catch (e) {
    clearInterval(updateTimer);
  }
};

/* Show upload progress if there is a valid task ID */
window.addEventListener("load", function () {
  cancelUploadButton.addEventListener("click", function () {
    document.getElementById("upload-applications-error-text").style.display = "none";
  });

  if (document.getElementById("upload-applications-error-text") && document.getElementById("upload-applications-error-text").value != "None") {
    uploadApplicantModal.openInstant();
  }
  if (document.getElementById("task-id") && document.getElementById("task-id").value != "None") {
    initializeApplicantUploadProgress();
  } else {
    hideProgressBar();
  }
});