/* CONSTANTS AND VARIABLES */
const favourites = document.getElementsByClassName("favourite-icon");
const addUser = document.getElementById("add-users-button");
const userDisplayLocation = document.getElementById("userDisplay");
const currentUser = document.getElementById("current-user");
const userEmailField = document.getElementById("user-email-input");
const addUserMessagePrompt = document.getElementById("addUserMessagePrompt");

const unfavourite = function(i, id) {
  console.log(id);
};

const favourite = function(i, id) {
  url = "/add_to_favourites?app_id=" + id + "&favouriteStatus=" + document.getElementById(id).dataset.favouriteStatus;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      element = document.getElementById(id); // the outer span surrounding the icon
      if (data.favourite_status == "True") {
        element.children[0].innerText = 'star_border';
        element.setAttribute("data-favourite-status", "False");
      } else {
        element.children[0].innerText = 'star';
        element.setAttribute("data-favourite-status", "True");
      }
    }).catch(error => console.error());
  });
};


const setDefaultFavouriteStatus = function(element) {
  const favouriteStatus = element.dataset.favouriteStatus;
  if (favouriteStatus == "False") {
    element.children[0].innerText = 'star_border';
  } else {
    element.children[0].innerText = 'star';
  }
};


const add_user_to_position = function(position_id) {
    url = "/add_user_to_position?email=" + userEmailField.value + "&id=" + position_id
    // reset field input

    userEmailField.value = ""
    fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
        if (data.exception != undefined) {
            addUserMessagePrompt.text = data.exception
        } else {
            addUserMessagePrompt.text = ""
            // retrieve the default element to mimic (so new element isn't built
            // from ground up
            user = document.getElementById(data.userEmail)

            // create clone of element: simply setting x = y will make a shallow copy
            newUser = currentUser.cloneNode(true)

            // change the relevant fields (id, text fields, add remove button)
            newUser.id = data.userEmail
            newUser.innerHTML = '<p>' + data.userName + ' - ' + data.userEmail + '</p>'
            newUser.innerHTML += ('<i class="material-icons red-text remove-user">cancel</i>')

            // append the element to the end of the holder element
            userDisplayLocation.appendChild(newUser)

            //re-init remove buttons
            set_remove_button_handlers(position_id)
        }
    }).catch(error => console.error());
  });
};


const remove_user_from_position = function(email, position_id) {
    url = "/remove_user_from_position?email=" + email + "&id=" + position_id

    fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
        //retrieves the element and removes it from the holder element
        user = document.getElementById(data.userEmail)

        userDisplayLocation.removeChild(user)

        //re-init remove buttons
        set_remove_button_handlers()
    }).catch(error => console.error());
  });
};


const set_remove_button_handlers = function(position_id) {
    // As remove buttons can be added/removed freely, need to redefine them every time.
    removeUserButtons = document.getElementsByClassName("remove-user");
    for (let i = 0; i < removeUserButtons.length; i++) {
        removeUserButtons[i].addEventListener("click", () => {
            if (removeUserButtons[i] != undefined) {
                remove_user_from_position(removeUserButtons[i].parentNode.id, position_id);
            }
        });
    }
};

window.addEventListener('DOMContentLoaded', (event) => {
  // stores position id
  if (userDisplayLocation != undefined) {
    position_id = userDisplayLocation.dataset.positionId
    addUser.addEventListener("click", () => {
      add_user_to_position(position_id);
    });
    set_remove_button_handlers(position_id)
  }

  for (let i = 0; i < favourites.length; i++) {
    setDefaultFavouriteStatus(favourites[i]);
    favourites[i].addEventListener("click", () => {
      favourite(i, favourites[i].id);
    });
  }

});
