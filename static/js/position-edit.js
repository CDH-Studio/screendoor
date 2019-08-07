"use strict";

/* CONSTANTS AND VARIABLES */

var card = document.getElementById("position-card");
var editButton = document.getElementById("edit-button");
var saveButton = document.getElementById("save-button");
var okButton = document.getElementById("edit-button") ? editButton.cloneNode() : null;
var cancelButton = document.getElementById("save-button") ? saveButton.cloneNode() : null;
var form = document.getElementById("edit-position");
var requirementTypeHeaders = document.getElementsByClassName("requirement-type");
var cells = Array.from(document.getElementsByClassName("edit"));
var requirementPoints = document.getElementsByClassName("requirement-point");
var educationRequirementDiv = document.getElementById("education-requirements");
var experienceRequirementDiv = document.getElementById("experience-requirements");
var assetRequirementDiv = document.getElementById("asset-requirements");
var resetEducation = educationRequirementDiv ? educationRequirementDiv.cloneNode(true) : null;
var resetExperience = experienceRequirementDiv ? experienceRequirementDiv.cloneNode(true) : null;
var resetAsset = assetRequirementDiv ? assetRequirementDiv.cloneNode(true) : null;
var buttonRow = document.getElementById("import-position-buttons");
var cellText = [];

var getEditData = function getEditData() {
  var params = Object.create(null);
  params["positionId"] = document.getElementById("position-id").value;
  cells.forEach(function (cell) {
    params[cell.id] = cell.textContent;
  });
  return params;
};

/* Sends data from edited cells via AJAX POST request */
var editPosition = function editPosition() {
  var url = "/edit-position";
  var data = JSON.stringify(getEditData());

  fetch(url, {
    method: "POST", // or "PUT"
    body: data, // data can be `string` or {object}!
    headers: {
      "Content-Type": "application/json"
    }
  }).catch(function (error) {
    return console.error("Error:", error);
  });
};

/* Rearrange requirement abbreviations (i.e. EXP1) to ensure order is maintained */
var rearrangeAbbreviations = function rearrangeAbbreviations() {
  var educationRequirements = document.querySelectorAll("div[data-requirement-type='Education']");
  var experienceRequirements = document.querySelectorAll("div[data-requirement-type='Experience']");
  var assetRequirements = document.querySelectorAll("div[data-requirement-type='Asset']");

  for (var i = 0; i < educationRequirements.length; i++) {
    educationRequirements[i].children[1].textContent = "ED" + (i + 1);
  }
  for (var _i = 0; _i < experienceRequirements.length; _i++) {
    experienceRequirements[_i].children[1].textContent = "EXP" + (_i + 1);
  }
  for (var _i2 = 0; _i2 < assetRequirements.length; _i2++) {
    assetRequirements[_i2].children[1].textContent = "AEXP" + (_i2 + 1);
  }
};

/* Ensure consistency in the IDs of requirement delete buttons */
var reinitializeDeleteButtonIds = function reinitializeDeleteButtonIds() {
  requirementPoints = document.getElementsByClassName("requirement-point");
  var removeButtons = document.getElementsByClassName("remove-requirement-button");
  for (var i = 0; i < requirementPoints.length; i++) {
    removeButtons[i].id = "remove-button-" + i;
  }
};

/* Reinitialize data for requirement point divs */
var reinitializeRequirementPointData = function reinitializeRequirementPointData() {
  for (var i = 0; i < requirementPoints.length; i++) {
    var abbreviation = requirementPoints[i].children[1].textContent;
    requirementPoints[i].dataset.requirementAbbrev = abbreviation;
    requirementPoints[i].dataset.requirementId = i;
    requirementPoints[i].children[0].dataset.requirementAbbrev = abbreviation;
    requirementPoints[i].children[0].dataset.requirementId = i;
  }
};

