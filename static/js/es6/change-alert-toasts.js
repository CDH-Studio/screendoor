/* Pop-up alert that page contents have changed */
const showToast = function() {
  /* Get the snackbar div */
  const snackbar = document.getElementById("snackbar");

  /* Set the div class to "show" */
  snackbar.className = "show";
};

/* Close alert that page contents have changed */
const closeToast = function() {
  /* Get the snackbar div */
  const snackbar = document.getElementById("snackbar");

  /* Set the div class to "hide" */
  snackbar.className = "hide";
};

/* Poll to see if any of the page's values were changed externally. */
const checkForPageChanges = function() {
  const data = Object.create(null);
  data["pageType"] = window.location.pathname;
  if (document.getElementById("position-id")) {
    data["positionId"] = document.getElementById("position-id").value;
  }
  if (document.getElementById("applicant-id")) {
    data["applicantId"] = document.getElementById("applicant-id").value;
  }
  const url = "/change_notification";
  fetch(url, {
    method: "POST",
    body: JSON.stringify(data), // data can be `string` or {object}!
    headers:{
      "Content-Type": "application/json"
    }
  }).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      /* If there is a message indicating a change */
      if ((data.message == "change")) {
        /* If the user is not the same as the user who made the changes */
        if (document.getElementById("user-welcome").dataset.userEmail != data.lastEditedBy) {
          /* Then show change notification toast */
          showToast();
        }
      }
    }).catch(() => console.error());
  });
};

/* Show upload progress if there is a valid task ID */
window.addEventListener("DOMContentLoaded", () => {
  const closeNotifToast = document.getElementById("close-notif-toast");
  closeNotifToast.addEventListener("click", () => {
    closeToast();
  });
  const userChangeToastText = document.getElementById("user-change-toast-text");
  userChangeToastText.addEventListener("click", () => {
    location.reload();
  });
  setInterval(function() {
    checkForPageChanges();
  }, 7000);
});
