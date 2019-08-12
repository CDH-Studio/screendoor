const addUser = document.getElementById("add-users-button");
const userDisplayLocation = document.getElementById("userDisplay");
const currentUser = document.getElementById("current-user");
const userEmailField = document.getElementById("user-email-input");
const addUserMessagePrompt = document.getElementById("addUserMessagePrompt");
let removeUserListeners = [];

const addUserToPosition = function(positionId) {
  const url = "/add_user_to_position?email=" + userEmailField.value +
        "&id=" + positionId;
  // reset field input
  userEmailField.value = "";

  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      if (data.exception) {
        addUserMessagePrompt.textContent = data.exception;
      } else {
        addUserMessagePrompt.textContent = "";

        // create clone of element: simply setting x = y makes ashallow copy
        const newUser = currentUser.cloneNode(true);

        // change the relevant fields (id, text fields, add remove button)
        newUser.id = data.userEmail;
        newUser.children[0].textContent = data.userEmail;
        newUser.children[0].classList.remove("grey-text");
        const removeButton = document.createElement("i");
        removeButton.classList.add("material-icons", "red-text", "remove-user");
        removeButton.textContent = "cancel";
        removeButton.addEventListener("click", () => {
          removeUserFromPosition(data.userEmail, positionId);
        });
        newUser.appendChild(removeButton);

        // append the element to the end of the holder element
        userDisplayLocation.appendChild(newUser);

        // re-init remove buttons
        removeRemoveButtonHandlers();
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
      removeRemoveButtonHandlers();
      setRemoveButtonHandlers(positionId);
    }).catch(() => console.error());
  });
};

const setRemoveButtonHandlers = function(positionId) {
  removeUserListeners = [];
  // As remove buttons can be added/removed, need to continually redefine them.
  const removeUserButtons = document.getElementsByClassName("remove-user");
  for (let i = 0; i < removeUserButtons.length; i++) {
    const removeButtonListener = () => {
      removeUserFromPosition(removeUserButtons[i].parentNode.id, positionId);
    };
    removeUserButtons[i].addEventListener("click", removeButtonListener);
    removeUserListeners.push(removeButtonListener);
  }
};

const removeRemoveButtonHandlers = function() {
  const removeUserButtons = document.getElementsByClassName("remove-user");
  for (let i = 0; i < removeUserButtons.length; i++) {
    const removeButtonListener = removeUserListeners[i];
    removeUserButtons[i].removeEventListener("click", removeButtonListener);
  }
};

window.addEventListener("DOMContentLoaded", () => {
  // stores position id
  if (userDisplayLocation) {
    const positionId = userDisplayLocation.dataset.positionId;
    addUser.addEventListener("click", () => {
      addUserToPosition(positionId);
    });
    setRemoveButtonHandlers(positionId);
  }
});
