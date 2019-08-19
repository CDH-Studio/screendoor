/* Divs containing an applicant's full response to a question */
const applicantResponseFull = document.getElementsByClassName("applicant-response-full");

/* li elements corresponding to each education header */
const educationItems = document.getElementsByClassName("education-item");

/* Divs containing education header info for each education item */
const educationHeaders = document.getElementsByClassName("education-header");

/* Divs containing all of the extracts corresponding to a particular answer */
const extractFull = document.getElementsByClassName("extracts-full");

/* Divs containing all of the extracts corresponding to a particular answer,
   to be displayed when user hovers over the question-answer icon */
const extractPreviews = document.getElementsByClassName("extract-previews");

/* Div containing applicant icon, id, stream, and classification info  */
const applicantHeader = document.getElementById("applicant-header");

/* Div containing elements with basic applicant info, e.g. priority, language preferences */
const hiddenApplicantInfo = document.getElementsByClassName("hidden-applicant-info");

/* Div containing additional education info for each education row */
const hiddenEducationInfo = document.getElementsByClassName("hidden-education-info");

/* li elements containing the header for each question  */
const questionPreviews = document.getElementsByClassName("question-preview");

/* Top-level divs within questionPreviews li elements */
const questionPreviewDivs = document.getElementsByClassName("question-preview-div");

/* Icons on the left side of each question row */
const questionIcons = document.getElementsByClassName("question-icons");

/* Divs which each contain a questionIcon */
const questionIconDivs = document.getElementsByClassName("question-icon-div");

/* Divs containing the full question/answer information for each question,
   revealed when header clicked */
const questionAnswerFull = document.getElementsByClassName("question-answer-full");

/* Divs containing abbreviations for requirements, present in a question header
   if that question has a matching requirement */
const requirementAbbreviations = document.getElementsByClassName("requirement-abbreviation");

/* Hidden input elements containing the full text of each requirement */
const requirementTips = document.getElementsByClassName("requirement-text");

/* Divs containing question preview text that appears on question headers */
const shortQuestionTexts = document.getElementsByClassName("short-question-text");

/* Divs containing substantive classifications of an applicant  */
const substantiveClassifications = document.getElementsByClassName("classification-substantive");

/* Divs containing current classifications of an applicant  */
const currentClassifications = document.getElementsByClassName("classification-current");

/* Spans containing substantive classification text of an applicant  */
const substantiveClassificationText = document.getElementById("substantive-classification-text");

/* Spans containing current classification text of an applicant  */
const currentClassificationText = document.getElementById("current-classification-text");

/* Expand/collapse education icon */
const expandCollapseEducationButton = document.getElementById("expand-collapse-education");

/* Expand/collapse questions icon */
const expandCollapseQuestionsButton = document.getElementById("expand-collapse-questions");

/* Expand/collapse applicant info icon */
const expandCollapseApplicantButton = document.getElementById("expand-collapse-applicant");

/* Icon indicating education row can be expanded/collapsed */
const expandCollapseEducationButtons = document.getElementsByClassName("expand-collapse-education-item");

/* Icon indicating education row can be expanded/collapsed */
const expandCollapseQuestionButtons = document.getElementsByClassName("expand-collapse-questions");

/* Spans corresponding to each stream to which an applicant is applying */
const streams = document.getElementsByClassName("stream");

/* To hold requirement and classification info that will be shown upon hovering */
const abbreviations = [];
const descriptions = [];
const substantiveClassificationAbbrev = [];
const currentClassificationAbbrev = [];

/* Expand all of an applicant's questions */
const expandAllQuestions = function() {
  for (let i = 0; i < questionPreviews.length; i++) {
    openQuestionFull(i);
    expandCollapseQuestionButtons[i].innerText = "expand_less";
  }
};

/* Collapse all of an applicant's questions */
const collapseAllQuestions = function() {
  for (let i = 0; i < questionPreviews.length; i++) {
    closeQuestionFull(i);
    expandCollapseQuestionButtons[i].innerText = "expand_more";
  }
};


/* Expand or collapse all questions depending on whether they are
   collapsed or expanded */
const expandOrCollapseAllQuestions = function() {
  if (expandCollapseQuestionsButton.innerText == "unfold_more") {
    expandAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_less";
  } else {
    collapseAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_more";
  }
};

/* Expand all education rows */
const expandAllEducation = function() {
  for (let i = 0; i < educationItems.length; i++) {
    untruncateEducationHeader(i);
    expandCollapseEducationButtons[i].innerText = "expand_less";
    educationItems[i].classList.remove("hoverable");
    hiddenEducationInfo[i].classList.remove("row-closed");
  }
};

