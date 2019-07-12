/* CONSTANTS AND VARIABLES */

const editButton = document.getElementById("edit-button");
const saveButton = document.getElementById("save-button");
const okButton = document.getElementById("edit-button") ? editButton.cloneNode() : null;
const cancelButton = document.getElementById("save-button") ? saveButton.cloneNode() : null;
const hiddenInputs = document.getElementsByClassName("hidden");
const cells = window.location.pathname.includes("/createnewposition") ? Array.from(document.getElementsByTagName("td")) : Array.from(document.getElementsByClassName("editable")[0].getElementsByTagName("td"));
cells.unshift(document.getElementById("title"));
let buttonRow = document.getElementById("import-position-buttons");
let cellText = [];

/* HELPER FUNCTIONS */

/* Appends edit cells containing existing position data */
const defineEditCells = function(cell, name, isReadOnly) {
  let input = createReturnTextInput(cell.innerText, name);
  input.readOnly = isReadOnly;
  if (!isReadOnly) {
    cell.innerText = null;
    cell.appendChild(input);
  }
};

/* Returns an edit cell with the name and value of the table data element */
const createReturnTextInput = function(text, name) {
  let editableNode = document.createElement("input");
  editableNode.name = name;
  editableNode.className = "editable";
  editableNode.type = "text";
  editableNode.value = text;
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

const startEditing = function() {
  showElements(okButton, window.location.pathname.includes("/createnewposition") ? cancelButton : null);
  hideElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null);

  cells.forEach(function(cell, i) {
    cellText[i] = cells[i].innerText;
    cell.className == "readonly" ? defineEditCells(cell, cell.name, true) : defineEditCells(cell, cell.name, false);
  });
};

const confirmEditChanges = function() {
  showElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null);
  hideElements(okButton, window.location.pathname.includes("/createnewposition") ? cancelButton : null);

  cells.forEach(function(cell, i) {
    cell.lastChild.value != null ? hiddenInputs[i].value = cell.lastChild.value :
      hiddenInputs[i].value = cell.value;
    cell.lastChild.value != null ? cell.innerText = cell.lastChild.value : cell.innerText = cell.value;
  });
  if (window.location.pathname.includes("/position")) {
    document.getElementById("save-position").submit();
  }
};

const cancelEditChanges = function() {
  showElements(editButton, saveButton);
  hideElements(okButton, cancelButton);

  cells.forEach(function(cell, i) {
    cell.innerText = cellText[i];
  });
};

/* LISTENERS */
window.addEventListener('DOMContentLoaded', (event) => {
  /* Defines additional buttons that do not appear on page load */
  if (document.getElementById("edit-button")) {
    defineAdditionalButtons();
  /* User presses the edit button to change position information */
  editButton.addEventListener("click", startEditing);

  /* User presses the OK button to confirm editing changes */
  okButton.addEventListener("click", confirmEditChanges);
  }

  if (cancelButton) {
    /* User presses the cancel button to cancel editing changes and revert to original */
    cancelButton.addEventListener("click", cancelEditChanges);
  }
});
