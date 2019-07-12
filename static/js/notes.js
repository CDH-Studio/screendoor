const addNoteButtons = document.getElementsByClassName("add-note");
const noteInputs = document.getElementsByClassName("note-input");
const cancelNoteButtons = document.getElementsByClassName("cancel-note");
const saveNoteButtons = document.getElementsByClassName("save-note");
const addNoteForms = document.getElementsByClassName("note-form");

const deleteNoteForms = document.getElementsByClassName("delete-note-form");
const deleteNoteButtons = document.getElementsByClassName("delete-note");
const noteDeleteAnswerCounters = document.getElementsByClassName("note-delete-answer-counter");

const persistOpenedQuestion = function(i) {
  localStorage.setItem('questionIndex', i);
};

const persistOpenedEditBox = function(i) {
  localStorage.setItem('boxOpen', i);
};

const toggleNoteInput = function(i) {
  noteInputs[i].classList.contains("hide") ? showElements(noteInputs[i]) : hideElements(noteInputs[i]);
};

const retrieveOpenedQuestion = function() {
  if (localStorage.getItem('questionIndex')) {
    questionHeaders[localStorage.getItem('questionIndex')].click();
    localStorage.removeItem('questionIndex');
  }
  if (localStorage.getItem('boxOpen')) {
    toggleNoteInput(localStorage.getItem('boxOpen'));
    localStorage.removeItem('boxOpen');
  }
};

const saveNote = function(i) {
  if (addNoteForms[i].reportValidity()) {
    persistOpenedQuestion(i);
    persistOpenedEditBox(i);
    persistScrollLocation();
    addNoteForms[i].submit();
  }
};

const deleteNote = function(i) {
  persistOpenedQuestion(noteDeleteAnswerCounters[i].value);
  persistScrollLocation();
  deleteNoteForms[i].submit();
};

const cancelAddNote = function(i) {
  hideElements(noteInputs[i]);
};

window.addEventListener('DOMContentLoaded', function() {
  retrieveOpenedQuestion();
  getScrollLocation();
  for (let i = 0; i < addNoteButtons.length; i++) {
    addNoteButtons[i].addEventListener("click", () => { toggleNoteInput(i); });
    cancelNoteButtons[i].addEventListener("click", () => { cancelAddNote(i); });
    saveNoteButtons[i].addEventListener("click", () => { saveNote(i); });
  }
  for (let i = 0; i < deleteNoteButtons.length; i++) {
    deleteNoteButtons[i].addEventListener("click", () => { deleteNote(i); });
  }
});
