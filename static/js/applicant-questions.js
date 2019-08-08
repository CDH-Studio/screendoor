"use strict";

var applicantResponseFull = document.getElementsByClassName("applicant-response-full");
var educationItems = document.getElementsByClassName("education-item");
var educationHeaders = document.getElementsByClassName("education-header");
var extractFull = document.getElementsByClassName("extracts-full");
var extractPreviews = document.getElementsByClassName("extract-previews");
var applicantHeader = document.getElementsByClassName("applicant-header");
var hiddenApplicantInfo = document.getElementsByClassName("hidden-applicant-info");
var hiddenEducationInfo = document.getElementsByClassName("hidden-education-info");
var questionPreviews = document.getElementsByClassName("question-preview");
var questionPreviewDivs = document.getElementsByClassName("question-preview-div");
var questionIcons = document.getElementsByClassName("question-icons");
var questionIconDivs = document.getElementsByClassName("question-icon-div");
var questionAnswerFull = document.getElementsByClassName("question-answer-full");
var requirementAbbreviations = document.getElementsByClassName("requirement-abbreviation");
var requirementTips = document.getElementsByClassName("requirement-text");
var shortQuestionTexts = document.getElementsByClassName("short-question-text");
var substantiveClassifications = document.getElementsByClassName("classification-substantive");
var currentClassifications = document.getElementsByClassName("classification-current");
var substantiveClassificationText = document.getElementById("substantive-classification-text");
var currentClassificationText = document.getElementById("current-classification-text");
var expandCollapseEducationButton = document.getElementById("expand-collapse-education");
var expandCollapseQuestionsButton = document.getElementById("expand-collapse-questions");
var expandCollapseApplicantButton = document.getElementById("expand-collapse-applicant");
var expandCollapseEducationButtons = document.getElementsByClassName("expand-collapse-education-item");
var expandCollapseQuestionButtons = document.getElementsByClassName("expand-collapse-questions");

var streams = document.getElementsByClassName("stream");

var abbreviations = [];
var descriptions = [];
var substantiveClassificationAbbrev = [];
var currentClassificationAbbrev = [];

var expandAllQuestions = function expandAllQuestions() {
  for (var i = 0; i < questionPreviews.length; i++) {
    openQuestionFull(i);
    expandCollapseQuestionButtons[i].innerText = "expand_less";
  }
};

var collapseAllQuestions = function collapseAllQuestions() {
  for (var i = 0; i < questionPreviews.length; i++) {
    closeQuestionFull(i);
    expandCollapseQuestionButtons[i].innerText = "expand_more";
  }
};

var expandOrCollapseAllQuestions = function expandOrCollapseAllQuestions() {
  if (expandCollapseQuestionsButton.innerText == "unfold_more") {
    expandAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_less";
  } else {
    collapseAllQuestions();
    expandCollapseQuestionsButton.innerText = "unfold_more";
  }
};

var expandAllEducation = function expandAllEducation() {
  for (var i = 0; i < educationItems.length; i++) {
    untruncateEducationHeader(i);
    expandCollapseEducationButtons[i].innerText = "expand_less";
    educationItems[i].classList.remove("hoverable");
    hiddenEducationInfo[i].classList.remove("row-closed");
  }
};

var collapseAllEducation = function collapseAllEducation() {
  for (var i = 0; i < educationItems.length; i++) {
    expandCollapseEducationButtons[i].innerText = "expand_more";
    truncateEducationHeader(i);
    educationItems[i].classList.add("hoverable");
    hiddenEducationInfo[i].classList.add("row-closed");
  }
};

var expandOrCollapseAllEducation = function expandOrCollapseAllEducation() {
  if (expandCollapseEducationButton.innerText == "unfold_more") {
    expandAllEducation();
    expandCollapseEducationButton.innerText = "unfold_less";
  } else {
    collapseAllEducation();
    expandCollapseEducationButton.innerText = "unfold_more";
  }
};

var initializeText = function initializeText(i) {
  abbreviations[i] = requirementAbbreviations[i].innerText;
  descriptions[i] = requirementTips[i].value;
};

var expandStream = function expandStream() {
  document.getElementById("stream-div").classList.remove("truncation");
};

var collapseStream = function collapseStream() {
  // document.getElementById("stream-div").classList.add("truncation");
};

var expandCurrentClassification = function expandCurrentClassification(i) {
  var currentTextSplit = currentClassificationText.value.split();

  for (var j = 0; j < currentTextSplit.length; j++) {
    currentClassifications[i].innerText += currentTextSplit[j];
  }
};

var contractCurrentClassification = function contractCurrentClassification(i) {
  currentClassifications[i].innerText = currentClassificationAbbrev[i];
};

var contractSubstantiveClassification = function contractSubstantiveClassification(i) {
  substantiveClassifications[i].innerText = substantiveClassificationAbbrev[i];
};

var expandSubstantiveClassification = function expandSubstantiveClassification(i) {
  var substantiveTextSplit = substantiveClassificationText.value.split();

  for (var j = 0; j < substantiveTextSplit.length; j++) {
    substantiveClassifications[i].innerText += substantiveTextSplit[j];
  }
};

