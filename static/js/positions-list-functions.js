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

/* Assign values to upload or delete modals based on the element clicked */
const initializeButtonListeners = function() {
  for (let i = 0; i < positionIdList.length; i++) {
    /* For position list view: Gets position ID to correctly display delete confirmation message, and to set position ID in the delete form */
    positionUploadButtons[i].addEventListener("click", function() {
      positionIdForUpload.value = positionIdList[i].value;
      textForUploadModal.innerHTML = positionApplicantUploadText[i].value;
    });
    /* For position list view: Gets position ID to correctly display upload applications pop-up, and to set position ID to associate the positions */
    positionDeleteButtons[i].addEventListener("click", function() {
      positionIdForDelete.value = positionIdList[i].value;
      textForDeleteModal.innerHTML = positionTitleList[i].value;
    });
  }
};

/* Initialize listeners on load */
window.addEventListener("load", initializeButtonListeners);
