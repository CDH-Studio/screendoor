/* CONSTANTS AND VARIABLES */

/* Collapsible table elements */
const collapseElements = document.getElementsByClassName("collapse");
const collapseArrows = document.getElementsByClassName("collapse-arrows");

/* Buttons */
const collapseAllButton = document.getElementById("collapse-all");
const expandAllButton = document.getElementById("expand-all");

/* Ellipses */
const questionEllipses = document.getElementsByClassName("question-ellipsis");
const questionHeaders = document.getElementsByClassName("question-header");
const questionSubheads = document.getElementsByClassName("question-subhead");

/* Analysis preview and full */
const analysisSpan = document.getElementsByClassName("analysis-preview");
const questionSpan = document.getElementsByClassName("question-preview");
let questionTruncated = [];
let questionTruncatedAnalysis = [];
let analysisSubheads = [];
let previewFull = [];
let previewSmall = [];
let clickedHeaders = [];

/* Education preview */
const educationEllipses = document.getElementsByClassName("education-ellipsis");
const educationHeaders = document.getElementsByClassName("education-header");
const educationHeadersClicked = document.getElementsByClassName("education-header-clicked");
let educationAcademicTruncated = [];
let educationInstitutionTruncated = [];
let educationAreaStudyTruncated = [];

/* HELPER FUNCTIONS */

const slideCloseElements = function(...elements) {
  for (let element of elements) {
    if (element) {
      element.classList.add("row-closed");
      // element.ontransitionend = () => {
      //   element.classList.add("invisible");
      // };
    }
  }
};

const slideOpenElements = function(...elements) {
  for (let element of elements) {
    if (element) {
      element.classList.remove("row-closed");
      // element.classList.remove("invisible");
      // element.ontransitionend = () => {
      //   element.classList.remove("invisible");
      // };
    }
  }
};

/* Toggles TBODY collapse and expand */
const toggleRow = function(row) {
  if (row) {
    row.classList.contains("row-closed") ? slideOpenElements(row) : slideCloseElements(row);
    try {
      if (row.nextElementSibling.classList.contains("body-row")) {
        row = row.nextElementSibling;
        toggleRow(row);
      }
    } catch (TypeError) {}
  }
};

/* Display ellipses if there is truncated text on row */
const displayEllipsesIfNeeded = function(i) {
  !isEllipsisActive(questionTruncated[i], questionTruncatedAnalysis[i]) ? slideCloseElements(questionEllipses[i]) : slideOpenElements(questionEllipses[i]);
};

/* Arrow indicates row is open or closed */
const openCloseArrow = function(i) {
  collapseArrows[i].innerHTML == "keyboard_arrow_right" ? collapseArrows[i].innerHTML = "keyboard_arrow_down" : collapseArrows[i].innerHTML = "keyboard_arrow_right";
};

/* User wants to view question detail */
const expandCollapseQuestionHeaders = function(i) {
  !isOpen(previewSmall[i]) ? expandQuestionHeaders(i) : collapseQuestionHeaders(i);
};

const expandQuestionHeaders = function(i) {
  slideOpenElements(clickedHeaders[i]);
  slideCloseElements(previewFull[i], previewSmall[i]);
  // backgroundOffWhite(questionHeaders[i]);
};

const collapseQuestionHeaders = function(i) {
  slideOpenElements(previewSmall[i]);
  slideCloseElements(clickedHeaders[i]);
  // backgroundWhite(questionHeaders[i]);
  hideQuestionPreview(i);
};

/* User moves mouse over question ellipses */
const showQuestionPreview = function(i) {
  slideCloseElements(analysisSpan[i], questionSpan[i]);
  slideOpenElements(previewFull[i], questionSubheads[i]);
  // backgroundOffWhite(previewSmall[i]);
  unTruncate(questionTruncated[i]);
  growEllipsis(questionEllipses[i]);

  if (analysisSubheads[i]) {
    slideOpenElements(analysisSubheads[i]);
  }
  if (questionTruncatedAnalysis[i]) {
    unTruncate(questionTruncatedAnalysis[i]);
  }
};

