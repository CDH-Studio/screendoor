const applicantResponseFull = document.getElementsByClassName("applicant-response-full");
const educationItems = document.getElementsByClassName("education-item");
const educationHeaders = document.getElementsByClassName("education-header");
const extractFull = document.getElementsByClassName("extracts-full");
const extractPreviews = document.getElementsByClassName("extract-previews");
const applicantHeader = document.getElementsByClassName("applicant-header");
const hiddenApplicantInfo = document.getElementsByClassName("hidden-applicant-info");
const hiddenEducationInfo = document.getElementsByClassName("hidden-education-info");
const questionPreviews = document.getElementsByClassName("question-preview");
const questionPreviewDivs = document.getElementsByClassName("question-preview-div");
const questionIcons = document.getElementsByClassName("question-icons");
const questionIconDivs = document.getElementsByClassName("question-icon-div");
const questionAnswerFull = document.getElementsByClassName("question-answer-full");
const requirementAbbreviations = document.getElementsByClassName("requirement-abbreviation");
const requirementTips = document.getElementsByClassName("requirement-text");
const shortQuestionTexts = document.getElementsByClassName("short-question-text");
const substantiveClassifications = document.getElementsByClassName("classification-substantive");
const currentClassifications = document.getElementsByClassName("classification-current");
const substantiveClassificationText = document.getElementById("substantive-classification-text");
const currentClassificationText = document.getElementById("current-classification-text");
const expandCollapseEducationButton = document.getElementById("expand-collapse-education");
const expandCollapseQuestionsButton = document.getElementById("expand-collapse-questions");
const expandCollapseApplicantButton = document.getElementById("expand-collapse-applicant");
const expandCollapseEducationButtons = document.getElementsByClassName("expand-collapse-education-item");
const expandCollapseQuestionButtons = document.getElementsByClassName("expand-collapse-questions");

const abbreviations = [];
const descriptions = [];
const substantiveClassificationAbbrev = [];
const currentClassificationAbbrev = [];

const expandAllQuestions = function() {
  for (let i = 0; i < questionPreviews.length; i++) {
    openQuestionFull(i);
    expandCollapseQuestionButtons[i].innerText = "expand_less";
  }
};

const collapseAllQuestions = function() {
  for (let i = 0; i < questionPreviews.length; i++) {
    closeQuestionFull(i);
    expandCollapseQuestionButtons[i].innerText = "expand_more";
  }
};

const expandOrCollapseAllQuestions = function() {
  if (expandCollapseQuestionsButton.innerText == "unfold_more") {
    expandAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_less";
  } else {
    collapseAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_more";
  }
};

const expandAllEducation = function() {
  for (let i = 0; i < educationItems.length; i++) {
    untruncateEducationHeader(i);
    expandCollapseEducationButtons[i].innerText = "expand_less";
    educationItems[i].classList.remove("hoverable");
    hiddenEducationInfo[i].classList.remove("row-closed");
  }
};

const collapseAllEducation = function() {
  for (let i = 0; i < educationItems.length; i++)  {
    expandCollapseEducationButtons[i].innerText = "expand_more";
    truncateEducationHeader(i);
    educationItems[i].classList.add("hoverable");
    hiddenEducationInfo[i].classList.add("row-closed");
  }
};

const expandOrCollapseAllEducation = function() {
  if (expandCollapseEducationButton.innerText == "unfold_more") {
    expandAllEducation();
    expandCollapseEducationButton.innerText = "unfold_less";
  } else {
    collapseAllEducation();
    expandCollapseEducationButton.innerText = "unfold_more";
  }
};

const initializeText = function(i) {
  abbreviations[i] = requirementAbbreviations[i].innerText;
  descriptions[i] = requirementTips[i].value;
};

const expandCurrentClassification = function(i) {
  const currentTextSplit = currentClassificationText.value.split();

  for (let j = 0; j < currentTextSplit.length; j++) {
    currentClassifications[i].innerText += currentTextSplit[j];
  }
};

const contractCurrentClassification = function(i) {
  currentClassifications[i].innerText = currentClassificationAbbrev[i];
};

const contractSubstantiveClassification = function(i) {
  substantiveClassifications[i].innerText = substantiveClassificationAbbrev[i];
};

const expandSubstantiveClassification = function(i) {
  const substantiveTextSplit = substantiveClassificationText.value.split();

  for (let j = 0; j < substantiveTextSplit.length; j++) {
    substantiveClassifications[i].innerText += substantiveTextSplit[j];
  }
};

const expandRequirementTip = function(i) {
  const descriptionChars = descriptions[i].split();

  for (let j = 0; j < descriptionChars.length; j++) {
    requirementAbbreviations[i].innerText += descriptionChars[j];
  }

  requirementAbbreviations[i].addEventListener("transitionend", () => {
    requirementAbbreviations[i].classList.add("no-truncation");
  });
};

const contractRequirementTip = function(i) {
  requirementAbbreviations[i].innerText = abbreviations[i];
  requirementAbbreviations[i].addEventListener("transitionend", () => {
    requirementAbbreviations[i].classList.remove("no-truncation");
  });
};

const untruncateEducationHeader = function(i) {
  for (let j = 1; j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.remove("truncation");
  }
};

const truncateEducationHeader = function(i) {
  for (let j = 1;j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.add("truncation");
  }
};

const expandApplicantHeaders = function(i) {
  if (hiddenApplicantInfo[i].classList.contains("row-closed")) {
    expandCollapseApplicantButton.innerText = "expand_less";
    applicantHeader[i].classList.remove("hoverable");
    hiddenApplicantInfo[i].classList.remove("row-closed");
  } else {
    expandCollapseApplicantButton.innerText = "expand_more";
    applicantHeader[i].classList.add("hoverable");
    hiddenApplicantInfo[i].classList.add("row-closed");
  }
};

