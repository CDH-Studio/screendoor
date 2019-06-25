/* VARIABLES */

/* Collapsible table elements */
let collapseElements = document.getElementsByClassName("collapse");
let collapseArrows = document.getElementsByClassName("collapse-arrows");

/* Buttons */
let collapseAllButton = document.getElementById("collapse-all");
let expandAllButton = document.getElementById("expand-all");

/* Ellipses */
let questionEllipses = document.getElementsByClassName("question-ellipsis");
let questionHeaders = document.getElementsByClassName("question-header");
let questionSubheads = document.getElementsByClassName("question-subhead");

/* Analysis preview and full */
let analysisSpan = document.getElementsByClassName("analysis-preview");
let questionSpan = document.getElementsByClassName("question-preview");
let questionTruncated = [];
let questionTruncatedAnalysis = [];
let analysisSubheads = [];
let previewFull = [];
let previewSmall = [];
let clickedHeaders = [];

/* Education preview */
let educationEllipses = document.getElementsByClassName("education-ellipsis");
let educationHeaders = document.getElementsByClassName("education-header");
let educationHeadersClicked = document.getElementsByClassName("education-header-clicked");
let educationAcademicTruncated = [];
let educationInstitutionTruncated = [];
let educationAreaStudyTruncated = [];

/* LISTENERS */

/* Initializes positions table with experience and assets collapsed */
window.addEventListener('DOMContentLoaded', (event) => {
  for (let i = 0; i < collapseElements.length; i++) {
    initializeRowListeners(i);
    if (i > 3) {
      collapseArrows[i].innerHTML = "keyboard_arrow_right";
      collapseRow(collapseElements[i].nextElementSibling);
    }
  }
  initializeEducationListeners();
  initializeQuestionListeners();
});

/* Individual row click listeners */
function initializeRowListeners(i) {
  collapseElements[i].style.cursor = 'pointer';
  let row = collapseElements[i].nextElementSibling;

  collapseElements[i].addEventListener("click", function() {
    openCloseArrow(i);
    expandOrCollapseRows(row);
  });
}

/* Collapse All button listener */
collapseAllButton.addEventListener("click", collapseAll);

/* Expand all button listener */
expandAllButton.addEventListener("click", expandAll);

/* Initialize question listeners */
function initializeQuestionListeners() {

  /* Initializes and adds listeners for truncated question text */
  for (let i = 0; i < questionEllipses.length; i++) {
    previewFull[i] = document.getElementById("previews-full" + i);
    previewSmall[i] = document.getElementById("previews-small" + i);
    questionTruncated[i] = document.getElementById("truncated" + i);
    questionTruncatedAnalysis[i] = document.getElementById("truncated-analysis" + i);
    analysisSubheads[i] = document.getElementById("analysis-subhead" + i);
    clickedHeaders[i] = document.getElementById("clicked-header" + i);

    hideElement(clickedHeaders[i], previewFull[i]);
    displayEllipsesIfNeeded(i);

    /* User clicks question header */
    questionHeaders[i].addEventListener("click", () => { expandCollapseQuestionHeaders(i); });

    /* User moves mouse over a question ellipsis */
    questionEllipses[i].addEventListener("mouseover", () => { showQuestionPreview(i); });

    /* User moves mouse off a question ellipsis */
    questionHeaders[i].addEventListener("mouseleave", () => { hideQuestionPreview(i); });

    /* Resize adjustment for ellipses */
    window.addEventListener('resize', () => { displayEllipsesIfNeeded(i); });
  }
}

