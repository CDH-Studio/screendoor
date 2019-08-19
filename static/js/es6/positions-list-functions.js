/* Hidden inputs containing position ID values */
const positionIdList = document.getElementsByClassName("position-id-list");

/* Hidden inputs with text for applicant upload modals */
const positionApplicantUploadText = document.getElementsByClassName("position-applicant-text");

/* Hidden inputs with position titles */
const positionTitleList = document.getElementsByClassName("position-title-list");

/* a elements triggering delete modals for each position */
const positionDeleteButtons = document.getElementsByClassName("delete-button");

/* a elements triggering upload application modals for each position */
const positionUploadButtons = document.getElementsByClassName("upload-applicants-button");

/* Hidden input the value of which set later */
const positionIdForUpload = document.getElementById("upload-applications-id");

/* Hidden input the value of which set later */
const positionIdForDelete = document.getElementById("delete-confirm-id");

/* h6 element the textContent of which is set later */
const textForDeleteModal = document.getElementById("delete-text");
const textForUploadModal = document.getElementById("upload-applications-text");

/* Assign values to upload or delete modals based on the element clicked */
const initializeButtonListeners = function() {
  for (let i = 0; i < positionIdList.length; i++) {
    /* For position list view: Gets position ID to correctly display delete confirmation message, and to set position ID in the delete form */
    positionUploadButtons[i].addEventListener("click", function() {
      positionIdForUpload.value = positionIdList[i].value;
      textForUploadModal.textContent = positionApplicantUploadText[i].value;
    });
    /* For position list view: Gets position ID to correctly display upload applications pop-up, and to set position ID to associate the positions */
    positionDeleteButtons[i].addEventListener("click", function() {
      positionIdForDelete.value = positionIdList[i].value;
      textForDeleteModal.textContent = positionTitleList[i].value;
    });
  }
};

/* Initialize listeners on load */
window.addEventListener("load", initializeButtonListeners);
