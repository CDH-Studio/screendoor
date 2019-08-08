const showToast = function() {
  // Get the snackbar DIV
  const snackbar = document.getElementById("snackbar");
  
  // Add the "show" class to DIV
  snackbar.className = "show";
};

const closeToast = function() {
  // Get the snackbar DIV
  const snackbar = document.getElementById("snackbar");
    
  // Add the "show" class to DIV
  snackbar.className = "hide";
};

const checkForPageChanges = function() {
  const pageType = window.location.pathname;
  const url = "/change_notification?path=" + pageType;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      //If there is a message indicating a change
      if ((data.message == "change")) {
        //If the user is not the same as the user who made the changes
        if (document.getElementById("user-welcome").dataset.userEmail != data.lastEditedBy) {
          // Then show change notification toast
          showToast();
        }
      }
    }).catch(() => console.error());
  });
};

/* Show upload progress if there is a valid task ID */
window.addEventListener("DOMContentLoaded", () => {
  this.document.getElementById("close-notif-toast").addEventListener("click", () => {
    closeToast();
  });
  this.document.getElementById("user-change-toast-text").addEventListener("click", () => {
    location.reload();
  });
  setInterval(function() {
    checkForPageChanges();
  }, 7000); 
});