const expandEducationHeaders = function(i) {
  if (hiddenEducationInfo[i].classList.contains("row-closed")) {
    untruncateEducationHeader(i);
    expandCollapseEducationButtons[i].innerText = "expand_less";
    educationItems[i].classList.remove("hoverable");
    hiddenEducationInfo[i].classList.remove("row-closed");
  } else {
    truncateEducationHeader(i);
    expandCollapseEducationButtons[i].innerText = "expand_more";
    educationItems[i].classList.add("hoverable");
    hiddenEducationInfo[i].classList.add("row-closed");
  }
};

const openQuestionFull = function(i) {
  questionPreviewDivs[i].classList.remove("hoverable");
  applicantResponseFull[i].classList.add("applicant-response-full-open");
  extractFull[i].classList.add("extracts-full-open");
  questionAnswerFull[i].classList.remove("row-closed");
  questionIconDivs[i].classList.add("hide");

  for (let j = 0; j < extractFull[i].getElementsByTagName("i").length; j++) {
    extractFull[i].getElementsByTagName("i")[j].classList.remove("hide");
  }
};

const closeQuestionFull = function(i) {
  applicantResponseFull[i].classList.remove("applicant-response-full-open");
  extractFull[i].classList.remove("extracts-full-open");
  questionPreviewDivs[i].classList.add("hoverable");
  questionIconDivs[i].classList.remove("hide");
  questionAnswerFull[i].classList.add("row-closed");

  for (let j = 0; j < extractFull[i].getElementsByTagName("i").length; j++) {
    extractFull[i].getElementsByTagName("i")[j].classList.add("hide");
  }
};

const openCloseQuestionFull = function(i) {
  questionAnswerFull[i].classList.contains("row-closed") ? questionAnswerFull[i].classList.remove("row-closed") : questionAnswerFull[i].classList.add("row-closed");
  extractPreviews[i].classList.remove("extract-previews-open");
  questionIcons[i].style.fontSize = "1.8rem";
  if (requirementAbbreviations[i]) {
    requirementAbbreviations[i].classList.remove("hide");
  }
  if (!applicantResponseFull[i].classList.contains("applicant-response-full-open")) {
    expandCollapseQuestionButtons[i].innerText = "expand_less";
    openQuestionFull(i);
  } else {
    closeQuestionFull(i);
    expandCollapseQuestionButtons[i].innerText = "expand_more";
  }
};

window.addEventListener("DOMContentLoaded", () => {
  for (let i = 0; i < substantiveClassifications.length; i++) {
    substantiveClassificationAbbrev[i] = substantiveClassifications[
      i
    ].innerText.toString();

    substantiveClassifications[i].addEventListener("mouseover", () => {
      expandSubstantiveClassification(i);
    });

    substantiveClassifications[i].addEventListener("mouseleave", () => {
      contractSubstantiveClassification(i);
    });
  }

  for (let i = 0; i < currentClassifications.length; i++) {
    currentClassificationAbbrev[i] = currentClassifications[i].innerText.toString();

    currentClassifications[i].addEventListener("mouseover", () => {
      expandCurrentClassification(i);
    });

    currentClassifications[i].addEventListener("mouseleave", () => {
      contractCurrentClassification(i);
    });
  }

  for (let i = 0; i < questionPreviews.length; i++) {
    shortQuestionTexts[i].addEventListener("mouseleave", () => {
      extractPreviews[i].classList.remove("extract-extra-margin");
    });

    questionIconDivs[i].addEventListener("mouseover", () => {
      if (questionIcons[i].innerText == "question_answer") {
        extractPreviews[i].classList.add("extract-previews-open");
        questionIcons[i].style.fontSize = "3rem";
        if (requirementAbbreviations[i]) {
          requirementAbbreviations[i].classList.add("hide");
        }
      }
    });

    questionPreviews[i].addEventListener("mouseleave", () => {
      extractPreviews[i].classList.remove("extract-previews-open");
      questionIcons[i].style.fontSize = "1.9rem";
      if (requirementAbbreviations[i]) {
        requirementAbbreviations[i].classList.remove("hide");
      }
    });

    questionPreviewDivs[i].addEventListener("click", () => {
      openCloseQuestionFull(i);
    });
  }

  for (let i = 0; i < applicantHeader.length; i++) {
    applicantHeader[i].addEventListener("click", () => {
      expandApplicantHeaders(i);
    });
  }

  for (let i = 0; i < educationHeaders.length; i++) {
    educationHeaders[i].addEventListener("click", () => {
      expandEducationHeaders(i);
    });

    educationHeaders[i].addEventListener("mouseover", () => {
      untruncateEducationHeader(i);
    });

    educationHeaders[i].addEventListener("mouseleave", () => {
      if (hiddenEducationInfo[i].classList.contains("row-closed")) {
        truncateEducationHeader(i);
      }
    });
  }

  for (let i = 0; i < requirementAbbreviations.length; i++) {
    initializeText(i);

    requirementAbbreviations[i].addEventListener("mouseover", () => {
      expandRequirementTip(i);
      shortQuestionTexts[i].classList.add("hide");
    });

    requirementAbbreviations[i].addEventListener("mouseleave", () => {
      contractRequirementTip(i);
      shortQuestionTexts[i].classList.remove("hide");
    });
  }

  expandCollapseQuestionsButton.addEventListener("click", () => {
    expandOrCollapseAllQuestions();
  });

  expandCollapseEducationButton.addEventListener("click", () => {
    expandOrCollapseAllEducation();
  });

});