/* Reinitialize IDs of cells to ensure consistency after changes made */
var reinitializeRequirementIds = function reinitializeRequirementIds() {
  // LAST
  requirementPoints = document.getElementsByClassName("requirement-point");
  var requirementCells = document.getElementsByClassName("edit requirement-description");
  for (var i = 0; i < requirementCells.length; i++) {
    var abbreviation = requirementPoints[i].dataset.requirementAbbrev;
    var requirementNumber = parseInt(abbreviation.match(/\d+/g).map(Number));
    var requirementType = requirementPoints[i].dataset.requirementType;
    requirementCells[i].id = requirementType.toLowerCase() + "-" + requirementNumber.toString();
    if (requirementCells[i].children[0]) {
      requirementCells[i].children[0].name = requirementCells[i].id;
    }
  }
  cells = Array.from(document.getElementsByClassName("edit"));
};

/* Remove a requirement and reinitialize abbreviations and IDs */
var removeRequirement = function removeRequirement(requirementId) {
  for (var i = 0; i < requirementPoints.length; i++) {
    if (requirementPoints[i].dataset.requirementId == requirementId) {
      requirementPoints[i].remove();
    }
  }
  requirementPoints = document.getElementsByClassName("requirement-point");
  rearrangeAbbreviations();
  reinitializeDeleteButtonIds();
  reinitializeRequirementPointData();
  reinitializeRequirementIds();
};

/* Return a new blank requirement item */
var newRequirement = function newRequirement(requirementType) {
  var newNode = document.createElement("div");
  newNode.classList.add("requirement-point", "row");
  newNode.dataset.requirementType = requirementType;
  newNode.appendChild(removeRequirementButton());
  var abbrevDiv = document.createElement("div");
  abbrevDiv.classList.add("requirement-abbrev", "col");
  newNode.appendChild(abbrevDiv);
  var descripDiv = document.createElement("div");
  descripDiv.classList.add("requirement-description", "col", "s11", "edit");
  descripDiv.appendChild(createReturnTextInput("", "placeholder", false));
  switch (requirementType) {
    case "Education":
      descripDiv.classList.add("education-description");
      break;
    case "Experience":
      descripDiv.classList.add("experience-description");
      break;
    case "Asset":
      descripDiv.classList.add("asset-description");
      break;
  }
  newNode.appendChild(descripDiv);
  return newNode;
};

/* Add a requirement based on its type and reinitialize IDs to ensure consistency */
var addRequirement = function addRequirement(requirementType) {
  var newNode = newRequirement(requirementType);
  switch (requirementType) {
    case "Education":
      educationRequirementDiv.appendChild(newNode);
      break;
    case "Experience":
      experienceRequirementDiv.appendChild(newNode);
      break;
    case "Asset":
      assetRequirementDiv.appendChild(newNode);
      break;
  }
  rearrangeAbbreviations();
  reinitializeDeleteButtonIds();
  reinitializeRequirementPointData();
  reinitializeRequirementIds();

  newNode.children[0].addEventListener("click", function () {
    removeRequirement(newNode.dataset.requirementId);
  });
};

/* Returns a button used to remove a requirement */
var removeRequirementButton = function removeRequirementButton(i) {
  var removeButton = document.createElement("i");
  removeButton.classList.add("material-icons", "col", "red-text", "remove-requirement-button", "left");
  removeButton.textContent = "remove_circle";
  removeButton.id = "remove-button-" + i;
  return removeButton;
};

/* Returns a button used to add a requirement */
var addRequirementButton = function addRequirementButton(i) {
  var addButton = document.createElement("i");
  addButton.classList.add("material-icons", "orange-text", "add-requirement-button");
  addButton.textContent = "add_circle";
  addButton.id = "add-button-" + i;
  return addButton;
};

/* Adds buttons to requirement headers allowing the user to click to add requirements */
var addButtonsToRequirementHeaders = function addButtonsToRequirementHeaders() {
  var _loop = function _loop(i) {
    var requirementButton = addRequirementButton(i);
    requirementButton.dataset.requirementType = requirementTypeHeaders[i].dataset.requirementType;
    requirementButton.addEventListener("click", function () {
      addRequirement(requirementButton.dataset.requirementType);
    });
    requirementTypeHeaders[i].appendChild(requirementButton);
  };

  for (var i = 0; i < requirementTypeHeaders.length; i++) {
    _loop(i);
  }
};

