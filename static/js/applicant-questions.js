"use strict";

/* Divs containing an applicant's full response to a question */
var applicantResponseFull = document.getElementsByClassName("applicant-response-full");

/* li elements corresponding to each education header */
var educationItems = document.getElementsByClassName("education-item");

/* Divs containing education header info for each education item */
var educationHeaders = document.getElementsByClassName("education-header");

/* Divs containing all of the extracts corresponding to a particular answer */
var extractFull = document.getElementsByClassName("extracts-full");

/* Divs containing all of the extracts corresponding to a particular answer,
   to be displayed when user hovers over the question-answer icon */
var extractPreviews = document.getElementsByClassName("extract-previews");

/* Div containing applicant icon, id, stream, and classification info  */
var applicantHeader = document.getElementById("applicant-header");

/* Div containing elements with basic applicant info, e.g. priority, language preferences */
var hiddenApplicantInfo = document.getElementById("hidden-applicant-info");

/* Div containing additional education info for each education row */
var hiddenEducationInfo = document.getElementsByClassName("hidden-education-info");

/* li elements containing the header for each question  */
var questionPreviews = document.getElementsByClassName("question-preview");

/* Top-level divs within questionPreviews li elements */
var questionPreviewDivs = document.getElementsByClassName("question-preview-div");

/* Icons on the left side of each question row */
var questionIcons = document.getElementsByClassName("question-icons");

/* Divs which each contain a questionIcon */
var questionIconDivs = document.getElementsByClassName("question-icon-div");

/* Divs containing the full question/answer information for each question,
   revealed when header clicked */
var questionAnswerFull = document.getElementsByClassName("question-answer-full");

/* Divs containing abbreviations for requirements, present in a question header
   if that question has a matching requirement */
var requirementAbbreviations = document.getElementsByClassName("requirement-abbreviation");

/* Hidden input elements containing the full text of each requirement */
var requirementTips = document.getElementsByClassName("requirement-text");

/* Divs containing question preview text that appears on question headers */
var shortQuestionTexts = document.getElementsByClassName("short-question-text");

/* Divs containing substantive classifications of an applicant  */
var substantiveClassifications = document.getElementsByClassName("classification-substantive");

/* Divs containing current classifications of an applicant  */
var currentClassifications = document.getElementsByClassName("classification-current");

/* Spans containing substantive classification text of an applicant  */
var substantiveClassificationText = document.getElementById("substantive-classification-text");

/* Spans containing current classification text of an applicant  */
var currentClassificationText = document.getElementById("current-classification-text");

/* Expand/collapse education icon */
var expandCollapseEducationButton = document.getElementById("expand-collapse-education");

/* Expand/collapse questions icon */
var expandCollapseQuestionsButton = document.getElementById("expand-collapse-questions");

/* Expand/collapse applicant info icon */
var expandCollapseApplicantButton = document.getElementById("expand-collapse-applicant");

/* Icon indicating education row can be expanded/collapsed */
var expandCollapseEducationButtons = document.getElementsByClassName("expand-collapse-education-item");

/* Icon indicating education row can be expanded/collapsed */
var expandCollapseQuestionButtons = document.getElementsByClassName("expand-collapse-questions");

/* Spans corresponding to each stream to which an applicant is applying */
var streams = document.getElementsByClassName("stream");

/* To hold requirement and classification info that will be shown upon hovering */
var abbreviations = [];
var descriptions = [];
var substantiveClassificationAbbrev = [];
var currentClassificationAbbrev = [];

/* Expand all of an applicant's questions */
var expandAllQuestions = function expandAllQuestions() {
  for (var _i = 0; _i < questionPreviews.length; _i++) {
    openQuestionFull(_i);
    expandCollapseQuestionButtons[_i].innerText = "expand_less";
  }
};

/* Collapse all of an applicant's questions */
var collapseAllQuestions = function collapseAllQuestions() {
  for (var _i2 = 0; _i2 < questionPreviews.length; _i2++) {
    closeQuestionFull(_i2);
    expandCollapseQuestionButtons[_i2].innerText = "expand_more";
  }
};

/* Expand or collapse all questions depending on whether they are
   collapsed or expanded */
var expandOrCollapseAllQuestions = function expandOrCollapseAllQuestions() {
  if (expandCollapseQuestionsButton.innerText == "unfold_more") {
    expandAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_less";
  } else {
    collapseAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_more";
  }
};

