/* CONSTANTS AND VARIABLES */

/* Same length */
const extractStringStarts = document.getElementsByClassName("extract-string-index");
const extractStringEnds = document.getElementsByClassName("extract-ending-index");
const extractStringNext = document.getElementsByClassName("extract-next-index");
const extractText = document.getElementsByClassName("extract-string");
const visibleExtracts = document.getElementsByClassName("extract-text");
const extractParentAnswerIds = document.getElementsByClassName("extract-parent-answer-id");
const extractParentAnswerTexts = document.getElementsByClassName("extract-parent-answer");

/* Same length */
const answerComplementaryResponse = document.getElementsByClassName("answer-complementary-response");
const answerComplementaryResponseValue = document.getElementsByClassName("answer-complementary-response-value");


const underlineExtracts = function(extractIndex, direction) {
  visibleExtracts[extractIndex].classList.add("extract-bold");
  if (extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1]) {
    if (extractStringStarts[extractIndex].value == extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1].value) {
      underlineExtracts(direction == "backwards" ? extractIndex - 1 : extractIndex + 1, direction);
    }
  }
};

const clearExtractsUnderline = function(extractIndex, direction) {
  visibleExtracts[extractIndex].classList.remove("extract-bold");
  if (extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1]) {
    if (extractStringStarts[extractIndex].value == extractStringStarts[direction == "backwards" ? extractIndex - 1 : extractIndex + 1].value) {
      clearExtractsUnderline(direction == "backwards" ? extractIndex - 1 : extractIndex + 1, direction);
    }
  }
};

const highlightSentence = function(extractIndex, answerId) {
  underlineExtracts(extractIndex, "backwards");
  underlineExtracts(extractIndex, "forwards");

  for (let i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {

      let startIndex = parseInt(extractStringStarts[extractIndex].value);
      let endIndex = parseInt(extractStringEnds[extractIndex].value);
      const answerText = answerComplementaryResponseValue[i].value;

      const answerBefore = answerText.slice(0, startIndex);
      const answerHighlight = "<span id='answer-highlight' class='answer-highlight'>" + answerText.slice(startIndex, endIndex) + "</span>";
      const answerAfter = answerText.slice(endIndex);

      answerComplementaryResponse[i].innerHTML = answerBefore + answerHighlight + answerAfter;
      document.getElementById('answer-highlight').classList.add("answer-highlighted");
    }
  }
};

const unHighlightSentence = function(extractIndex, answerId) {
  clearExtractsUnderline(extractIndex, "backwards");
  clearExtractsUnderline(extractIndex, "forwards");

  for (let i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {
      answerComplementaryResponse[i].innerHTML = extractParentAnswerTexts[extractIndex].value;
    }
  }
};

const setHighlightListeners = function() {
  for (let i = 0; i < visibleExtracts.length; i++) {
    visibleExtracts[i].addEventListener("mouseover", function() {
      highlightSentence(i, extractParentAnswerIds[i].value);
    });
    visibleExtracts[i].addEventListener("mouseout", function() {
      unHighlightSentence(i, extractParentAnswerIds[i].value);
    });
  }
  for (let i = 0; i < answerComplementaryResponse.length; i++) {
    answerComplementaryResponse[i].answerId = document.getElementsByClassName("answer-id")[i];
  }
};

window.addEventListener('DOMContentLoaded', setHighlightListeners);
