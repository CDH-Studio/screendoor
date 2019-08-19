/* CONSTANTS AND VARIABLES */

/* "Card" div containing position */
const card = document.getElementById("position-card");

/* Button user clicks to begin editing position */
const editButton = document.getElementById("edit-button");

/* Button user clicks to save position during upload */
const saveButton = document.getElementById("save-button");

/* Button user clicks to confirm changes during edit  */
const okButton = document.getElementById("edit-button") ? editButton.cloneNode() : null;

/* Button user clicks to discard changes during edit */
const cancelButton = document.getElementById("save-button") ? saveButton.cloneNode() : null;

/* Form element surrounding position edit fields  */
const form = document.getElementById("edit-position");

/* li elements for each category of position requirement  */
const requirementTypeHeaders = document.getElementsByClassName("requirement-type");

/* Array comprised of divs holding editable text */
let cells = Array.from(document.getElementsByClassName("edit"));

/* Divs containing individual requirements  */
let requirementPoints = document.getElementsByClassName("requirement-point");

/* Div containing all education requirements */
let educationRequirementDiv = document.getElementById("education-requirements");

/* Div containing all experience requirements */
let experienceRequirementDiv = document.getElementById("experience-requirements");

/* Div containing all asset requirements */
let assetRequirementDiv = document.getElementById("asset-requirements");

/* Persisted education, experience, and asset rows to restore if user cancels editing */
let resetEducation = educationRequirementDiv ? educationRequirementDiv.cloneNode(true) : null;
let resetExperience = experienceRequirementDiv ? experienceRequirementDiv.cloneNode(true) : null;
let resetAsset = assetRequirementDiv ? assetRequirementDiv.cloneNode(true) : null;

/* Row of editing-related buttons */
let buttonRow = document.getElementById("import-position-buttons");

/* Array to be populated by the text from each editable field */
let cellText = [];

/* Return data for body of AJAX request */
const getEditData = function() {
  const params = Object.create(null);
  params["positionId"] = document.getElementById("position-id").value;
  cells.forEach(function(cell) {
    params[cell.id] = cell.textContent;
  });
  return params;
};

/* Sends data from edited cells via AJAX POST request */
const editPosition = function() {
  const url = "/edit-position";
  const data = JSON.stringify(getEditData());

  fetch(url, {
    method: "POST", // or "PUT"
    body: data, // data can be `string` or {object}!
    headers:{
      "Content-Type": "application/json"
    }
  }).catch(error => console.error("Error:", error));
};

/* Rearrange requirement abbreviations (i.e. EXP1) to ensure order is maintained */
const rearrangeAbbreviations = function() {
  const educationRequirements = document.querySelectorAll("div[data-requirement-type='Education']");
  const experienceRequirements = document.querySelectorAll("div[data-requirement-type='Experience']");
  const assetRequirements = document.querySelectorAll("div[data-requirement-type='Asset']");

  for (let i = 0; i < educationRequirements.length; i++) {
    educationRequirements[i].children[1].textContent = "ED" + (i+1);
  }
  for (let i = 0; i < experienceRequirements.length; i++) {
    experienceRequirements[i].children[1].textContent = "EXP" + (i+1);
  }
  for (let i = 0; i < assetRequirements.length; i++) {
    assetRequirements[i].children[1].textContent = "AEXP" + (i+1);
  }
};

/* Ensure consistency in the IDs of requirement delete buttons */
const reinitializeDeleteButtonIds = function() {
  requirementPoints = document.getElementsByClassName("requirement-point");
  const removeButtons = document.getElementsByClassName("remove-requirement-button");
  for (let i = 0; i < requirementPoints.length; i++) {
    removeButtons[i].id = "remove-button-" + i;
  }
};

/* Reinitialize data for requirement point divs */
const reinitializeRequirementPointData = function() {
  for (let i = 0; i < requirementPoints.length; i++) {
    const abbreviation = requirementPoints[i].children[1].textContent;
    requirementPoints[i].dataset.requirementAbbrev = abbreviation;
    requirementPoints[i].dataset.requirementId = i;
    requirementPoints[i].children[0].dataset.requirementAbbrev = abbreviation;
    requirementPoints[i].children[0].dataset.requirementId = i;
  }
};