/* Initializes and creates listeners for education header truncation */
function initializeEducationListeners() {
  for (let i = 0; i < educationEllipses.length; i++) {
    educationAcademicTruncated[i] = document.getElementById("education-academic-truncated" + i);
    educationInstitutionTruncated[i] = document.getElementById("education-institution-truncated" + i);
    educationAreaStudyTruncated[i] = document.getElementById("education-areastudy-truncated" + i);

    if (!isEllipsisActive(educationAreaStudyTruncated[i]) &&
        !isEllipsisActive(educationInstitutionTruncated[i]) &&
        !isEllipsisActive(educationAcademicTruncated[i])) {
      hideElement(educationEllipses[i]);
    }

    /* User clicks to show education detail */
    educationHeaders[i].addEventListener("click", () => { showEducationFull(i); });

    /* User clicks to hide education detail */
    educationHeadersClicked[i].addEventListener("click", () => { hideEducationFull(i); });

    /* User moves mouse over education ellipsis */
    educationEllipses[i].addEventListener("mouseover", () => { showEducationPreview(i); });

    /* User moves mouse off education ellipsis */
    educationHeaders[i].addEventListener("mouseleave", () => { hideEducationPreview(i); });

    /* Handles window resizing and adding/removing ellipses based on browser window size */
    window.addEventListener('resize', () => { displayEllipsesIfNeeded(i); });
  }
}

/* HELPER FUNCTIONS */

/* Display ellipses if there is truncated text on row */
function displayEllipsesIfNeeded(i) {
  !isEllipsisActive(questionTruncated[i])
    && !isEllipsisActive(questionTruncatedAnalysis[i]) ? hideElement(questionEllipses[i]) : showElement(questionEllipses[i]);
}

/* Arrow indicates row is open or closed */
function openCloseArrow(i) {
  collapseArrows[i].innerHTML == "keyboard_arrow_right" ? collapseArrows[i].innerHTML = "keyboard_arrow_down" : collapseArrows[i].innerHTML = "keyboard_arrow_right";
}

/* User wants to view question detail */
function expandCollapseQuestionHeaders(i) {
  if (!isOpen(previewSmall[i])) {
    expandQuestionHeaders(i);
  } else {
    collapseQuestionHeaders(i);
  }
}

function expandQuestionHeaders(i) {
  showElement(clickedHeaders[i]);
  hideElement(previewFull[i], previewSmall[i]);
  backgroundOffWhite(questionHeaders[i]);
}

function collapseQuestionHeaders(i) {
  showElement(previewSmall[i]);
  hideElement(clickedHeaders[i]);
  backgroundWhite(questionHeaders[i]);
  hideQuestionPreview(i);
}

/* User moves mouse over question ellipses */
function showQuestionPreview(i) {
  hideElement(analysisSpan[i], questionSpan[i]);
  showElement(previewFull[i], questionSubheads[i]);
  backgroundOffWhite(previewSmall[i]);
  unTruncate(questionTruncated[i]);
  growEllipsis(questionEllipses[i]);

  if (analysisSubheads[i]) {
    showElement(analysisSubheads[i]);
  }
  if (questionTruncatedAnalysis[i]) {
    unTruncate(questionTruncatedAnalysis[i]);
  }
}

/* User moves mouse off question preview */
function hideQuestionPreview(i) {
  showElement(analysisSpan[i], questionSpan[i]);
  hideElement(questionSubheads[i], previewFull[i]);
  backgroundWhite(previewSmall[i]);
  truncate(questionTruncated[i]);
  shrinkEllipsis(questionEllipses[i]);

  if (analysisSubheads[i]) {
    hideElement(analysisSubheads[i]);
  }
  if (questionTruncatedAnalysis[i]) {
    truncate(questionTruncatedAnalysis[i]);
  }
}

/* User clicks an education row */
function showEducationFull(i) {
  showElement(educationHeadersClicked[i]);
  hideElement(educationHeaders[i]);
}

/* User clicks an expanded education row */
function hideEducationFull(i) {
  hideElement(educationHeadersClicked[i]);
  showElement(educationHeaders[i]);
}

