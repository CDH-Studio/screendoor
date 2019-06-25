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
  collapseAll();
});

function collapseAll() {
  for (let i = 0; i < collapseElements.length; i++) {
    let rowToCollapse = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_right";
    collapseRow(rowToCollapse);
    questionHeaders[i].click();
  }
}

/* Expand all button listener */
expandAllButton.addEventListener("click", function() {
  expandAll();
});

function expandAll() {
  for (let i = 0; i < collapseElements.length; i++) {
    let rowToExpand = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_down";
    expandRow(rowToExpand);
  }
}

function showPreviewContents(preview, analysis, question) {
  preview.style.display = "table-row";
  analysis.style.display = "none";
  question.style.display = "none";
}

function hidePreviewContents(preview, analysis, question) {
  preview.style.display = "none";
  analysis.style.display = "inline";
  question.style.display = "inline";
}

/* Initializes and adds listeners for truncated question text */
for (let i = 0; i < questionEllipses.length; i++) {
  previewFull[i] = document.getElementById("previews-full" + i);
  previewFull[i].style.display = "None";
  previewSmall[i] = document.getElementById("previews-small" + i);
  questionTruncated[i] = document.getElementById("truncated" + i);
  questionTruncatedAnalysis[i] = document.getElementById("truncated-analysis" + i);
  analysisSubheads[i] = document.getElementById("analysis-subhead" + i);
  clickedHeaders[i] = document.getElementById("clicked-header" + i);
  questionHeaders[i].isOpen = false;
  hideElement(clickedHeaders[i]);

  !isEllipsisActive(questionTruncated[i])
                           && !isEllipsisActive(questionTruncatedAnalysis[i]) ? hideElement(questionEllipses[i]) :
                              showElement(questionEllipses[i])

  /* User clicks question header */
  questionHeaders[i].addEventListener("click", function() {
    if (!questionHeaders[i].isOpen) {
      showElement(clickedHeaders[i]);
      hideElement(previewFull[i]);
      hideElement(previewSmall[i]);
      clickedHeaders[i].style.display = "table-row";
      questionHeaders[i].isOpen = true;
    } else {
      hideElement(clickedHeaders[i]);
      showElement(previewSmall[i]);
      showElement(previewFull[i]);
      clickedHeaders[i].style.display = "none";
      questionHeaders[i].isOpen = false;
    }
  });

  /* User moves mouse over a question ellipsis */
  questionEllipses[i].addEventListener("mouseover", function() {
    showPreviewContents(previewFull[i], analysisSpan[i], questionSpan[i]);
    backgroundOffWhite(previewSmall[i]);
    showElement(questionSubheads[i]);
    unTruncate(questionTruncated[i]);
    growEllipsis(questionEllipses[i]);

    if (analysisSubheads[i]) {
      showElement(analysisSubheads[i]);
    }
    if (questionTruncatedAnalysis[i]) {
      unTruncate(questionTruncatedAnalysis[i]);
    }
  });

  /* User moves mouse off a question ellipsis */
  questionHeaders[i].addEventListener("mouseleave", function() {
    hidePreviewContents(previewFull[i], analysisSpan[i], questionSpan[i]);
    backgroundWhite(previewSmall[i]);
    hideElement(questionSubheads[i]);
    shrinkEllipsis(questionEllipses[i]);
    truncate(questionTruncated[i]);

    if (analysisSubheads[i]) {
      hideElement(analysisSubheads[i]);
    }
    if (questionTruncatedAnalysis[i]) {
      truncate(questionTruncatedAnalysis[i]);
    }
  });
}

/* Initializes and creates listener for education header truncation */
for (let i = 0; i < educationEllipses.length; i++) {
  educationAcademicTruncated[i] = document.getElementById("education-academic-truncated" + i);
  educationInstitutionTruncated[i] = document.getElementById("education-institution-truncated" + i);
  educationAreaStudyTruncated[i] = document.getElementById("education-areastudy-truncated" + i);
  educationHeaders[i].isOpen = false;

  if (!isEllipsisActive(educationAreaStudyTruncated[i]) &&
      !isEllipsisActive(educationInstitutionTruncated[i]) &&
      !isEllipsisActive(educationAcademicTruncated[i])) {
    hideElement(educationEllipses[i]);
  }

  educationHeaders[i].addEventListener("click", function() {
    showElement(educationHeadersClicked[i]);
    hideElement(educationHeaders[i]);
    educationHeadersClicked[i].style.display = "table-row";
  });

  educationHeadersClicked[i].addEventListener("click", function() {
    hideElement(educationHeadersClicked[i]);
    showElement(educationHeaders[i]);
    clickedHeaders[i].style.display = "none";
    educationHeaders[i].isOpen = false;
  });

  /* User moves mouse over education ellipsis */
  educationEllipses[i].addEventListener("mouseover", function() {
    if (isEllipsisActive(educationAreaStudyTruncated[i]) ||
        isEllipsisActive(educationInstitutionTruncated[i]) ||
        isEllipsisActive(educationAcademicTruncated[i])) {
      growEllipsis(educationEllipses[i]);
    }
    backgroundOffWhite(educationHeaders[i]);
    unTruncate(educationAcademicTruncated[i]);
    unTruncate(educationInstitutionTruncated[i]);
    unTruncate(educationAreaStudyTruncated[i]);
  });

  /* User moves mouse off education ellipsis */
  educationHeaders[i].addEventListener("mouseleave", function() {
    backgroundWhite(educationHeaders[i]);
    shrinkEllipsis(educationEllipses[i]);
    truncate(educationAcademicTruncated[i]);
    truncate(educationAreaStudyTruncated[i]);
    truncate(educationInstitutionTruncated[i]);
  });
}

/* Handles window resizing and adding/removing ellipses based on browser window size */
window.addEventListener('resize', function() {
  for (let i = 0; i < questionEllipses.length; i++) {
    !isEllipsisActive(questionTruncated[i])
    && !isEllipsisActive(questionTruncatedAnalysis[i]) ? hideElement(questionEllipses[i]) : showElement(questionEllipses[i]);
  }
  for (let i = 0; i < educationEllipses.length; i++) {
    !isEllipsisActive(educationAreaStudyTruncated[i]) && !isEllipsisActive(educationInstitutionTruncated[i]) && !isEllipsisActive(educationAcademicTruncated[i]) ? hideElement(educationEllipses[i]) : showElement(educationEllipses[i]);
  }
});

/* HELPER FUNCTIONS */

/* Hide an HTML element */
function hideElement(element) {
  element.classList.add("hide");
}

/* Show an HTML element */
function showElement(element) {
  element.classList.remove("hide");
}

/* Truncate the text in an HTML element */
function truncate(element) {
  element.classList.add("truncation");
  element.classList.remove("truncation-open");
}

/* Un-truncate the text in an HTML element */
function unTruncate(element) {
  element.classList.remove("truncation");
  element.classList.add("truncation-open");
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
}

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