/* Removes buttons from requirement headers */
var removeButtonsFromRequirementHeaders = function removeButtonsFromRequirementHeaders() {
  for (var i = 0; i < requirementTypeHeaders.length; i++) {
    requirementTypeHeaders[i].removeChild(document.getElementById("add-button-" + i));
  }
};

/* Adds buttons to requirement items allowing user to delete them */
var addButtonsToRequirements = function addButtonsToRequirements() {
  var _loop2 = function _loop2(i) {
    var removeButton = removeRequirementButton(i);
    removeButton.dataset.requirementType = requirementPoints[i].dataset.requirementType;
    removeButton.dataset.requirementAbbrev = requirementPoints[i].dataset.requirementAbbrev;
    removeButton.dataset.requirementId = requirementPoints[i].dataset.requirementId;
    removeButton.addEventListener("click", function () {
      removeRequirement(removeButton.dataset.requirementId);
    });
    requirementPoints[i].prepend(removeButton);
  };

  for (var i = 0; i < requirementPoints.length; i++) {
    _loop2(i);
  }
};

/* Removes delete buttons from requirement items */
var removeButtonsFromRequirements = function removeButtonsFromRequirements() {
  requirementPoints = document.getElementsByClassName("requirement-point");
  for (var i = 0; i < requirementPoints.length; i++) {
    try {
      if (document.getElementById("remove-button-" + i)) {
        requirementPoints[i].removeChild(document.getElementById("remove-button-" + i));
      }
    } catch (NotFoundError) {
      console.error();
    }
  }
};

/* Adds all necessary buttons for adding and removing requirements */
var addReqButtons = function addReqButtons() {
  addButtonsToRequirements();
  addButtonsToRequirementHeaders();
};

/* Removes all requirement-related buttons */
var removeReqButtons = function removeReqButtons() {
  removeButtonsFromRequirements();
  removeButtonsFromRequirementHeaders();
};

/* Appends edit cells containing existing position data */
var defineEditCells = function defineEditCells(cell, name, isReadOnly) {
  var input = createReturnTextInput(cell.textContent, name, isReadOnly);
  cell.textContent = null;
  cell.appendChild(input);
};

/* Returns an edit cell with the name and value of the table data element */
var createReturnTextInput = function createReturnTextInput(text, name, isReadOnly) {
  var editableNode = document.createElement("input");
  editableNode.readOnly = isReadOnly;
  editableNode.name = name;
  editableNode.className = "editing";
  if (name == "position-date-closed" && !isIE()) {
    editableNode.type = "date";
  } else {
    editableNode.type = "text";
  }
  editableNode.value = text.trim();
  editableNode.setAttribute("required", "");
  return editableNode;
};

/* Create confirm and cancel buttons for editing */
var defineAdditionalButtons = function defineAdditionalButtons() {
  window.location.pathname.includes("/createnewposition") ? okButton.value = document.getElementById("ok-button-text").value : okButton.textContent = document.getElementById("ok-button-text").value;
  okButton.id = "ok-button";
  okButton.name = "save-edits";
  okButton.type = "button";
  okButton.classList.add("hide");
  window.location.pathname.includes("/createnewposition") ? cancelButton.value = document.getElementById("cancel-button-text").value : cancelButton.textContent = document.getElementById("cancel-button-text").value;
  cancelButton.id = "cancel-button";
  cancelButton.name = "cancel-edits";
  cancelButton.type = "button";
  cancelButton.classList.add("hide");
  buttonRow.append(okButton, cancelButton);
};

/* Adjust card size based on browser window width */
var setCardSize = function setCardSize() {
  var percentage = 0;
  if (window.location.pathname.includes("/createnewposition")) {
    percentage = sidebarIsOpen ? 50 : 70; // from sd-sidenav.js
  } else {
    percentage = sidebarIsOpen ? 70 : 88; // from sd-sidenav.js
  }
  fixPaddingWidth(); // from sd-sidenav.js
  var width = window.innerWidth < 1800 ? parseInt(window.innerWidth * percentage / 100).toString().concat("px") : 1250;
  card.style.setProperty("max-width", width, "important");
  card.style.setProperty("width", width, "important");
  card.style.setProperty("min-width", "700px", "important");
};

