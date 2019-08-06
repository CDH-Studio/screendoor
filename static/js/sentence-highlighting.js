"use strict";

/* CONSTANTS AND VARIABLES */

/* Same length */
var extractStringStarts = document.getElementsByClassName("extract-string-index");
var extractStringEnds = document.getElementsByClassName("extract-ending-index");
var extractStringNext = document.getElementsByClassName("extract-next-index");
var extractText = document.getElementsByClassName("extract-string");
var visibleExtracts = document.getElementsByClassName("extract-text");
var extractDivs = document.getElementsByClassName("extract-full");
var extractParentAnswerIds = document.getElementsByClassName("extract-parent-answer-id");
var extractParentAnswerTexts = document.getElementsByClassName("extract-parent-answer");

/* Same length */
var answerComplementaryResponse = document.getElementsByClassName("answer-complementary-response");
var answerComplementaryResponseValue = document.getElementsByClassName("answer-complementary-response-value");

var underlineExtracts = function underlineExtracts(extractIndex, direction) {
  visibleExtracts[extractIndex].classList.add("extract-bold");
  // if (extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1]) {
  //   if (extractStringStarts[extractIndex].value == extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1].value) {
  //     underlineExtracts(direction == "backwards" ? extractIndex - 1 : extractIndex + 1, direction);
  //   }
  // }
};

var clearExtractsUnderline = function clearExtractsUnderline(extractIndex, direction) {
  visibleExtracts[extractIndex].classList.remove("extract-bold");
  // if (extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1]) {
  //   if (extractStringStarts[extractIndex].value == extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1].value) {
  //     clearExtractsUnderline(direction == "backwards" ? extractIndex - 1 : extractIndex + 1, direction);
  //   }
  // }
};

var highlightSentence = function highlightSentence(extractIndex, answerId) {
  underlineExtracts(extractIndex, "backwards");
  underlineExtracts(extractIndex, "forwards");

  for (var i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {

      var startIndex = parseInt(extractStringStarts[extractIndex].value);
      var endIndex = parseInt(extractStringEnds[extractIndex].value);
      var answerText = answerComplementaryResponseValue[i].value;

      var answerBefore = answerText.slice(0, startIndex);
      var answerHighlight = "<span id='answer-highlight' class='answer-highlight'>" + answerText.slice(startIndex, endIndex) + "</span>";
      var answerAfter = answerText.slice(endIndex);

      answerComplementaryResponse[i].innerHTML = answerBefore + answerHighlight + answerAfter;
      document.getElementById('answer-highlight').classList.add("answer-highlighted");
    }
  }
};

var unHighlightSentence = function unHighlightSentence(extractIndex, answerId) {
  clearExtractsUnderline(extractIndex, "backwards");
  clearExtractsUnderline(extractIndex, "forwards");

  for (var i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {
      answerComplementaryResponse[i].innerHTML = extractParentAnswerTexts[extractIndex].value;
    }
  }
};

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

window.addEventListener('DOMContentLoaded', setHighlightListeners);