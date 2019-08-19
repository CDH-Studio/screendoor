"use strict";

/* Pop-up alert that page contents have changed */
var showToast = function showToast() {
  /* Get the snackbar div */
  var snackbar = document.getElementById("snackbar");

  /* Set the div class to "show" */
  snackbar.className = "show";
};

/* Close alert that page contents have changed */
var closeToast = function closeToast() {
  /* Get the snackbar div */
  var snackbar = document.getElementById("snackbar");

  /* Set the div class to "hide" */
  snackbar.className = "hide";
};

/* Poll to see if any of the page's values were changed externally. */
var checkForPageChanges = function checkForPageChanges() {
  var requestData = Object.create(null);
  requestData["pageType"] = window.location.pathname;
  if (document.getElementById("position-id")) {
    requestData["positionId"] = document.getElementById("position-id").value;
  }
  if (document.getElementById("applicant-id")) {
    requestData["applicantId"] = document.getElementById("applicant-id").value;
  }
  var url = "/change_notification";
  fetch(url, {
    method: "POST",
    body: JSON.stringify(requestData), // data can be `string` or {object}!
    headers: {
      "Content-Type": "application/json"
    }
  }).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (responseData) {
      /* If there is a message indicating a change */
      if (responseData.message == "change") {
        /* If the user is not the same as the user who made the changes */
        if (document.getElementById("user-welcome").dataset.userEmail != responseData.lastEditedBy) {
          /* Then show change notification toast */
          showToast();
        }
      }
    }).catch(function () {
      return console.error();
    });
  });
};

/* Show upload progress if there is a valid task ID */
window.addEventListener("DOMContentLoaded", function () {
  var closeNotifToast = document.getElementById("close-notif-toast");
  closeNotifToast.addEventListener("click", function () {
    closeToast();
  });
  var userChangeToastText = document.getElementById("user-change-toast-text");
  userChangeToastText.addEventListener("click", function () {
    location.reload();
  });
  setInterval(function () {
    checkForPageChanges();
  }, 7000);
});