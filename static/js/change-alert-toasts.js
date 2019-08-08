"use strict";

var showToast = function showToast() {
  // Get the snackbar DIV
  var snackbar = document.getElementById("snackbar");

  // Add the "show" class to DIV
  snackbar.className = "show";
};

var closeToast = function closeToast() {
  // Get the snackbar DIV
  var snackbar = document.getElementById("snackbar");

  // Add the "show" class to DIV
  snackbar.className = "hide";
};

var checkForPageChanges = function checkForPageChanges() {
  var pageType = window.location.pathname;
  var url = "/change_notification?path=" + pageType;
  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      //If there is a message indicating a change
      if (data.message == "change") {
        //If the user is not the same as the user who made the changes
        if (document.getElementById("user-welcome").dataset.userEmail != data.lastEditedBy) {
          // Then show change notification toast
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
  undefined.document.getElementById("close-notif-toast").addEventListener("click", function () {
    closeToast();
  });
  undefined.document.getElementById("user-change-toast-text").addEventListener("click", function () {
    location.reload();
  });
  setInterval(function () {
    checkForPageChanges();
  }, 7000);
});