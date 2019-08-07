const showToast = function() {
  // Get the snackbar DIV
  var x = document.getElementById("snackbar");
  
  // Add the "show" class to DIV
  x.className = "show";

};

const closeToast = function() {
  // Get the snackbar DIV
  var x = document.getElementById("snackbar");
    
  // Add the "show" class to DIV
  x.className = "hide";
  
};

/* Show upload progress if there is a valid task ID */
window.addEventListener("load", function() {
  this.document.getElementById("close-notif-toast").addEventListener("click", () => {
    closeToast();
  });
  setInterval(function() {
    checkForPageChanges();
  }, 7000); 
});


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