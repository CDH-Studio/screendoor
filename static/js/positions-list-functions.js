"use strict";

/* Positions list specific constants */
var positionIdList = document.getElementsByClassName("position-id-list");
var positionReferenceList = document.getElementsByClassName("position-reference-list");
var positionApplicantUploadText = document.getElementsByClassName("position-applicant-text");
var positionTitleList = document.getElementsByClassName("position-title-list");
var positionDeleteButtons = document.getElementsByClassName("delete-button");
var positionUploadButtons = document.getElementsByClassName("upload-applicants-button");
var positionIdForUpload = document.getElementById("upload-applications-id");
var positionIdForDelete = document.getElementById("delete-confirm-id");
var textForDeleteModal = document.getElementById("delete-text");
var textForUploadModal = document.getElementById("upload-applications-text");

/* Assign values to upload or delete modals based on the element clicked */
var initializeButtonListeners = function initializeButtonListeners() {
  var _loop = function _loop(i) {
    /* For position list view: Gets position ID to correctly display delete confirmation message, and to set position ID in the delete form */
    positionUploadButtons[i].addEventListener("click", function () {
      positionIdForUpload.value = positionIdList[i].value;
      textForUploadModal.innerHTML = positionApplicantUploadText[i].value;
    });
    /* For position list view: Gets position ID to correctly display upload applications pop-up, and to set position ID to associate the positions */
    positionDeleteButtons[i].addEventListener("click", function () {
      positionIdForDelete.value = positionIdList[i].value;
      textForDeleteModal.innerHTML = positionTitleList[i].value;
    });
  };

  for (var i = 0; i < positionIdList.length; i++) {
    _loop(i);
  }
};

/* Initialize listeners on load */
window.addEventListener("load", initializeButtonListeners);