"use strict";

/* Button user clicks to add another user to position */
var addUser = document.getElementById("add-users-button");

/* Div containing all users who can access a position */
var userDisplayLocation = document.getElementById("userDisplay");

/* Div containing information about the currently-logged in user */
var currentUser = document.getElementById("current-user");

/* Input for adding another user's e-mail address */
var userEmailField = document.getElementById("user-email-input");

/* Span containing error messages, if any */
var addUserMessagePrompt = document.getElementById("addUserMessagePrompt");

/* Id of the current position */
var positionId = userDisplayLocation.dataset.positionId;

/* Buttons to remove each user */
var removeUserButtons = document.getElementsByClassName("remove-user");

/* Add another user to position */
var addUserToPosition = function addUserToPosition() {
  var url = "/add_user_to_position?email=" + userEmailField.value + "&id=" + positionId;
  /* reset field input */
  userEmailField.value = "";

  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      if (data.exception) {
        addUserMessagePrompt.textContent = data.exception;
      } else {
        addUserMessagePrompt.textContent = "";

        /* create clone of element: simply setting x = y makes ashallow copy */
        var newUser = currentUser.cloneNode(true);

        /* change the relevant fields (id, text fields, add remove button) */
        newUser.id = data.userEmail;
        newUser.children[0].textContent = data.userEmail;
        newUser.children[0].classList.remove("grey-text");
        var removeButton = document.createElement("i");
        removeButton.classList.add("material-icons", "red-text", "remove-user");
        removeButton.textContent = "cancel";
        removeButton.dataset.userEmail = data.userEmail;

        removeButton.addEventListener("click", function () {
          removeUserFromPosition(removeButton.dataset.userEmail);
        });

        newUser.appendChild(removeButton);

        /* append the element to the end of the holder element */
        userDisplayLocation.appendChild(newUser);

        setRemoveButtonHandlers();
      }
    }).catch(function () {
      return console.error();
    });
  });
};

/* Remove a user's access to a position */
var removeUserFromPosition = function removeUserFromPosition(email) {
  console.log(email);
  console.log(positionId);
  var url = "/remove_user_from_position?email=" + email + "&id=" + positionId;
  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      /* retrieves the element and removes it from the holder element */
      var user = document.getElementById(data.userEmail);

      user.remove();
    }).catch(function () {
      return console.error();
    });
  });
};

/* Initialize listeners for buttons to remove users from a position */
var setRemoveButtonHandlers = function setRemoveButtonHandlers() {
  /* As remove buttons can be added/removed, need to continually redefine them. */
  removeUserButtons = document.getElementsByClassName("remove-user");

  var _loop = function _loop(i) {
    removeUserButtons[i].dataset.userEmail = removeUserButtons[i].parentNode.id;
    var email = removeUserButtons[i].dataset.userEmail;
    var removeButtonListener = function removeButtonListener() {
      removeUserFromPosition(email);
    };
    removeUserButtons[i].addEventListener("click", removeButtonListener);
  };

  for (var i = 0; i < removeUserButtons.length; i++) {
    _loop(i);
  }
};

/* Initializes button to add user to a position and remove button listeners */
window.addEventListener("DOMContentLoaded", function () {
  addUser.addEventListener("click", function () {
    if (userEmailField.reportValidity()) {
      addUserToPosition();
    }
  });
  setRemoveButtonHandlers();
});