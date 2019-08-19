/* Button user clicks to add another user to position */
const addUser = document.getElementById("add-users-button");

/* Div containing all users who can access a position */
const userDisplayLocation = document.getElementById("userDisplay");

/* Div containing information about the currently-logged in user */
const currentUser = document.getElementById("current-user");

/* Input for adding another user's e-mail address */
const userEmailField = document.getElementById("user-email-input");

/* Span containing error messages, if any */
const addUserMessagePrompt = document.getElementById("addUserMessagePrompt");

/* Id of the current position */
const positionId = userDisplayLocation.dataset.positionId;

/* Buttons to remove each user */
let removeUserButtons = document.getElementsByClassName("remove-user");

/* Add another user to position */
const addUserToPosition = function() {
  const url = "/add_user_to_position?email=" + userEmailField.value +
        "&id=" + positionId;
  /* reset field input */
  userEmailField.value = "";

  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      if (data.exception) {
        addUserMessagePrompt.textContent = data.exception;
      } else {
        addUserMessagePrompt.textContent = "";

        /* create clone of element: simply setting x = y makes ashallow copy */
        const newUser = currentUser.cloneNode(true);

        /* change the relevant fields (id, text fields, add remove button) */
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

        /* append the element to the end of the holder element */
        userDisplayLocation.appendChild(newUser);

        setRemoveButtonHandlers();
      }
    }).catch(() => console.error());
  });
};

/* Remove a user's access to a position */
const removeUserFromPosition = function(email) {
  console.log(email);
  console.log(positionId);
  const url = "/remove_user_from_position?email=" + email + "&id=" + positionId;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      /* retrieves the element and removes it from the holder element */
      const user = document.getElementById(data.userEmail);

      user.remove();

    }).catch(() => console.error());
  });
};

/* Initialize listeners for buttons to remove users from a position */
const setRemoveButtonHandlers = function() {
  /* As remove buttons can be added/removed, need to continually redefine them. */
  removeUserButtons = document.getElementsByClassName("remove-user");
  for (let i = 0; i < removeUserButtons.length; i++) {
    removeUserButtons[i].dataset.userEmail = removeUserButtons[i].parentNode.id;
    const email = removeUserButtons[i].dataset.userEmail;
    const removeButtonListener = () => {
      removeUserFromPosition(email);
    };
    removeUserButtons[i].addEventListener("click", removeButtonListener);
  }
};

/* Initializes button to add user to a position and remove button listeners */
window.addEventListener("DOMContentLoaded", () => {
  addUser.addEventListener("click", () => {
    if (userEmailField.reportValidity()) {
      addUserToPosition();
    }
  });
  setRemoveButtonHandlers();
});
