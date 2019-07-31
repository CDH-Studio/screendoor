/* CONSTANTS AND VARIABLES */

const card = document.getElementById("position-card");
const editButton = document.getElementById("edit-button");
const saveButton = document.getElementById("save-button");
const okButton = document.getElementById("edit-button") ? editButton.cloneNode() : null;
const cancelButton = document.getElementById("save-button") ? saveButton.cloneNode() : null;
const form = document.getElementById("edit-position");
const cells = Array.from(document.getElementsByClassName("edit"));
let buttonRow = document.getElementById("import-position-buttons");
let cellText = [];

const getEditData = function() {
  const params = Object.create(null);
  params["positionId"] = document.getElementById("position-id").value;
  cells.forEach(function(cell) {
    params[cell.id] = cell.textContent;
  });
  return params;
};

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
  })
    .catch(error => console.error("Error:", error));
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
  const percentage = window.location.pathname.includes("/createnewposition") ? 70 : 88;
  const width = window.outerWidth < 1800 ? parseInt((window.innerWidth * percentage) / 100).toString().concat("px") : 1250;
  card.style.setProperty("width", width, "important");
  card.style.setProperty("min-width", "700px", "important");
};

const startEditing = function() {
  /* From position-tables.js */
  expandAllRequirements();
  setCardSize();
  window.addEventListener("resize", setCardSize);
  /* From helper-functions.js */
  showElements(okButton, cancelButton);
  hideElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null);

  cells.forEach(function(cell, i) {
    cellText[i] = cells[i].textContent;
    cell.classList.contains("readonly") ? defineEditCells(cell, cell.id, true) : defineEditCells(cell, cell.id, false);
  });
};

const stopEditing = function() {
  showElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null);
  hideElements(okButton, cancelButton);
  card.style.setProperty("width", "auto", "important");
  card.style.setProperty("min-width", "700px", "important");
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
  stopEditing();

  cells.forEach(function(cell, i) {
    cell.textContent = cellText[i];
  });
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