/* Expand all education rows */
var expandAllEducation = function expandAllEducation() {
  for (var _i3 = 0; _i3 < educationItems.length; _i3++) {
    untruncateEducationHeader(_i3);
    expandCollapseEducationButtons[_i3].innerText = "expand_less";
    educationItems[_i3].classList.remove("hoverable");
    hiddenEducationInfo[_i3].classList.remove("row-closed");
  }
};

/* Collapse all education rows */
var collapseAllEducation = function collapseAllEducation() {
  for (var _i4 = 0; _i4 < educationItems.length; _i4++) {
    expandCollapseEducationButtons[_i4].innerText = "expand_more";
    truncateEducationHeader(_i4);
    educationItems[_i4].classList.add("hoverable");
    hiddenEducationInfo[_i4].classList.add("row-closed");
  }
};

/* Expand or collapse all education rows depending on whether they
   are expanded or collapsed */
var expandOrCollapseAllEducation = function expandOrCollapseAllEducation() {
  if (expandCollapseEducationButton.innerText == "unfold_more") {
    expandAllEducation();
    expandCollapseEducationButton.innerText = "unfold_less";
  } else {
    collapseAllEducation();
    expandCollapseEducationButton.innerText = "unfold_more";
  }
};

/* Initialize values of requirement abbreviations and descriptions */
var initializeText = function initializeText(i) {
  abbreviations[i] = requirementAbbreviations[i].innerText;
  descriptions[i] = requirementTips[i].value;
};

/* Adds classification description one letter at a time upon hover */
var expandCurrentClassification = function expandCurrentClassification(i) {
  var currentTextSplit = currentClassificationText.value.split();

  for (var j = 0; j < currentTextSplit.length; j++) {
    currentClassifications[i].innerText += currentTextSplit[j];
  }
};

/* Adds classification description one letter at a time upon hover */
var expandSubstantiveClassification = function expandSubstantiveClassification(i) {
  var substantiveTextSplit = substantiveClassificationText.value.split();

  for (var j = 0; j < substantiveTextSplit.length; j++) {
    substantiveClassifications[i].innerText += substantiveTextSplit[j];
  }
};

/* Return classification to abbreviation */
var contractCurrentClassification = function contractCurrentClassification(i) {
  currentClassifications[i].innerText = currentClassificationAbbrev[i];
};

/* Return classification to abbreviation */
var contractSubstantiveClassification = function contractSubstantiveClassification(i) {
  substantiveClassifications[i].innerText = substantiveClassificationAbbrev[i];
};

/* Expand requirement one letter at a time */
var expandRequirementTip = function expandRequirementTip(i) {
  var descriptionChars = descriptions[i].split();

  for (var j = 0; j < descriptionChars.length; j++) {
    requirementAbbreviations[i].innerText += descriptionChars[j];
  }

  requirementAbbreviations[i].addEventListener("transitionend", function () {
    requirementAbbreviations[i].classList.add("no-truncation");
  });
};

/* Restore requirement to abbreviation */
var contractRequirementTip = function contractRequirementTip(i) {
  requirementAbbreviations[i].innerText = abbreviations[i];
  requirementAbbreviations[i].addEventListener("transitionend", function () {
    requirementAbbreviations[i].classList.remove("no-truncation");
  });
};

/* Remove ellipses from education header and show the full text */
var untruncateEducationHeader = function untruncateEducationHeader(i) {
  for (var j = 1; j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.remove("truncation");
  }
};

/* Truncate education header text and restore ellipses for overflow */
var truncateEducationHeader = function truncateEducationHeader(i) {
  for (var j = 1; j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.add("truncation");
  }
};

/* Expand basic applicant information section */
var expandApplicantHeaders = function expandApplicantHeaders() {
  if (hiddenApplicantInfo.classList.contains("row-closed")) {
    expandCollapseApplicantButton.innerText = "expand_less";
    applicantHeader.classList.remove("hoverable");
    hiddenApplicantInfo.classList.remove("row-closed");
  } else {
    expandCollapseApplicantButton.innerText = "expand_more";
    applicantHeader.classList.add("hoverable");
    hiddenApplicantInfo.classList.add("row-closed");
  }
};