/* Collapse all education rows */
const collapseAllEducation = function() {
  for (let i = 0; i < educationItems.length; i++)  {
    expandCollapseEducationButtons[i].innerText = "expand_more";
    truncateEducationHeader(i);
    educationItems[i].classList.add("hoverable");
    hiddenEducationInfo[i].classList.add("row-closed");
  }
};

/* Expand or collapse all education rows depending on whether they
   are expanded or collapsed */
const expandOrCollapseAllEducation = function() {
  if (expandCollapseEducationButton.innerText == "unfold_more") {
    expandAllEducation();
    expandCollapseEducationButton.innerText = "unfold_less";
  } else {
    collapseAllEducation();
    expandCollapseEducationButton.innerText = "unfold_more";
  }
};

/* Initialize values of requirement abbreviations and descriptions */
const initializeText = function(i) {
  abbreviations[i] = requirementAbbreviations[i].innerText;
  descriptions[i] = requirementTips[i].value;
};

/* Adds classification description one letter at a time upon hover */
const expandCurrentClassification = function(i) {
  const currentTextSplit = currentClassificationText.value.split();

  for (let j = 0; j < currentTextSplit.length; j++) {
    currentClassifications[i].innerText += currentTextSplit[j];
  }
};

/* Adds classification description one letter at a time upon hover */
const expandSubstantiveClassification = function(i) {
  const substantiveTextSplit = substantiveClassificationText.value.split();

  for (let j = 0; j < substantiveTextSplit.length; j++) {
    substantiveClassifications[i].innerText += substantiveTextSplit[j];
  }
};

/* Return classification to abbreviation */
const contractCurrentClassification = function(i) {
  currentClassifications[i].innerText = currentClassificationAbbrev[i];
};

/* Return classification to abbreviation */
const contractSubstantiveClassification = function(i) {
  substantiveClassifications[i].innerText = substantiveClassificationAbbrev[i];
};

/* Expand requirement one letter at a time */
const expandRequirementTip = function(i) {
  const descriptionChars = descriptions[i].split();

  for (let j = 0; j < descriptionChars.length; j++) {
    requirementAbbreviations[i].innerText += descriptionChars[j];
  }

  requirementAbbreviations[i].addEventListener("transitionend", () => {
    requirementAbbreviations[i].classList.add("no-truncation");
  });
};

/* Restore requirement to abbreviation */
const contractRequirementTip = function(i) {
  requirementAbbreviations[i].innerText = abbreviations[i];
  requirementAbbreviations[i].addEventListener("transitionend", () => {
    requirementAbbreviations[i].classList.remove("no-truncation");
  });
};

/* Remove ellipses from education header and show the full text */
const untruncateEducationHeader = function(i) {
  for (let j = 1; j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.remove("truncation");
  }
};

/* Truncate education header text and restore ellipses for overflow */
const truncateEducationHeader = function(i) {
  for (let j = 1;j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.add("truncation");
  }
};

/* Expand basic applicant information section */
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

/* Expand an education row upon clicking */
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

/* Expand a question upon clicking */
const openQuestionFull = function(i) {
  shortQuestionTexts[i].classList.add("short-question-text-open");
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
  shortQuestionTexts[i].classList.remove("short-question-text-open");
  applicantResponseFull[i].classList.remove("applicant-response-full-open");
  extractFull[i].classList.remove("extracts-full-open");
  questionPreviewDivs[i].classList.add("hoverable");
  questionIconDivs[i].classList.remove("hide");
  questionAnswerFull[i].classList.add("row-closed");

  for (let j = 0; j < extractFull[i].getElementsByTagName("i").length; j++) {
    extractFull[i].getElementsByTagName("i")[j].classList.add("hide");
  }
};

/* Close a question upon clicking */
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

/* Initialize listeners */
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
        shortQuestionTexts[i].classList.add("short-question-text-open");
        extractPreviews[i].classList.add("extract-previews-open");
        questionIcons[i].style.fontSize = "3rem";
      }
    });

    questionPreviews[i].addEventListener("mouseleave", () => {
      if (!applicantResponseFull[i].classList.contains("applicant-response-full-open")) {
        shortQuestionTexts[i].classList.remove("short-question-text-open");
      }
      extractPreviews[i].classList.remove("extract-previews-open");
      questionIcons[i].style.fontSize = "1.9rem";
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
