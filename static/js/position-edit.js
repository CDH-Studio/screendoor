/* CONSTANTS AND VARIABLES */

const editButton = document.getElementById("edit-button");
const saveButton = document.getElementById("save-button");
const okButton = editButton.cloneNode();
const cancelButton = saveButton.cloneNode();
const hiddenInputs = document.getElementsByClassName("hidden");
const form = window.location.pathname.includes("/createnewposition") ? document.getElementById("save-edit-position") : document.getElementById("save-position");
const cells = Array.from(document.getElementsByClassName("edit"));
let buttonRow = document.getElementById("import-position-buttons");
let cellText = [];

document.addEventListener('DOMContentLoaded', function() {
  var datepickers = document.querySelectorAll('.datepicker');
  var datepickerInstances = M.Datepicker.init(datepickers, {});
});

/* HELPER FUNCTIONS */

/* Appends edit cells containing existing position data */
const defineEditCells = function(cell, name, isReadOnly) {
  let input = createReturnTextInput(cell.innerText, name, isReadOnly);
  cell.innerText = null;
  cell.appendChild(input);
};

/* Returns an edit cell with the name and value of the table data element */
const createReturnTextInput = function(text, name, isReadOnly) {
  let editableNode = document.createElement("input");
  editableNode.readOnly = isReadOnly;
  editableNode.name = name;
  editableNode.className = "editing";
  editableNode.value = text;
  if (name == "position-date-closed") {
    editableNode.type = "date";
    editableNode.value = text;
  } else if (name.includes("salary")) {
    editableNode.style.width = "60";
    editableNode.type = "number";
  } else {
    editableNode.type = "text";
  }
  editableNode.setAttribute("required", "");;
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
  if (window.location.pathname.includes("/position")) {
    expandAllButton.click();
  }
  showElements(okButton, window.location.pathname.includes("/createnewposition") ? cancelButton : null);
  hideElements(editButton, window.location.pathname.includes("/createnewposition") ? saveButton : null);

  cells.forEach(function(cell, i) {
    cellText[i] = cells[i].innerText;
    cell.classList.contains("readonly") ? defineEditCells(cell, cell.id, true) : defineEditCells(cell, cell.id, false);
  });
};

const confirmEditChanges = function() {
  if (form.reportValidity()) {
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
  defineAdditionalButtons();

  /* User presses the edit button to change position information */
  editButton.addEventListener("click", startEditing);

  /* User presses the OK button to confirm editing changes */
  okButton.addEventListener("click", confirmEditChanges);

  /* User presses the cancel button to cancel editing changes and revert to original */
  cancelButton.addEventListener("click", cancelEditChanges);
});