/* User moves mouse off question preview */
const hideQuestionPreview = function(i) {
  slideOpenElements(analysisSpan[i], questionSpan[i]);
  slideCloseElements(questionSubheads[i], previewFull[i]);
  // backgroundWhite(previewSmall[i]);
  truncate(questionTruncated[i]);
  shrinkEllipsis(questionEllipses[i]);

  if (analysisSubheads[i]) {
    slideCloseElements(analysisSubheads[i]);
  }
  if (questionTruncatedAnalysis[i]) {
    truncate(questionTruncatedAnalysis[i]);
  }
};

/* User clicks an education row */
const showEducationFull = function(i) {
  showElements(educationHeadersClicked[i]);
  slideOpenElements(educationHeadersClicked[i]);
  hideElements(educationHeaders[i]);
  slideCloseElements(educationHeaders[i]);
};

/* User clicks an expanded education row */
const hideEducationFull = function(i) {
  hideElements(educationHeadersClicked[i]);
  slideCloseElements(educationHeadersClicked[i]);
  showElements(educationHeaders[i]);
  slideOpenElements(educationHeaders[i]);
};

/* User moves mouse over education ellipses */
const showEducationPreview = function(i) {
  if (isEllipsisActive(educationAreaStudyTruncated[i], educationInstitutionTruncated[i], educationAcademicTruncated[i])) {
    growEllipsis(educationEllipses[i]);
  }
  // backgroundOffWhite(educationHeaders[i]);
  unTruncate(educationAcademicTruncated[i], educationInstitutionTruncated[i], educationAreaStudyTruncated[i]);
};

/* User moves mouse off education preview */
const hideEducationPreview = function(i) {
  // backgroundWhite(educationHeaders[i]);
  shrinkEllipsis(educationEllipses[i]);
  truncate(educationAcademicTruncated[i], educationAreaStudyTruncated[i], educationInstitutionTruncated[i]);
};

/* Row is currently expanded */
const isOpen = function(row) {
  return !row.classList.contains("row-closed");
};

/* Recursively expands successive TBODY rows */
const expandRow = function(row) {
  row.classList.remove("row-closed");
  try {
    if (row.nextElementSibling.classList.contains("body-row")) {
      row = row.nextElementSibling;
      expandRow(row);
    }
  } catch (TypeError) {}
};

/* Recursively collapses successive TBODY rows */
const collapseRow = function(row) {
  if (row) {
    row.classList.add("row-closed");
    try {
      if (row.nextElementSibling.classList.contains("body-row")) {
        row = row.nextElementSibling;
        collapseRow(row);
      }
    } catch (TypeError) {}
  }
};

/* Toggles TBODY collapse and expand */
const expandOrCollapseRows = function(row) {
  row.classList.contains("row-closed") ? row.classList.remove("row-closed") : row.classList.add("row-closed");
  try {
    if (row.nextElementSibling.classList.contains("body-row")) {
      row = row.nextElementSibling;
      expandOrCollapseRows(row);
    }
  } catch (TypeError) {}
};

/* Collapse all rows */
const collapseAll = function() {
  for (let i = 0; i < collapseElements.length; i++) {
    let row = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_right";
    collapseRow(row);
  }

  for (let i = 0; i < questionHeaders.length; i++) {
    collapseQuestionHeaders(i);
  }

  for (let i = 0; i < questionHeaders.length; i++) {
    hideEducationFull(i);
  }
};

/* Expand all rows */
const expandAll = function() {
  for (let i = 0; i < collapseElements.length; i++) {
    let row = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_down";
    expandRow(row);
  }

  for (let i = 0; i < questionHeaders.length; i++) {
    expandQuestionHeaders(i);
  }

  for (let i = 0; i < questionHeaders.length; i++) {
    showEducationFull(i);
  }
};