/* User moves mouse over education ellipses */
function showEducationPreview(i) {
  if (isEllipsisActive(educationAreaStudyTruncated[i]) ||
      isEllipsisActive(educationInstitutionTruncated[i]) ||
      isEllipsisActive(educationAcademicTruncated[i])) {
    growEllipsis(educationEllipses[i]);
  }
  backgroundOffWhite(educationHeaders[i]);
  unTruncate(educationAcademicTruncated[i], educationInstitutionTruncated[i], educationAreaStudyTruncated[i]);
}

/* User moves mouse off education preview */
function hideEducationPreview(i) {
  backgroundWhite(educationHeaders[i]);
  shrinkEllipsis(educationEllipses[i]);
  truncate(educationAcademicTruncated[i], educationAreaStudyTruncated[i], educationInstitutionTruncated[i]);
}

/* Row is currently expanded */
function isOpen(row) {
  return row.classList.contains("hide");
}

/* Recursively expands successive TBODY rows */
function expandRow(row) {
  row.classList.remove("hide");
  try {
    if (row.nextElementSibling.tagName == "TBODY") {
      row = row.nextElementSibling;
      expandRow(row);
    }
  } catch (TypeError) {}
}

/* Recursively collapses successive TBODY rows */
function collapseRow(row) {
  row.classList.add("hide");
  try {
    if (row.nextElementSibling.tagName == "TBODY") {
      row = row.nextElementSibling;
      collapseRow(row);
    }
  } catch (TypeError) {}
}

/* Toggles TBODY collapse and expand */
function expandOrCollapseRows(row) {
  row.classList.contains("hide") ? row.classList.remove("hide") : row.classList.add("hide");
  try {
    if (row.nextElementSibling.tagName == "TBODY") {
      row = row.nextElementSibling;
      expandOrCollapseRows(row);
    }
  } catch (TypeError) {}
}

/* Collapse all rows */
function collapseAll() {
  for (let i = 0; i < collapseElements.length; i++) {
    let row = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_right";
    collapseRow(row);
    for (let i = 0; i < questionHeaders.length; i++) {
      collapseQuestionHeaders(i);
    }
    for (let i = 0; i < educationHeaders.length; i++) {
      hideEducationFull(i);
    }
  }
}

/* Expand all rows */
function expandAll() {
  for (let i = 0; i < collapseElements.length; i++) {
    let rowToExpand = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_down";
    expandRow(rowToExpand);
  }
  for (let i = 0; i < questionHeaders.length; i++) {
    expandQuestionHeaders(i);
  }
  for (let i = 0; i < educationHeaders.length; i++) {
    showEducationFull(i);
  }
}

/* Hide an HTML element */
function hideElement(...elements) {
  elements.forEach(element => element.classList.add("hide"));
}

/* Show an HTML element */
function showElement(...elements) {
  elements.forEach(element => element.classList.remove("hide"));
}

/* Truncate the text in an HTML element */
function truncate(...elements) {
  elements.forEach(element => element.classList.add("truncation"));
  elements.forEach(element => element.classList.remove("truncation-open"));
}

/* Un-truncate the text in an HTML element */
function unTruncate(...elements) {
  elements.forEach(element => element.classList.remove("truncation"));
  elements.forEach(element => element.classList.add("truncation-open"));
}

/* Indicate that an ellipsis has mouse over it */
function growEllipsis(element) {
  element.classList.remove("ellipsis");
  element.classList.add("ellipsis-larger");
}

/* Restore ellipsis to default look */
function shrinkEllipsis(element) {
  element.classList.remove("ellipsis-larger");
  element.classList.add("ellipsis");
}

/* Highlight element with off-white background */
function backgroundOffWhite(element) {
  element.style.transition = "all .5s ease";
  element.style.backgroundColor = "rgba(242, 242, 242, 0.5)";
}

/* Restore background to white */
function backgroundWhite(element) {
  element.style.backgroundColor = "#ffffff";
}

/* Returns true if the text in an element is truncated */
function isEllipsisActive(e) {
  if (e) {
    return (e.offsetWidth < e.scrollWidth);
  }
  return false;
}
