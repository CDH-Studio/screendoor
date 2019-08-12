const addUser = document.getElementById("add-users-button");
const userDisplayLocation = document.getElementById("userDisplay");
const currentUser = document.getElementById("current-user");
const userEmailField = document.getElementById("user-email-input");
const addUserMessagePrompt = document.getElementById("addUserMessagePrompt");
const positionId = userDisplayLocation.dataset.positionId;
let removeUserButtons = document.getElementsByClassName("remove-user");
let removeUserListeners = [];

const addUserToPosition = function() {
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
        removeButton.dataset.userEmail = data.userEmail;

        removeButton.addEventListener("click", () => {
          removeUserFromPosition(removeButton.dataset.userEmail);
        });

        newUser.appendChild(removeButton);

        // append the element to the end of the holder element
        userDisplayLocation.appendChild(newUser);

        setRemoveButtonHandlers();
      }
    }).catch(() => console.error());
  });
};

const removeUserFromPosition = function(email) {
  console.log(email);
  console.log(positionId);
  const url = "/remove_user_from_position?email=" + email + "&id=" + positionId;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      // retrieves the element and removes it from the holder element
      const user = document.getElementById(data.userEmail);

      user.remove();

      // re-init remove buttons
    }).catch(() => console.error());
  });
};

const setRemoveButtonHandlers = function() {
  removeUserListeners = [];
  // As remove buttons can be added/removed, need to continually redefine them.
  removeUserButtons = document.getElementsByClassName("remove-user");
  for (let i = 0; i < removeUserButtons.length; i++) {
    removeUserButtons[i].dataset.userEmail = removeUserButtons[i].parentNode.id;
    const email = removeUserButtons[i].dataset.userEmail;
    const removeButtonListener = () => {
      removeUserFromPosition(email);
    };
    removeUserButtons[i].addEventListener("click", removeButtonListener);
    removeUserListeners.push(removeButtonListener);
  }
};

window.addEventListener("DOMContentLoaded", () => {
  addUser.addEventListener("click", () => {
    if (userEmailField.reportValidity()) {
      addUserToPosition();
    }
  });
  setRemoveButtonHandlers();
});