/* Truncate the text in an HTML element */
const truncate = function(...elements) {
  elements.forEach(function(element) {
    if (element) {
      element.classList.add("truncation");
      element.classList.remove("truncation-open");
    }
  });
};

/* Un-truncate the text in an HTML element */
const unTruncate = function(...elements) {
  elements.forEach(function(element) {
    if (element) {
      element.classList.remove("truncation");
      element.classList.add("truncation-open");
    }
  });
};

/* Indicate that an ellipsis has mouse over it */
const growEllipsis = function(element) {
  element.classList.remove("ellipsis");
  element.classList.add("ellipsis-larger");
};

/* Restore ellipsis to default look */
const shrinkEllipsis = function(element) {
  element.classList.remove("ellipsis-larger");
  element.classList.add("ellipsis");
};

/* Highlight element with off-white background */
const backgroundOffWhite = function(element) {
  element.style.transition = "all .5s ease";
  element.style.backgroundColor = "rgba(242, 242, 242, 0.5)";
};

/* Restore background to white */
const backgroundWhite = function(element) {
  element.style.backgroundColor = "#ffffff";
};

/* Returns true if the text in an element is truncated */
const isEllipsisActive = function(...elements) {
  for (let i = 0; i < elements.length; i++) {
    if (elements[i]) {
      if (elements[i].offsetWidth < elements[i].scrollWidth) {
        return true;
      }
    }
  }
  return false;
};

/* LISTENERS */

/* Individual row click listeners */
const initializeRowListeners = function(i) {
  collapseElements[i].style.cursor = 'pointer';
  let row = collapseElements[i].nextElementSibling;

  collapseElements[i].addEventListener("click", function() {
    openCloseArrow(i);
    toggleRow(row);
  });
};

/* Initialize question listeners */
const initializeQuestionListeners = function() {

  /* Initializes and adds listeners for truncated question text */
  for (let i = 0; i < questionEllipses.length; i++) {
    previewFull[i] = document.getElementById("previews-full" + i);
    previewSmall[i] = document.getElementById("previews-small" + i);
    questionTruncated[i] = document.getElementById("truncated" + i);
    questionTruncatedAnalysis[i] = document.getElementById("truncated-analysis" + i);
    analysisSubheads[i] = document.getElementById("analysis-subhead" + i);
    clickedHeaders[i] = document.getElementById("clicked-header" + i);

    slideCloseElements(clickedHeaders[i], previewFull[i]);
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
};

/* Initializes and creates listeners for education header truncation */
const initializeEducationListeners = function() {
  for (let i = 0; i < educationEllipses.length; i++) {
    educationAcademicTruncated[i] = document.getElementById("education-academic-truncated" + i);
    educationInstitutionTruncated[i] = document.getElementById("education-institution-truncated" + i);
    educationAreaStudyTruncated[i] = document.getElementById("education-areastudy-truncated" + i);

    if (!isEllipsisActive(educationAreaStudyTruncated[i], educationInstitutionTruncated[i], educationAcademicTruncated[i])) {
      hideElements(educationEllipses[i]);
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
};

/* Initializes positions table with experience and assets collapsed */
window.addEventListener('DOMContentLoaded', (event) => {
  /* Collapse All button listener */
  collapseAllButton.addEventListener("click", collapseAll);

  /* Expand all button listener */
  expandAllButton.addEventListener("click", expandAll);

  for (let i = 0; i < collapseElements.length; i++) {
    initializeRowListeners(i);
    // if (i > (window.location.pathname.includes("application") ? 3 : 2)) {
    //   collapseArrows[i].innerHTML = "keyboard_arrow_right";
    //   collapseRow(collapseElements[i].nextElementSibling);
    // }
  }

  if (window.location.pathname.includes("application")) {
    initializeEducationListeners();
    initializeQuestionListeners();
  }
});