var showRequirementTypeHeaders = function showRequirementTypeHeaders() {
  for (var i = 0; i < requirementTypeHeaders.length; i++) {
    requirementTypeHeaders[i].classList.remove("hide");
  }
};

var hideShowMissingRequirements = function hideShowMissingRequirements() {
  document.querySelectorAll("div[data-requirement-type='Education']").length == 0 ? requirementTypeHeaders[0].classList.add("hide") : requirementTypeHeaders[0].classList.remove("hide");
  document.querySelectorAll("div[data-requirement-type='Experience']").length == 0 ? requirementTypeHeaders[1].classList.add("hide") : requirementTypeHeaders[1].classList.remove("hide");
  document.querySelectorAll("div[data-requirement-type='Asset']").length == 0 ? requirementTypeHeaders[2].classList.add("hide") : requirementTypeHeaders[2].classList.remove("hide");
};

/* Convert text fields into editable inputs */
var startEditing = function startEditing() {
  removeRequirementListeners(); // From position-tables.js
  expandAllRequirements(); // From position-tables.js
  showRequirementTypeHeaders();
  reinitializeRequirementIds();
  setCardSize();
  window.addEventListener("resize", setCardSize);
  document.getElementById("base-header").addEventListener("transitionend", setCardSize);
  showElements(okButton, cancelButton); // From helper-functions.js
  hideElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null); // From helper-functions.js

  cells.forEach(function (cell, i) {
    cellText[i] = cells[i].textContent;
    cell.classList.contains("readonly") ? defineEditCells(cell, cell.id, true) : defineEditCells(cell, cell.id, false);
  });
  addReqButtons();
};

/* Tasks associated with stopping edit, either via cancel or confirm */
var stopEditing = function stopEditing() {
  addRequirementListeners(); // From position-tables.js
  hideShowMissingRequirements();
  showElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null); // From helper-functions.js
  hideElements(okButton, cancelButton); // From helper-functions.js
  card.style.setProperty("max-width", "auto", "important");
  card.style.setProperty("min-width", "700px", "important");
  removeReqButtons();
};

/* Confirm changes to position and send data via AJAX */
var confirmEditChanges = function confirmEditChanges() {
  if (form.reportValidity()) {
    stopEditing();
    cells.forEach(function (cell) {
      cell.textContent = cell.lastChild.value != null ? cell.lastChild.value : cell.value;
    });
    editPosition();
  }
};

/* Cancel edits and return position to original imported state */
var cancelEditChanges = function cancelEditChanges() {
  if (educationRequirementDiv) {
    educationRequirementDiv.replaceWith(resetEducation);
    educationRequirementDiv = document.getElementById("education-requirements");
    educationRequirementDiv.classList.remove("row-closed");
  }
  if (experienceRequirementDiv) {
    experienceRequirementDiv.replaceWith(resetExperience);
    experienceRequirementDiv = document.getElementById("experience-requirements");
    experienceRequirementDiv.classList.remove("row-closed");
  }
  if (assetRequirementDiv) {
    assetRequirementDiv.replaceWith(resetAsset);
    assetRequirementDiv = document.getElementById("asset-requirements");
    assetRequirementDiv.classList.remove("row-closed");
  }
  cells.forEach(function (cell, i) {
    cell.textContent = cellText[i];
  });
  cells = Array.from(document.getElementsByClassName("edit"));
  stopEditing();
};

/* LISTENERS */
window.addEventListener("DOMContentLoaded", function () {
  /* Defines additional buttons that do not appear on page load */
  if (document.getElementById("edit-button")) {
    defineAdditionalButtons();
    /* User presses the edit button to change position information */
    editButton.addEventListener("click", startEditing);
    /* User presses the OK button to confirm editing changes */
    okButton.addEventListener("click", confirmEditChanges);

    /* User presses the cancel button to cancel editing changes and revert to original */
    cancelButton.addEventListener("click", cancelEditChanges);

    hideShowMissingRequirements();
  }
});