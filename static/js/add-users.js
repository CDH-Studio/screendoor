"use strict";

var addUser = document.getElementById("add-users-button");
var userDisplayLocation = document.getElementById("userDisplay");
var currentUser = document.getElementById("current-user");
var userEmailField = document.getElementById("user-email-input");
var addUserMessagePrompt = document.getElementById("addUserMessagePrompt");

var addUserToPosition = function addUserToPosition(positionId) {
  var url = "/add_user_to_position?email=" + userEmailField.value + "&id=" + positionId;
  // reset field input
  userEmailField.value = "";

  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      console.log(data);
      if (data.exception != undefined) {
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
        newUser.appendChild(removeButton);

        // append the element to the end of the holder element
        userDisplayLocation.appendChild(newUser);

        // re-init remove buttons
        setRemoveButtonHandlers(positionId);
      }
    }).catch(function () {
      return console.error();
    });
  });
};

var removeUserFromPosition = function removeUserFromPosition(email, positionId) {
  var url = "/remove_user_from_position?email=" + email + "&id=" + positionId;
  console.log(email);
  console.log(positionId);
  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      // retrieves the element and removes it from the holder element
      var user = document.getElementById(data.userEmail);
      userDisplayLocation.removeChild(user);

      // re-init remove buttons
      setRemoveButtonHandlers(positionId);
    }).catch(function () {
      return console.error();
    });
  });
};

var setRemoveButtonHandlers = function setRemoveButtonHandlers(positionId) {
  // As remove buttons can be added/removed, need to continually redefine them.
  var removeUserButtons = document.getElementsByClassName("remove-user");

  var _loop = function _loop(i) {
    removeUserButtons[i].addEventListener("click", function () {
      if (removeUserButtons[i] != undefined) {
        removeUserFromPosition(removeUserButtons[i].parentNode.id, positionId);
      }
    });
  };

  for (var i = 0; i < removeUserButtons.length; i++) {
    _loop(i);
  }
};

window.addEventListener("DOMContentLoaded", function () {
  // stores position id
  if (userDisplayLocation != undefined) {
    var positionId = userDisplayLocation.dataset.positionId;
    addUser.addEventListener("click", function () {
      addUserToPosition(positionId);
    });
    setRemoveButtonHandlers(positionId);
  }
});