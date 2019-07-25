/* DOM constants */
const uploadCard = document.getElementById("upload-applications-modal");
const progressBlock = document.getElementById("progress-div");
const currentNumberSpan = document.getElementById("current-number");
const totalNumberSpan = document.getElementById("total-number");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const loadingEllipses = document.getElementById("loading-ellipses");

/* Constants derived from Django variables in hidden inputs */
const queryUrl = new URL(document.getElementById("task-url").value, "http://localhost");
const reloadUrl = document.getElementById("reload-url").value;
const taskId = document.getElementById("task-id").value;

/* Variable representing ajax request timer */
let updateTimer = null;

const updateProgressText = function(total, current) {
  progressText.innerHTML = document.getElementById("progress-text-value").value;
  document.getElementById("current-number").innerHTML = current;
  document.getElementById("total-number").innerHTML = total;
};

const updateLoadingBarProgress = function(total, current) {
  progressBar.style.width = Math.floor(current * 100 / total) + "%";
};

const showEllipses = function() {
  loadingEllipses.classList.add("loading");
};

const hideEllipses = function() {
  loadingEllipses.classList.remove("loading");
};

const showProgressBar = function() {
  progressBlock.classList.remove("hide");
};

const hideProgressBar = function() {
  progressBlock.classList.add("hide");
};

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
  fetch(queryUrl).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
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
    }).catch(error => console.error());
  });
};

/* Execute and run timer if applicant file upload is taking place */
const initializeApplicantUploadProgress = function() {
  document.getElementById('files-processing').innerHTML = localStorage.getItem('applicationFiles');
  clearExceptSidebar();
  uploadModal.openInstant();
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
  if (document.getElementById("task-id") && document.getElementById("task-id").value != "None") {
    initializeApplicantUploadProgress();
  } else {
    hideProgressBar();
  }
});
