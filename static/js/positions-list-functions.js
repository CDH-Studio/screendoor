/* Positions list specific constants */
const positionIdList = document.getElementsByClassName("position-id-list");
const positionReferenceList = document.getElementsByClassName("position-reference-list");
const positionApplicantUploadText = document.getElementsByClassName("position-applicant-text");
const positionTitleList = document.getElementsByClassName("position-title-list");
const positionDeleteButtons = document.getElementsByClassName("delete-button");
const positionUploadButtons = document.getElementsByClassName("upload-applicants-button");
const positionIdForUpload = document.getElementById("upload-applications-id");
const positionIdForDelete = document.getElementById("delete-confirm-id");
const textForDeleteModal = document.getElementById("delete-text");
const textForUploadModal = document.getElementById("upload-applications-text");

/* For position list view: Gets position ID to correctly display delete confirmation message, and to set position ID in the delete form */
const assignDeleteValues = function(i) {
  positionIdForDelete.value = positionIdList[i].value;
  textForDeleteModal.innerHTML = positionTitleList[i].value;
};

/* For position list view: Gets position ID to correctly displa upload applications pop-up, and to set position ID to associate the positions */
const assignApplicantUploadValues = function(i) {
  positionIdForUpload.value = positionIdList[i].value;
  textForUploadModal.innerHTML = positionApplicantUploadText[i].value;
};

/* Assign values to upload or delete modals based on the element clicked */
const initializeButtonListeners = function() {
  for (let i = 0; i < positionIdList.length; i++) {
    positionUploadButtons[i].addEventListener("click", assignApplicantUploadValues(i));
    positionDeleteButtons[i].addEventListener("click", assignDeleteValues(i));
  }
};

/* Initialize listeners on load */
window.addEventListener("load", initializeButtonListeners);