var expandRequirementTip = function expandRequirementTip(i) {
  var descriptionChars = descriptions[i].split();

  for (var j = 0; j < descriptionChars.length; j++) {
    requirementAbbreviations[i].innerText += descriptionChars[j];
  }

  requirementAbbreviations[i].addEventListener("transitionend", function () {
    requirementAbbreviations[i].classList.add("no-truncation");
  });
};

var contractRequirementTip = function contractRequirementTip(i) {
  requirementAbbreviations[i].innerText = abbreviations[i];
  requirementAbbreviations[i].addEventListener("transitionend", function () {
    requirementAbbreviations[i].classList.remove("no-truncation");
  });
};

var untruncateEducationHeader = function untruncateEducationHeader(i) {
  for (var j = 1; j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.remove("truncation");
  }
};

var truncateEducationHeader = function truncateEducationHeader(i) {
  for (var j = 1; j < educationHeaders[i].getElementsByClassName("cell-header").length; j++) {
    educationHeaders[i].getElementsByClassName("cell-header")[j].classList.add("truncation");
  }
};

var expandApplicantHeaders = function expandApplicantHeaders(i) {
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

window.addEventListener("DOMContentLoaded", function () {
  var _loop = function _loop(i) {
    streams[i].addEventListener("mouseover", function () {
      expandStream(i);
    });

    streams[i].addEventListener("mouseleave", function () {
      collapseStream(i);
    });
  };

  for (var i = 0; i < streams.length; i++) {
    _loop(i);
  }

  var _loop2 = function _loop2(i) {
    substantiveClassificationAbbrev[i] = substantiveClassifications[i].innerText.toString();

    substantiveClassifications[i].addEventListener("mouseover", function () {
      expandSubstantiveClassification(i);
    });

    substantiveClassifications[i].addEventListener("mouseleave", function () {
      contractSubstantiveClassification(i);
    });
  };

  for (var i = 0; i < substantiveClassifications.length; i++) {
    _loop2(i);
  }

  var _loop3 = function _loop3(i) {
    currentClassificationAbbrev[i] = currentClassifications[i].innerText.toString();

    currentClassifications[i].addEventListener("mouseover", function () {
      expandCurrentClassification(i);
    });

    currentClassifications[i].addEventListener("mouseleave", function () {
      contractCurrentClassification(i);
    });
  };

  for (var i = 0; i < currentClassifications.length; i++) {
    _loop3(i);
  }

  var _loop4 = function _loop4(i) {

    shortQuestionTexts[i].addEventListener("mouseleave", function () {
      extractPreviews[i].classList.remove("extract-extra-margin");
    });

    questionIconDivs[i].addEventListener("mouseover", function () {
      if (questionIcons[i].innerText == "question_answer") {
        shortQuestionTexts[i].classList.add("short-question-text-open");
        extractPreviews[i].classList.add("extract-previews-open");
        questionIcons[i].style.fontSize = "3rem";
      }
    });

    questionPreviews[i].addEventListener("mouseleave", function () {
      if (!applicantResponseFull[i].classList.contains("applicant-response-full-open")) {
        shortQuestionTexts[i].classList.remove("short-question-text-open");
      }
      extractPreviews[i].classList.remove("extract-previews-open");
      questionIcons[i].style.fontSize = "1.9rem";
    });

    questionPreviewDivs[i].addEventListener("click", function () {
      openCloseQuestionFull(i);
    });
  };

  for (var i = 0; i < questionPreviews.length; i++) {
    _loop4(i);
  }

  var _loop5 = function _loop5(i) {
    applicantHeader[i].addEventListener("click", function () {
      expandApplicantHeaders(i);
    });
  };

  for (var i = 0; i < applicantHeader.length; i++) {
    _loop5(i);
  }

  var _loop6 = function _loop6(i) {
    educationHeaders[i].addEventListener("click", function () {
      expandEducationHeaders(i);
    });

    educationHeaders[i].addEventListener("mouseover", function () {
      untruncateEducationHeader(i);
    });

    educationHeaders[i].addEventListener("mouseleave", function () {
      if (hiddenEducationInfo[i].classList.contains("row-closed")) {
        truncateEducationHeader(i);
      }
    });
  };

  for (var i = 0; i < educationHeaders.length; i++) {
    _loop6(i);
  }

  var _loop7 = function _loop7(i) {
    initializeText(i);

    requirementAbbreviations[i].addEventListener("mouseover", function () {
      expandRequirementTip(i);
      shortQuestionTexts[i].classList.add("hide");
    });

    requirementAbbreviations[i].addEventListener("mouseleave", function () {
      contractRequirementTip(i);
      shortQuestionTexts[i].classList.remove("hide");
    });
  };

  for (var i = 0; i < requirementAbbreviations.length; i++) {
    _loop7(i);
  }

  expandCollapseQuestionsButton.addEventListener("click", function () {
    expandOrCollapseAllQuestions();
  });

  expandCollapseEducationButton.addEventListener("click", function () {
    expandOrCollapseAllEducation();
  });
});