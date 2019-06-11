let editButton = document.getElementById("edit-button");
let saveButton = document.getElementById("save-button");
let okButton = editButton.cloneNode();
let cancelButton = saveButton.cloneNode();
let buttonRow = document.getElementById("import-position-buttons");
let hiddenInputs = document.getElementsByClassName("hidden");
let cells = Array.from(document.getElementsByTagName("td"));
cells.unshift(document.getElementById("title"));
let cellText = [];

/* Defines additional buttons that do not appear on page load */
window.addEventListener('DOMContentLoaded', (event) => {
  okButton.value = "OK";
  okButton.id = "ok-button";
  okButton.name = "save-edits";
  okButton.type = "button";
  okButton.style.display = "none";
  cancelButton.value = "Cancel";
  cancelButton.id = "cancel-button";
  cancelButton.name = "cancel-edits";
  cancelButton.type = "button";
  cancelButton.style.display = "none";
  buttonRow.append(okButton, cancelButton);
});

/* User presses the edit button to change position information */
editButton.addEventListener("click", function() {
  okButton.style.display = "inline";
  cancelButton.style.display = "inline";
  editButton.style.display = "none";
  saveButton.style.display = "none";

  for (let i = 0; i < cells.length; i++) {
    cellText[i] = cells[i].innerText;
    defineEditCells(cells[i], cells[i].name, false);
  }
});

/* User presses the OK button to confirm editing changes */
okButton.addEventListener("click", function() {
  editButton.style.display = "inline";
  saveButton.style.display = "inline";
  okButton.style.display = "none";
  cancelButton.style.display = "none";

  for (let i = 0; i < cells.length; i++) {
    cells[i].lastChild.value != null ?
    hiddenInputs[i].value = cells[i].lastChild.value :
                            hiddenInputs[i].value = cells[i].value;
    cells[i].lastChild.value != null ? cells[i].innerText = cells[i].lastChild.value : cells[i].innerText = cells[i].value;
  }
  document.getElementById("save-position").submit();
});

/* User presses the cancel button to cancel editing changes and revert to original */
cancelButton.addEventListener("click", function() {
  editButton.style.display = "inline";
  saveButton.style.display = "inline";
  okButton.style.display = "none";
  cancelButton.style.display = "none";

  for (let i = 0; i < cells.length; i++) {
    cells[i].innerText = cellText[i];
  }
});

/* Appends edit cells containing existing position data */
function defineEditCells(cell, name, isReadOnly) {
  let input = createReturnTextInput(cell.innerText, name);
  input.readOnly = isReadOnly;
  cell.innerText = null;
  cell.appendChild(input);
}

/* Returns an edit cell with the name and value of the table data element */
function createReturnTextInput(text, name) {
  let editableNode = document.createElement("input");
  editableNode.name = name;
  editableNode.className = "editable";
  editableNode.type = "text";
  editableNode.value = text;
  return editableNode;
}
