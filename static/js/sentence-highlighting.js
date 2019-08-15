"use strict";

/* Hidden inputs containing extract string starting indexes */
var extractStringStarts = document.getElementsByClassName("extract-string-index");

/* Hidden inputs containing extract string ending indexes */
var extractStringEnds = document.getElementsByClassName("extract-ending-index");

/* Spans containing the text of each individual extract */
var visibleExtracts = document.getElementsByClassName("extract-text");

/* Divs containing a span containing an individual extract */
var extractDivs = document.getElementsByClassName("extract-full");

/* Hidden inputs containing the id of the parent answer of an extract */
var extractParentAnswerIds = document.getElementsByClassName("extract-parent-answer-id");

/* Hidden inputs containing the parent answer text of the extract */
var extractParentAnswerTexts = document.getElementsByClassName("extract-parent-answer");

/* Spans containing applicant complementary response text */
var answerComplementaryResponse = document.getElementsByClassName("answer-complementary-response");

/* Hidden inputs containing applicant complementary response text */
var answerComplementaryResponseValue = document.getElementsByClassName("answer-complementary-response-value");

/* Underline the extract over which the user is hovering  */
var underlineExtracts = function underlineExtracts(extractIndex) {
  visibleExtracts[extractIndex].classList.add("extract-bold");
};

/* Remove underline when user moves mouse away  */
var clearExtractsUnderline = function clearExtractsUnderline(extractIndex) {
  visibleExtracts[extractIndex].classList.remove("extract-bold");
};

/* Highlight the sentence corresponding to extract user is hovering */
var highlightSentence = function highlightSentence(extractIndex, answerId) {
  underlineExtracts(extractIndex);

  for (var i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {

      var startIndex = parseInt(extractStringStarts[extractIndex].value);
      var endIndex = parseInt(extractStringEnds[extractIndex].value);
      var answerText = answerComplementaryResponseValue[i].value;

      var answerBefore = answerText.slice(0, startIndex);
      var answerHighlight = "<span id='answer-highlight' class='answer-highlight'>" + answerText.slice(startIndex, endIndex) + "</span>";
      var answerAfter = answerText.slice(endIndex);

      answerComplementaryResponse[i].innerHTML = answerBefore + answerHighlight + answerAfter;
      document.getElementById("answer-highlight").classList.add("answer-highlighted");
    }
  }
};

/* Remove highlight from sentence */
var unHighlightSentence = function unHighlightSentence(extractIndex, answerId) {
  clearExtractsUnderline(extractIndex);

  for (var i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {
      answerComplementaryResponse[i].innerHTML = extractParentAnswerTexts[extractIndex].value;
    }
  }
};

/* Initialize listeners for hovering over extracts */
var setHighlightListeners = function setHighlightListeners() {
  var _loop = function _loop(i) {
    extractDivs[i].addEventListener("mouseover", function () {
      highlightSentence(i, extractParentAnswerIds[i].value);
    });
    extractDivs[i].addEventListener("mouseout", function () {
      unHighlightSentence(i, extractParentAnswerIds[i].value);
    });
  };

  for (var i = 0; i < visibleExtracts.length; i++) {
    _loop(i);
  }
  for (var i = 0; i < answerComplementaryResponse.length; i++) {
    answerComplementaryResponse[i].answerId = document.getElementsByClassName("answer-id")[i];
  }
};

window.addEventListener("DOMContentLoaded", setHighlightListeners);