/* Expand an education row upon clicking */
var expandEducationHeaders = function expandEducationHeaders(i) {
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
var openQuestionFull = function openQuestionFull(i) {
  shortQuestionTexts[i].classList.add("short-question-text-open");
  questionPreviewDivs[i].classList.remove("hoverable");
  applicantResponseFull[i].classList.add("applicant-response-full-open");
  extractFull[i].classList.add("extracts-full-open");
  questionAnswerFull[i].classList.remove("row-closed");
  questionIconDivs[i].classList.add("hide");

  for (var j = 0; j < extractFull[i].getElementsByTagName("i").length; j++) {
    extractFull[i].getElementsByTagName("i")[j].classList.remove("hide");
  }
};

var closeQuestionFull = function closeQuestionFull(i) {
  shortQuestionTexts[i].classList.remove("short-question-text-open");
  applicantResponseFull[i].classList.remove("applicant-response-full-open");
  extractFull[i].classList.remove("extracts-full-open");
  questionPreviewDivs[i].classList.add("hoverable");
  questionIconDivs[i].classList.remove("hide");
  questionAnswerFull[i].classList.add("row-closed");

  for (var j = 0; j < extractFull[i].getElementsByTagName("i").length; j++) {
    extractFull[i].getElementsByTagName("i")[j].classList.add("hide");
  }
};

/* Close a question upon clicking */
var openCloseQuestionFull = function openCloseQuestionFull(i) {
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
window.addEventListener("DOMContentLoaded", function () {
  var _loop = function _loop(_i5) {
    substantiveClassificationAbbrev[_i5] = substantiveClassifications[_i5].innerText.toString();

    substantiveClassifications[_i5].addEventListener("mouseover", function () {
      expandSubstantiveClassification(_i5);
    });

    substantiveClassifications[_i5].addEventListener("mouseleave", function () {
      contractSubstantiveClassification(_i5);
    });
  };

  for (var _i5 = 0; _i5 < substantiveClassifications.length; _i5++) {
    _loop(_i5);
  }

  var _loop2 = function _loop2(_i6) {
    currentClassificationAbbrev[_i6] = currentClassifications[_i6].innerText.toString();

    currentClassifications[_i6].addEventListener("mouseover", function () {
      expandCurrentClassification(_i6);
    });

    currentClassifications[_i6].addEventListener("mouseleave", function () {
      contractCurrentClassification(_i6);
    });
  };

  for (var _i6 = 0; _i6 < currentClassifications.length; _i6++) {
    _loop2(_i6);
  }

  var _loop3 = function _loop3(_i7) {

    shortQuestionTexts[_i7].addEventListener("mouseleave", function () {
      extractPreviews[_i7].classList.remove("extract-extra-margin");
    });

    questionIconDivs[_i7].addEventListener("mouseover", function () {
      if (questionIcons[_i7].innerText == "question_answer") {
        shortQuestionTexts[_i7].classList.add("short-question-text-open");
        extractPreviews[_i7].classList.add("extract-previews-open");
        questionIcons[_i7].style.fontSize = "3rem";
      }
    });

    questionPreviews[_i7].addEventListener("mouseleave", function () {
      if (!applicantResponseFull[_i7].classList.contains("applicant-response-full-open")) {
        shortQuestionTexts[_i7].classList.remove("short-question-text-open");
      }
      extractPreviews[_i7].classList.remove("extract-previews-open");
      questionIcons[_i7].style.fontSize = "1.9rem";
    });

    questionPreviewDivs[_i7].addEventListener("click", function () {
      openCloseQuestionFull(_i7);
    });
  };

  for (var _i7 = 0; _i7 < questionPreviews.length; _i7++) {
    _loop3(_i7);
  }

  applicantHeader.addEventListener("click", function () {
    expandApplicantHeaders(i);
  });

  var _loop4 = function _loop4(_i8) {
    educationHeaders[_i8].addEventListener("click", function () {
      expandEducationHeaders(_i8);
    });

    educationHeaders[_i8].addEventListener("mouseover", function () {
      untruncateEducationHeader(_i8);
    });

    educationHeaders[_i8].addEventListener("mouseleave", function () {
      if (hiddenEducationInfo[_i8].classList.contains("row-closed")) {
        truncateEducationHeader(_i8);
      }
    });
  };

  for (var _i8 = 0; _i8 < educationHeaders.length; _i8++) {
    _loop4(_i8);
  }

  var _loop5 = function _loop5(_i9) {
    initializeText(_i9);

    requirementAbbreviations[_i9].addEventListener("mouseover", function () {
      expandRequirementTip(_i9);
      shortQuestionTexts[_i9].classList.add("hide");
    });

    requirementAbbreviations[_i9].addEventListener("mouseleave", function () {
      contractRequirementTip(_i9);
      shortQuestionTexts[_i9].classList.remove("hide");
    });
  };

  for (var _i9 = 0; _i9 < requirementAbbreviations.length; _i9++) {
    _loop5(_i9);
  }

  expandCollapseQuestionsButton.addEventListener("click", function () {
    expandOrCollapseAllQuestions();
  });

  expandCollapseEducationButton.addEventListener("click", function () {
    expandOrCollapseAllEducation();
  });
});