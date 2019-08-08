const addUser = document.getElementById("add-users-button");
const userDisplayLocation = document.getElementById("userDisplay");
const currentUser = document.getElementById("current-user");
const userEmailField = document.getElementById("user-email-input");
const addUserMessagePrompt = document.getElementById("addUserMessagePrompt");

const addUserToPosition = function(positionId) {
  const url = "/add_user_to_position?email=" + userEmailField.value +
        "&id=" + positionId;
  // reset field input
  userEmailField.value = "";

  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      if (data.exception != undefined) {
        addUserMessagePrompt.text = data.exception;
      } else {
        addUserMessagePrompt.text = "";
        // retrieve the default element to mimic (so new element isn"t built
        // from ground up
        const user = document.getElementById(data.userEmail);

        // create clone of element: simply setting x = y makes ashallow copy
        const newUser = currentUser.cloneNode(true);

        // change the relevant fields (id, text fields, add remove button)
        newUser.id = data.userEmail;
        newUser.innerHTML = '<p>' + data.userName + ' - ' +
          data.userEmail + '</p>';
        newUser.innerHTML += ('<i class="material-icons red-text ' +
                              'remove-user">cancel</i>');

        // append the element to the end of the holder element
        userDisplayLocation.appendChild(newUser);

        // re-init remove buttons
        setRemoveButtonHandlers(positionId);
      }
    }).catch(() => console.error());
  });
};

const removeUserFromPosition = function(email, positionId) {
  const url = "/remove_user_from_position?email=" + email + "&id=" + positionId;

  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      // retrieves the element and removes it from the holder element
      const user = document.getElementById(data.userEmail);

      userDisplayLocation.removeChild(user);

      // re-init remove buttons
      setRemoveButtonHandlers();
    }).catch(() => console.error());
  });
};

const setRemoveButtonHandlers = function(positionId) {
  // As remove buttons can be added/removed, need to continually redefine them.
  const removeUserButtons = document.getElementsByClassName("remove-user");
  for (let i = 0; i < removeUserButtons.length; i++) {
    removeUserButtons[i].addEventListener("click", () => {
      if (removeUserButtons[i] != undefined) {
        removeUserFromPosition(removeUserButtons[i].parentNode.id, positionId);
      }
    });
  }
};

window.addEventListener("DOMContentLoaded", () => {
  // stores position id
  if (userDisplayLocation != undefined) {
    const positionId = userDisplayLocation.dataset.positionId;
    addUser.addEventListener("click", () => {
      addUserToPosition(positionId);
    });
    setRemoveButtonHandlers(positionId);
  }
});
