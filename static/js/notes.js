"use strict";

var addNoteButtons = document.getElementsByClassName("add-note");
var cancelNoteButtons = document.getElementsByClassName("cancel-note");
var noteInputs = document.getElementsByClassName("note-input");
var noteTextArea = document.getElementsByClassName("note-box");
var saveNoteButtons = document.getElementsByClassName("save-note");

var toggleNoteInput = function toggleNoteInput(i) {
  if (noteTextArea[i].classList.contains('note-box-visible')) {
    noteTextArea[i].classList.remove('note-box-visible');
    addNoteButtons[i].children[0].style.fontSize = '2.1rem';
  } else {
    noteTextArea[i].classList.add('note-box-visible');
    addNoteButtons[i].children[0].style.fontSize = '3rem';
  }
};

var retrieveOpenedQuestion = function retrieveOpenedQuestion() {
  if (localStorage.getItem("questionIndex")) {
    questionPreviewDivs[localStorage.getItem("questionIndex")].click();
    localStorage.removeItem("questionIndex");
  }
  if (localStorage.getItem("boxOpen")) {
    toggleNoteInput(localStorage.getItem("boxOpen"));
    localStorage.removeItem("boxOpen");
  }
};

var saveNote = function saveNote(i, answerNum) {
  var noteInputId = "note-input-" + i;
  var noteInputField = document.getElementById(noteInputId);
  var answerId = noteInputField.dataset.parentAnswer;
  var url = "/add_note?noteText=" + encodeURIComponent(noteInputField.value) + "&parentAnswerId=" + answerId;
  noteInputField.value = "";

  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      // Reformat the date string to accord with the template default
      var options = { day: "2-digit", year: "numeric",
        month: "long", hour: "numeric", minute: "numeric" };
      var rawDateCreated = new Date(data.noteCreated);
      var dateCreated = rawDateCreated.toLocaleDateString("en-US", options);
      var datestring = dateCreated.replace("AM", "a.m.").replace("PM", "p.m.");

      // Create note DOM element
      var note = document.createElement("div");
      note.classList.add("note");
      note.id = data.noteId;
      note.setAttribute("data-parent-answer", answerId);
      var noteText = document.createElement("span");
      noteText.classList.add("note-text");
      noteText.innerText = data.noteText;
      note.appendChild(noteText);
      note.appendChild(document.createElement("br"));
      var noteAuthor = document.createElement("span");
      noteAuthor.classList.add("note-author", "grey-text");
      noteAuthor.innerText = data.noteAuthor;
      note.appendChild(noteAuthor);
      var noteCreated = document.createElement("span");
      noteCreated.classList.add("note-created", "grey-text");
      noteCreated.innerText = datestring;
      note.appendChild(noteCreated);
      var noteDelete = document.createElement("i");
      noteDelete.classList.add("material-icons", "red-text", "delete-note");
      noteDelete.setAttribute("data-note-id", data.noteId);
      noteDelete.setAttribute("data-answer-num", answerNum);
      noteDelete.innerText = "delete_forever";
      note.appendChild(noteDelete);

      // Add the new element to its holder block
      var notesBlockId = "notes-" + answerNum;
      var notesBlock = document.getElementById(notesBlockId);
      notesBlock.insertBefore(note, notesBlock.childNodes[0]);

      // Add event handler to new remove button
      addRemoveNoteHandlers();
    }).catch(function (error) {
      return console.error();
    });
  });
};

var addRemoveNoteHandlers = function addRemoveNoteHandlers() {
  var removeNoteButtons = document.getElementsByClassName("delete-note");

  var _loop = function _loop(i) {
    var noteId = removeNoteButtons[i].dataset.noteId;
    var answerNum = removeNoteButtons[i].dataset.answerNum;
    removeNoteButtons[i].addEventListener("click", function () {
      removeNote(noteId, answerNum);
    });
  };

  for (var i = 0; i < removeNoteButtons.length; i++) {
    _loop(i);
  }
};

var removeNote = function removeNote(noteId, answerNum) {
  var url = "/remove_note?noteId=" + noteId;
  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      // retrieve the block holding the note
      var notesBlockId = "notes-" + answerNum;
      var notesBlock = document.getElementById(notesBlockId);

      // find and remove the note from the block
      var note = document.getElementById(noteId);
      notesBlock.removeChild(note);
    }).catch(function (error) {
      return console.error();
    });
  });
};

var cancelAddNote = function cancelAddNote(i) {
  toggleNoteInput(i);
};

window.addEventListener("DOMContentLoaded", function () {
  retrieveOpenedQuestion();
  getScrollLocation();

  var _loop2 = function _loop2(i) {
    i % 2 === 0 ? noteInputs[i].style.backgroundColor = "#ffffff" : noteInputs[i].style.backgroundColor = "#fafafa";

    addNoteButtons[i].addEventListener("click", function () {
      toggleNoteInput(i);
    });

    cancelNoteButtons[i].addEventListener("click", function () {
      cancelAddNote(i);
    });

    var answerNum = saveNoteButtons[i].dataset.answerNum;
    saveNoteButtons[i].addEventListener("click", function () {
      saveNote(i, answerNum);
    });
  };

  for (var i = 0; i < addNoteButtons.length; i++) {
    _loop2(i);
  }

  addRemoveNoteHandlers();
});