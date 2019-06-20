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

function hideElement(element) {
  element.classList.add("hide");
}

function showElement(element) {
  element.classList.remove("hide");
}

function truncate(element) {
  element.classList.add("truncation");
  element.classList.remove("truncation-open");
}

function unTruncate(element) {
  element.classList.remove("truncation");
  element.classList.add("truncation-open");
}

function growEllipsis(element) {
  element.classList.remove("ellipsis");
  element.classList.add("ellipsis-larger");
}

function shrinkEllipsis(element) {
  element.classList.remove("ellipsis-larger");
  element.classList.add("ellipsis");
}

function backgroundOffWhite(element) {
  element.style.backgroundColor = "#fbfbfb";
}

function backgroundWhite(element) {
  element.style.backgroundColor = "#ffffff";
}

function isEllipsisActive(e) {
  if (e) {
    return (e.offsetWidth < e.scrollWidth);
  }
}

for (let i = 0; i < questionEllipses.length; i++) {
  questionTruncated[i] = document.getElementById("truncated" + i);
  questionTruncatedAnalysis[i] = document.getElementById("truncated-analysis" + i);
  analysisSubheads[i] = document.getElementById("analysis-subhead" + i);

  if (!isEllipsisActive(questionTruncated[i])) {
    hideElement(questionEllipses[i]);
  }

  questionEllipses[i].addEventListener("mouseover", function() {
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

  questionEllipses[i].addEventListener("mouseleave", function() {
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

for (let i = 0; i < educationEllipses.length; i++) {
  educationAcademicTruncated[i] = document.getElementById("education-academic-truncated" + i);
  educationInstitutionTruncated[i] = document.getElementById("education-institution-truncated" + i);
  educationAreaStudyTruncated[i] = document.getElementById("education-areastudy-truncated" + i);

  if (!isEllipsisActive(educationAreaStudyTruncated[i])
      && !isEllipsisActive(educationInstitutionTruncated[i])
      && !isEllipsisActive(educationAcademicTruncated[i])) {
    hideElement(educationEllipses[i]);
  }

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

  educationEllipses[i].addEventListener("mouseleave", function() {
    backgroundWhite(educationHeaders[i]);
    shrinkEllipsis(educationEllipses[i]);
    truncate(educationAcademicTruncated[i]);
    truncate(educationAreaStudyTruncated[i]);
    truncate(educationInstitutionTruncated[i]);
  });
}

window.addEventListener('resize', function() {
  for (let i = 0; i < questionEllipses.length; i++) {
    !isEllipsisActive ? hideElement(questionEllipses[i]) : showElement(questionEllipses[i]);
  }
  for (let i = 0; i < educationEllipses.length; i++) {
    !isEllipsisActive(educationAreaStudyTruncated[i]) && !isEllipsisActive(educationInstitutionTruncated[i]) && !isEllipsisActive(educationAcademicTruncated[i]) ? hideElement(educationEllipses[i]) : showElement(educationEllipses[i]);
  }
});
