/* CONSTANTS AND VARIABLES */

const card = document.getElementById("position-card");
const editButton = document.getElementById("edit-button");
const saveButton = document.getElementById("save-button");
const okButton = document.getElementById("edit-button") ? editButton.cloneNode() : null;
const cancelButton = document.getElementById("save-button") ? saveButton.cloneNode() : null;
const form = document.getElementById("edit-position");
let cells = Array.from(document.getElementsByClassName("edit"));

const requirementTypeHeaders = document.getElementsByClassName("requirement-type");
const requirementSections = document.getElementsByClassName("hidden-requirement-info");

let requirementPoints = document.getElementsByClassName("requirement-point");
let requirementDescriptions = document.getElementsByClassName("requirement-description");
let requirementAbbreviations = document.getElementsByClassName("requirement-abbrev");

let educationRequirementDiv = document.getElementById("education-requirements");
let experienceRequirementDiv = document.getElementById("experience-requirements");
let assetRequirementDiv = document.getElementById("asset-requirements");

let resetEducation = educationRequirementDiv ? educationRequirementDiv.cloneNode(true) : null;
let resetExperience = experienceRequirementDiv ? experienceRequirementDiv.cloneNode(true) : null;
let resetAsset = assetRequirementDiv ? assetRequirementDiv.cloneNode(true) : null;

let buttonRow = document.getElementById("import-position-buttons");
let cellText = [];

/* AJAX FUNCTIONS */

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

const removeRequirement = function(requirementId) {
  for (let i = 0; i < requirementPoints.length; i++) {
    if (requirementPoints[i].dataset.requirementId == requirementId)  {
      requirementPoints[i].remove();
    }
  }
  requirementPoints = document.getElementsByClassName("requirement-point");
  rearrangeAbbreviations();
  // initRemoveButtonHandlers();
};

const initRemoveButtonHandlers = function() {
  const removeButtons = document.getElementsByClassName("remove-requirement-button");
  console.log(removeButtons);
  console.log(removeButtons.length);
  for (let i = 0; i < removeButtons.length; i++) {
    removeButtons[i].addEventListener("click", () => {
      removeRequirement(i);
    });
  }
};

const newRequirement = function(requirementType) {
  for (let i = requirementPoints.length - 1; i > 0; i--) {
    if (requirementPoints[i].dataset.requirementType == requirementType) {
      const abbreviation = requirementPoints[i].children[1].textContent;
      const requirementNumber = parseInt(abbreviation.match(/\d+/g).map(Number));
      const newAbbreviation = abbreviation.replace(/[0-9]/g, "") + (requirementNumber + 1).toString();
      const newNode = requirementPoints[i].cloneNode(true);
      newNode.dataset.requirementId = parseInt(newNode.dataset.requirementId + 1).toString();
      newNode.children[0].addEventListener("click", () => {
        removeRequirement(newNode.dataset.requirementId);
      });
      newNode.children[1].textContent = newAbbreviation;
      newNode.children[2].children[0].value = "";
      newNode.children[2].id = requirementType.toLowerCase() + "-description-" + parseInt(requirementNumber + 1);
      return newNode;
    }
  }
};

const addRequirement = function(requirementType) {
  switch (requirementType) {
  case "Education":
    educationRequirementDiv.appendChild(newRequirement(requirementType));
    break;
  case "Experience":
    experienceRequirementDiv.appendChild(newRequirement(requirementType));
    break;
  case "Asset":
    assetRequirementDiv.appendChild(newRequirement(requirementType));
    break;
  }
};

const removeRequirementButton = function(i) {
  const removeButton = document.createElement("i");
  removeButton.classList.add("material-icons", "col", "red-text", "remove-requirement-button", "left");
  removeButton.textContent = "remove_circle";
  removeButton.id = "remove-button-" + i;
  return removeButton;
};

const addRequirementButton = function(i) {
  const addButton = document.createElement("i");
  addButton.classList.add("material-icons", "orange-text", "add-requirement-button");
  addButton.textContent = "add_circle";
  addButton.id = "add-button-" + i;
  return addButton;
};

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

const removeButtonsFromRequirementHeaders = function() {
  for (let i = 0; i < requirementTypeHeaders.length; i++) {
    requirementTypeHeaders[i].removeChild(document.getElementById("add-button-" + i));
  }
};

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

const removeButtonsFromRequirements = function() {
  for (let i = 0; i < requirementPoints.length; i++) {
    try {
      if (document.getElementById("remove-button-" + i)) {
        requirementPoints[i].removeChild(document.getElementById("remove-button-" + i));
      }
    } catch (NotFoundError) {
      null;
    }
  }
};

const addReqButtons = function() {
  addButtonsToRequirements();
  addButtonsToRequirementHeaders();
};

const removeReqButtons = function() {
  removeButtonsFromRequirements();
  removeButtonsFromRequirementHeaders();
};

const getEditData = function() {
  const params = Object.create(null);
  params["positionId"] = document.getElementById("position-id").value;
  cells.forEach(function(cell) {
    params[cell.id] = cell.textContent;
  });
  return params;
};

/* HELPER FUNCTIONS */

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
  if (name == "position-date-closed") {
    editableNode.type = "date";
  } else {
    editableNode.type = "text";
  }
  editableNode.value = text.trim();
  editableNode.setAttribute("required", "");
  return editableNode;
};

const defineAdditionalButtons = function() {
  okButton.value = document.getElementById("ok-button-text") ? document.getElementById("ok-button-text").value : null;
  okButton.id = "ok-button";
  okButton.name = "save-edits";
  okButton.type = "button";
  okButton.classList.add("hide");
  cancelButton.value = document.getElementById("cancel-button-text") ? document.getElementById("cancel-button-text").value : null;
  cancelButton.id = "cancel-button";
  cancelButton.name = "cancel-edits";
  cancelButton.type = "button";
  cancelButton.classList.add("hide");
  buttonRow.append(okButton, cancelButton);
};

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

const startEditing = function() {
  removeRequirementListeners(); // From position-tables.js
  expandAllRequirements(); // From position-tables.js
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

const stopEditing = function() {
  addRequirementListeners(); // From position-tables.js
  showElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null); // From helper-functions.js
  hideElements(okButton, cancelButton);
  card.style.setProperty("max-width", "auto", "important");
  card.style.setProperty("min-width", "700px", "important");
  removeReqButtons();
};

const confirmEditChanges = function() {
  if (form.reportValidity()) {
    stopEditing();

    cells.forEach(function(cell) {
      cell.textContent = cell.lastChild.value != null ? cell.lastChild.value : cell.value;
    });
    editPosition();
  }
};

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
  }
});
