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

/* Additional Applicant Table Features (Mouse over previews, etc) */

let questionEllipses = document.getElementsByClassName("question-ellipsis");
let questionHeaders = document.getElementsByClassName("question-header");
let questionSubheads = document.getElementsByClassName("question-subhead");
let questionTruncated = [];
let questionTruncatedAnalysis = [];
let analysisSubheads = []
let analysisFull = [];
let analysisPreview = [];
let analysisSpan = document.getElementsByClassName("analysis-preview");

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
  element.style.backgroundColor = "#fbfbfb";
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

/* Initializes and adds listeners for truncated question text */
for (let i = 0; i < questionEllipses.length; i++) {
  questionTruncated[i] = document.getElementById("truncated" + i);
  questionTruncatedAnalysis[i] = document.getElementById("truncated-analysis" + i);
  analysisSubheads[i] = document.getElementById("analysis-subhead" + i);

  analysisFull[i] = document.getElementById("analysis-full" + i).value;
  analysisPreview[i] = document.getElementById("analysis-short" + i).value;

  !isEllipsisActive ? hideElement(questionEllipses[i])
                     : showElement(questionEllipses[i])


  function replaceAnalysisTextWithLinebreak(element, index) {
    element.innerHTML = answersFull[index];
  }

  function restoreAnalysisTextNonLinebreak(element, index) {
    element.innerHTML = answersShort[index];
  }

  /* User moves mouse over a question ellipsis */
  questionEllipses[i].addEventListener("mouseover", function() {
    analysisSpan[i].innerHTML = analysisFull[i];
    backgroundOffWhite(questionHeaders[i]);
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
    analysisSpan[i].innerHTML = analysisPreview[i];
    backgroundWhite(questionHeaders[i]);
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

let educationEllipses = document.getElementsByClassName("education-ellipsis");
let educationHeaders = document.getElementsByClassName("education-header");
let educationAcademicTruncated = [];
let educationInstitutionTruncated = [];
let educationAreaStudyTruncated = [];

/* Initializes and creates listener for education header truncation */
for (let i = 0; i < educationEllipses.length; i++) {
  educationAcademicTruncated[i] = document.getElementById("education-academic-truncated" + i);
  educationInstitutionTruncated[i] = document.getElementById("education-institution-truncated" + i);
  educationAreaStudyTruncated[i] = document.getElementById("education-areastudy-truncated" + i);

  if (!isEllipsisActive(educationAreaStudyTruncated[i])
      && !isEllipsisActive(educationInstitutionTruncated[i])
      && !isEllipsisActive(educationAcademicTruncated[i])) {
    hideElement(educationEllipses[i]);
  }

  /* User moves mouse over education ellipsis */
  educationEllipses[i].addEventListener("mouseover", function() {
    if (isEllipsisActive(educationAreaStudyTruncated[i])
        || isEllipsisActive(educationInstitutionTruncated[i])
        || isEllipsisActive(educationAcademicTruncated[i])) {
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
    !isEllipsisActive ? hideElement(questionEllipses[i]) : showElement(questionEllipses[i]);
  }
  for (let i = 0; i < educationEllipses.length; i++) {
    !isEllipsisActive(educationAreaStudyTruncated[i]) && !isEllipsisActive(educationInstitutionTruncated[i]) && !isEllipsisActive(educationAcademicTruncated[i]) ? hideElement(educationEllipses[i]) : showElement(educationEllipses[i]);
  }
});
