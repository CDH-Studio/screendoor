"use strict";

var addUser = document.getElementById("add-users-button");
var userDisplayLocation = document.getElementById("userDisplay");
var currentUser = document.getElementById("current-user");
var userEmailField = document.getElementById("user-email-input");
var addUserMessagePrompt = document.getElementById("addUserMessagePrompt");
var removeUserListeners = [];

var addUserToPosition = function addUserToPosition(positionId) {
  var url = "/add_user_to_position?email=" + userEmailField.value + "&id=" + positionId;
  // reset field input
  userEmailField.value = "";

  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      console.log(data);
      if (data.exception) {
        addUserMessagePrompt.textContent = data.exception;
      } else {
        addUserMessagePrompt.textContent = "";

        // create clone of element: simply setting x = y makes ashallow copy
        var newUser = currentUser.cloneNode(true);

        // change the relevant fields (id, text fields, add remove button)
        newUser.id = data.userEmail;
        newUser.children[0].textContent = data.userEmail;
        newUser.children[0].classList.remove("grey-text");
        var removeButton = document.createElement("i");
        removeButton.classList.add("material-icons", "red-text", "remove-user");
        removeButton.textContent = "cancel";
        removeButton.addEventListener("click", function () {
          removeUserFromPosition(data.userEmail, positionId);
        });
        newUser.appendChild(removeButton);

        // append the element to the end of the holder element
        userDisplayLocation.appendChild(newUser);

        // re-init remove buttons
        removeRemoveButtonHandlers();
        setRemoveButtonHandlers(positionId);
      }
    }).catch(function () {
      return console.error();
    });
  });
};

var removeUserFromPosition = function removeUserFromPosition(email, positionId) {
  var url = "/remove_user_from_position?email=" + email + "&id=" + positionId;
  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      // retrieves the element and removes it from the holder element
      var user = document.getElementById(data.userEmail);
      userDisplayLocation.removeChild(user);

      // re-init remove buttons
      removeRemoveButtonHandlers();
      setRemoveButtonHandlers(positionId);
    }).catch(function () {
      return console.error();
    });
  });
};

var setRemoveButtonHandlers = function setRemoveButtonHandlers(positionId) {
  removeUserListeners = [];
  // As remove buttons can be added/removed, need to continually redefine them.
  var removeUserButtons = document.getElementsByClassName("remove-user");

  var _loop = function _loop(i) {
    var removeButtonListener = function removeButtonListener() {
      removeUserFromPosition(removeUserButtons[i].parentNode.id, positionId);
    };
    removeUserButtons[i].addEventListener("click", removeButtonListener);
    removeUserListeners.push(removeButtonListener);
  };

  for (var i = 0; i < removeUserButtons.length; i++) {
    _loop(i);
  }
};

var removeRemoveButtonHandlers = function removeRemoveButtonHandlers() {
  var removeUserButtons = document.getElementsByClassName("remove-user");
  for (var i = 0; i < removeUserButtons.length; i++) {
    var removeButtonListener = removeUserListeners[i];
    removeUserButtons[i].removeEventListener("click", removeButtonListener);
  }
};

window.addEventListener("DOMContentLoaded", function () {
  // stores position id
  if (userDisplayLocation) {
    var positionId = userDisplayLocation.dataset.positionId;
    addUser.addEventListener("click", function () {
      addUserToPosition(positionId);
    });
    setRemoveButtonHandlers(positionId);
  }
});