/* Reinitialize IDs of cells to ensure consistency after changes made */
const reinitializeRequirementIds = function() { // LAST
  requirementPoints = document.getElementsByClassName("requirement-point");
  const requirementCells = document.getElementsByClassName("edit requirement-description");
  for (let i = 0; i < requirementCells.length; i++) {
    const abbreviation = requirementPoints[i].dataset.requirementAbbrev;
    const requirementNumber = parseInt(abbreviation.match(/\d+/g).map(Number));
    const requirementType = requirementPoints[i].dataset.requirementType;
    requirementCells[i].id = requirementType.toLowerCase() + "-" + requirementNumber.toString();
    if (requirementCells[i].children[0]) {
      requirementCells[i].children[0].name = requirementCells[i].id;
    }
  }
  cells = Array.from(document.getElementsByClassName("edit"));
};

/* Remove a requirement and reinitialize abbreviations and IDs */
const removeRequirement = function(requirementId) {
  for (let i = 0; i < requirementPoints.length; i++) {
    if (requirementPoints[i].dataset.requirementId == requirementId)  {
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
const newRequirement = function(requirementType) {
  const newNode = document.createElement("div");
  newNode.classList.add("requirement-point", "row");
  newNode.dataset.requirementType = requirementType;
  newNode.appendChild(removeRequirementButton());
  const abbrevDiv = document.createElement("div");
  abbrevDiv.classList.add("requirement-abbrev", "col");
  newNode.appendChild(abbrevDiv);
  const descripDiv = document.createElement("div");
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
const addRequirement = function(requirementType) {
  const newNode = newRequirement(requirementType);
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

  newNode.children[0].addEventListener("click", () => {
    removeRequirement(newNode.dataset.requirementId);
  });
};

/* Returns a button used to remove a requirement */
const removeRequirementButton = function(i) {
  const removeButton = document.createElement("i");
  removeButton.classList.add("material-icons", "col", "red-text", "remove-requirement-button", "left");
  removeButton.textContent = "remove_circle";
  removeButton.id = "remove-button-" + i;
  return removeButton;
};

/* Returns a button used to add a requirement */
const addRequirementButton = function(i) {
  const addButton = document.createElement("i");
  addButton.classList.add("material-icons", "orange-text", "add-requirement-button");
  addButton.textContent = "add_circle";
  addButton.id = "add-button-" + i;
  return addButton;
};

/* Adds buttons to requirement headers allowing the user to click to add requirements */
const addButtonsToRequirementHeaders = function() {
  for (let i = 0; i < requirementTypeHeaders.length; i++) {
    const requirementButton = addRequirementButton(i);
    requirementButton.dataset.requirementType = requirementTypeHeaders[i].dataset.requirementType;
    requirementButton.addEventListener("click", () => {
      addRequirement(requirementButton.dataset.requirementType);
    });
    requirementTypeHeaders[i].appendChild(requirementButton);
  }
};

/* Removes buttons from requirement headers */
const removeButtonsFromRequirementHeaders = function() {
  for (let i = 0; i < requirementTypeHeaders.length; i++) {
    requirementTypeHeaders[i].removeChild(document.getElementById("add-button-" + i));
  }
};

/* Adds buttons to requirement items allowing user to delete them */
const addButtonsToRequirements = function() {
  for (let i = 0; i < requirementPoints.length; i++) {
    const removeButton = removeRequirementButton(i);
    removeButton.dataset.requirementType = requirementPoints[i].dataset.requirementType;
    removeButton.dataset.requirementAbbrev = requirementPoints[i].dataset.requirementAbbrev;
    removeButton.dataset.requirementId = requirementPoints[i].dataset.requirementId;
    removeButton.addEventListener("click", () => {
      removeRequirement(removeButton.dataset.requirementId);
    });
    requirementPoints[i].prepend(removeButton);
  }
};

/* Removes delete buttons from requirement items */
const removeButtonsFromRequirements = function() {
  requirementPoints = document.getElementsByClassName("requirement-point");
  for (let i = 0; i < requirementPoints.length; i++) {
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
const addReqButtons = function() {
  addButtonsToRequirements();
  addButtonsToRequirementHeaders();
};

/* Removes all requirement-related buttons */
const removeReqButtons = function() {
  removeButtonsFromRequirements();
  removeButtonsFromRequirementHeaders();
};


/* Appends edit cells containing existing position data */
const defineEditCells = function(cell, name, isReadOnly) {
  let input = createReturnTextInput(cell.textContent, name, isReadOnly);
  cell.textContent = null;
  cell.appendChild(input);
};

/* Returns an edit cell with the name and value of the table data element */
const createReturnTextInput = function(text, name, isReadOnly) {
  let editableNode = document.createElement("input");
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
const defineAdditionalButtons = function() {
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
const setCardSize = function() {
  let percentage = 0;
  if (window.location.pathname.includes("/createnewposition")) {
    percentage = sidebarIsOpen ? 50 : 70; // from sd-sidenav.js
  } else {
    percentage = sidebarIsOpen ? 70 : 88;  // from sd-sidenav.js
  }
  fixPaddingWidth(); // from sd-sidenav.js
  const width = window.innerWidth < 1800 ? parseInt((window.innerWidth * percentage) / 100).toString().concat("px") : 1250;
  card.style.setProperty("max-width", width, "important");
  card.style.setProperty("width", width, "important");
  card.style.setProperty("min-width", "700px", "important");
};

const showRequirementTypeHeaders = function() {
  for (let i = 0; i < requirementTypeHeaders.length; i++) {
    requirementTypeHeaders[i].classList.remove("hide");
  }
};

const hideShowMissingRequirements = function() {
  document.querySelectorAll("div[data-requirement-type='Education']").length == 0 ? requirementTypeHeaders[0].classList.add("hide") : requirementTypeHeaders[0].classList.remove("hide");
  document.querySelectorAll("div[data-requirement-type='Experience']").length == 0 ? requirementTypeHeaders[1].classList.add("hide") : requirementTypeHeaders[1].classList.remove("hide");
  document.querySelectorAll("div[data-requirement-type='Asset']").length == 0 ? requirementTypeHeaders[2].classList.add("hide") : requirementTypeHeaders[2].classList.remove("hide");
};

/* Convert text fields into editable inputs */
const startEditing = function() {
  resetEducation = educationRequirementDiv ? educationRequirementDiv.cloneNode(true) : null;
  resetExperience = experienceRequirementDiv ? experienceRequirementDiv.cloneNode(true) : null;
  resetAsset = assetRequirementDiv ? assetRequirementDiv.cloneNode(true) : null;
  removeRequirementListeners(); // From position-tables.js
  expandAllRequirements(); // From position-tables.js
  showRequirementTypeHeaders();
  reinitializeRequirementIds();
  setCardSize();
  window.addEventListener("resize", setCardSize);
  document.getElementById("base-header").addEventListener("transitionend", setCardSize);
  showElements(okButton, cancelButton); // From helper-functions.js
  hideElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null); // From helper-functions.js

  cells.forEach(function(cell, i) {
    cellText[i] = cells[i].textContent;
    cell.classList.contains("readonly") ? defineEditCells(cell, cell.id, true) : defineEditCells(cell, cell.id, false);
  });
  addReqButtons();
};

/* Tasks associated with stopping edit, either via cancel or confirm */
const stopEditing = function() {
  addRequirementListeners(); // From position-tables.js
  hideShowMissingRequirements();
  showElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null); // From helper-functions.js
  hideElements(okButton, cancelButton); // From helper-functions.js
  card.style.setProperty("max-width", "auto", "important");
  card.style.setProperty("min-width", "700px", "important");
  removeReqButtons();
};

/* Confirm changes to position and send data via AJAX */
const confirmEditChanges = function() {
  if (form.reportValidity()) {
    stopEditing();
    cells.forEach(function(cell) {
      cell.textContent = cell.lastChild.value != null ? cell.lastChild.value : cell.value;
    });
    editPosition();
  }
};

/* Cancel edits and return position to original imported state */
const cancelEditChanges = function() {
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
  cells.forEach(function(cell, i) {
    cell.textContent = cellText[i];
  });
  cells = Array.from(document.getElementsByClassName("edit"));
  stopEditing();
};

/* LISTENERS */
window.addEventListener("DOMContentLoaded", () => {
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
