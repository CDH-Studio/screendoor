/* CONSTANTS AND VARIABLES */

const favouriteIcons = document.getElementsByClassName('favourite-icon');
const addUser = document.getElementById('add-users-button');
const userDisplayLocation = document.getElementById('userDisplay');
const currentUser = document.getElementById('current-user');
const userEmailField = document.getElementById('user-email-input');
const addUserMessagePrompt = document.getElementById('addUserMessagePrompt');

const requirementTypes = document.getElementsByClassName("requirement-type");
const hiddenRequirementSections = document.getElementsByClassName("hidden-requirement-info");
const expandRequirementButtons = document.getElementsByClassName("expand-requirement");
const expandAllRequirementsButton = document.getElementById("expand-collapse-criteria");

const changeFavouriteStatus = function(i, id) {
  url = '/change_favourites_status?app_id=' + id +
    '&favouriteStatus=' + document.getElementById(id).dataset.favouriteStatus;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      element = document.getElementById(id);
      if (data.favourite_status == 'True') {
        element.children[0].innerText = 'star_border';
        element.setAttribute('data-favourite-status', 'False');
      } else {
        element.children[0].innerText = 'star';
        element.setAttribute('data-favourite-status', 'True');
      }
    }).catch((error) => console.error());
  });
};


const setDefaultFavouriteStatus = function(element) {
  const favouriteStatus = element.dataset.favouriteStatus;
  if (favouriteStatus == 'False') {
    element.children[0].innerText = 'star_border';
  } else {
    element.children[0].innerText = 'star';
  }
};


const addUserToPosition = function(positionId) {
  const url = '/add_user_to_position?email=' + userEmailField.value +
    '&id=' + positionId;
  // reset field input
  userEmailField.value = '';

  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      if (data.exception != undefined) {
        addUserMessagePrompt.text = data.exception;
      } else {
        addUserMessagePrompt.text = '';
        // retrieve the default element to mimic (so new element isn't built
        // from ground up
        user = document.getElementById(data.userEmail);

        // create clone of element: simply setting x = y makes ashallow copy
        newUser = currentUser.cloneNode(true);

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
    }).catch((error) => console.error());
  });
};


const removeUserFromPosition = function(email, positionId) {
  url = '/remove_user_from_position?email=' + email + '&id=' + positionId;

  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      // retrieves the element and removes it from the holder element
      user = document.getElementById(data.userEmail);

      userDisplayLocation.removeChild(user);

      // re-init remove buttons
      setRemoveButtonHandlers();
    }).catch((error) => console.error());
  });
};


const setRemoveButtonHandlers = function(positionId) {
  // As remove buttons can be added/removed, need to continually redefine them.
  removeUserButtons = document.getElementsByClassName('remove-user');
  for (let i = 0; i < removeUserButtons.length; i++) {
    removeUserButtons[i].addEventListener('click', () => {
      if (removeUserButtons[i] != undefined) {
        removeUserFromPosition(removeUserButtons[i].parentNode.id, positionId);
      }
    });
  }
};

const expandCollapseAllRequirements = function(i) {
  if (expandAllRequirementsButton.innerText == "unfold_more") {
    expandAllRequirementsButton.innerText = "unfold_less"
    for (let i = 0; i < hiddenRequirementSections.length; i++) {
      expandRequirement(i);
    }
  } else {
    expandAllRequirementsButton.innerText = "unfold_more"
    for (let i = 0; i < hiddenRequirementSections.length; i++) {
      collapseRequirement(i);
    }
  }
};

const expandRequirement = function(i) {
  expandRequirementButtons[i].innerText = "expand_less";
  hiddenRequirementSections[i].classList.remove("row-closed");
  requirementTypes[i].classList.remove("hoverable");
};

const collapseRequirement = function(i) {
  expandRequirementButtons[i].innerText = "expand_more";
  hiddenRequirementSections[i].classList.add("row-closed");
  requirementTypes[i].classList.add("hoverable");
};

const expandCollapseRequirement = function(i) {
  hiddenRequirementSections[i].classList.contains("row-closed") ? expandRequirement(i) : collapseRequirement(i);
};

window.addEventListener('DOMContentLoaded', (event) => {
  // stores position id
  if (userDisplayLocation != undefined) {
    positionId = userDisplayLocation.dataset.positionId;
    addUser.addEventListener('click', () => {
      addUserToPosition(positionId);
    });
    setRemoveButtonHandlers(positionId);
  }

  for (let i = 0; i < favouriteIcons.length; i++) {
    setDefaultFavouriteStatus(favouriteIcons[i]);
    favouriteIcons[i].addEventListener('click', () => {
      changeFavouriteStatus(i, favouriteIcons[i].id);
    });
  }

  for (let i = 0; i < requirementTypes.length; i++) {
    requirementTypes[i].addEventListener("click", () =>{
      expandCollapseRequirement(i)
    });
  }

  expandAllRequirementsButton.addEventListener("click", () => {
    expandCollapseAllRequirements();
  });
});
