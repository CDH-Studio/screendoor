let collapseElements = document.getElementsByClassName("collapse");
let collapseArrows = document.getElementsByClassName("collapse-arrows");
let collapseAllButton = document.getElementById("collapse-all");
let expandAllButton = document.getElementById("expand-all")

/* Initializes positions table with experience and assets collapsed */
window.addEventListener('DOMContentLoaded', (event) => {
  for (let i = 0; i < collapseElements.length; i++) {
    if (i > 3) {
      collapseArrows[i].innerHTML = "keyboard_arrow_right";
      collapseRow(collapseElements[i].nextElementSibling);
    }
  }
});

/* Individual row click listeners */
for (let i = 0; i < collapseElements.length; i++) {
  collapseElements[i].style.cursor = 'pointer';
  let rowToCollapse = collapseElements[i].nextElementSibling;
  collapseElements[i].addEventListener("click", function() {
    collapseArrows[i].innerHTML == "keyboard_arrow_right" ? collapseArrows[i].innerHTML = "keyboard_arrow_down" : collapseArrows[i].innerHTML = "keyboard_arrow_right";
    expandOrCollapseRows(rowToCollapse);
  });
}

/* Collapse All button listener */
collapseAllButton.addEventListener("click", function() {
  for (let i = 0; i < collapseElements.length; i++) {
    let rowToCollapse = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_right";
    collapseRow(rowToCollapse);
  }
});

/* Expand all button listener */
expandAllButton.addEventListener("click", function() {
  for (let i = 0; i < collapseElements.length; i++) {
    let rowToExpand = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_down";
    expandRow(rowToExpand);
  }
});

/* Recursively expands successive TBODY rows */
function expandRow(rowToExpand) {
  rowToExpand.style.display = 'table-row-group';
  try {
    if (rowToExpand.nextElementSibling.tagName == "TBODY") {
      rowToExpand = rowToExpand.nextElementSibling;
      expandRow(rowToExpand);
    }
  } catch (TypeError) {}
}

/* Recursively collapses successive TBODY rows */
function collapseRow(rowToCollapse) {
  rowToCollapse.style.display = 'none';
  try {
    if (rowToCollapse.nextElementSibling.tagName == "TBODY") {
      rowToCollapse = rowToCollapse.nextElementSibling;
      collapseRow(rowToCollapse);
    }
  } catch (TypeError) {}
}

/* Toggles TBODY collapse and expand */
function expandOrCollapseRows(rowToCollapse) {
  rowToCollapse.style.display == 'none' ? rowToCollapse.style.display = 'table-row-group' : rowToCollapse.style.display = 'none';
  try {
    if (rowToCollapse.nextElementSibling.tagName == "TBODY") {
      rowToCollapse = rowToCollapse.nextElementSibling;
      expandOrCollapseRows(rowToCollapse);
    }
  } catch (TypeError) {}
}
