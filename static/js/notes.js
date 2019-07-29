const addNoteButtons = document.getElementsByClassName("add-note");
const cancelNoteButtons = document.getElementsByClassName("cancel-note");
const noteInputs = document.getElementsByClassName("note-input");
const noteTextArea = document.getElementsByClassName("note-box");
const saveNoteButtons = document.getElementsByClassName("save-note");

const toggleNoteInput = function(i) {
  if (noteTextArea[i].classList.contains("note-box-visible")) {
    noteTextArea[i].classList.remove("note-box-visible");
    addNoteButtons[i].children[0].style.fontSize = "2.1rem";
  } else {
    noteTextArea[i].classList.add("note-box-visible");
    addNoteButtons[i].children[0].style.fontSize = "3rem";
  }
};

const retrieveOpenedQuestion = function() {
  if (localStorage.getItem("questionIndex")) {
    questionPreviewDivs[localStorage.getItem("questionIndex")].click();
    localStorage.removeItem("questionIndex");
  }
  if (localStorage.getItem("boxOpen")) {
    toggleNoteInput(localStorage.getItem("boxOpen"));
    localStorage.removeItem("boxOpen");
  }
};

const saveNote = function(i, answerNum) {
  const noteInputId = "note-input-" + i;
  const noteInputField = document.getElementById(noteInputId);
  const answerId = noteInputField.dataset.parentAnswer;
  const url = "/add_note?noteText=" + encodeURIComponent(noteInputField.value) +
        "&parentAnswerId=" + answerId;
  noteInputField.value = "";

  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      // Reformat the date string to accord with the template default
      const options = {day: "2-digit", year: "numeric",
        month: "long", hour: "numeric", minute: "numeric"};
      const rawDateCreated = new Date(data.noteCreated);
      const dateCreated = rawDateCreated.toLocaleDateString("en-US", options);
      const datestring = dateCreated.replace("AM", "a.m.").replace("PM", "p.m.");

      // Create note DOM element
      const note = document.createElement("div");
      note.classList.add("note");
      note.id = data.noteId;
      note.setAttribute("data-parent-answer", answerId);
      const noteText = document.createElement("span");
      noteText.classList.add("note-text");
      noteText.innerText = data.noteText;
      note.appendChild(noteText);
      note.appendChild(document.createElement("br"));
      const noteAuthor = document.createElement("span");
      noteAuthor.classList.add("note-author", "grey-text");
      noteAuthor.innerText = data.noteAuthor;
      note.appendChild(noteAuthor);
      const noteCreated = document.createElement("span");
      noteCreated.classList.add("note-created", "grey-text");
      noteCreated.innerText = datestring;
      note.appendChild(noteCreated);
      const noteDelete = document.createElement("i");
      noteDelete.classList.add("material-icons", "red-text", "delete-note");
      noteDelete.setAttribute("data-note-id", data.noteId);
      noteDelete.setAttribute("data-answer-num", answerNum);
      noteDelete.innerText = "delete_forever";
      note.appendChild(noteDelete);

      // Add the new element to its holder block
      const notesBlockId = "notes-" + answerNum;
      const notesBlock = document.getElementById(notesBlockId);
      notesBlock.insertBefore(note, notesBlock.childNodes[0]);

      // Add event handler to new remove button
      addRemoveNoteHandlers();
    }).catch((error) => console.error());
  });
};

const addRemoveNoteHandlers = function() {
  const removeNoteButtons = document.getElementsByClassName("delete-note");
  for (let i = 0; i < removeNoteButtons.length; i++) {
    const noteId = removeNoteButtons[i].dataset.noteId;
    const answerNum = removeNoteButtons[i].dataset.answerNum;
    removeNoteButtons[i].addEventListener("click", () => {
      removeNote(noteId, answerNum);
    });
  }
};

const removeNote = function(noteId, answerNum) {
  const url = "/remove_note?noteId=" + noteId;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      // retrieve the block holding the note
      const notesBlockId = "notes-" + answerNum;
      const notesBlock = document.getElementById(notesBlockId);

      // find and remove the note from the block
      const note = document.getElementById(noteId);
      notesBlock.removeChild(note);
    }).catch((error) => console.error());
  });
};

const cancelAddNote = function(i) {
  toggleNoteInput(i);
};

window.addEventListener("DOMContentLoaded", function() {
  retrieveOpenedQuestion();
  getScrollLocation();

  for (let i = 0; i < addNoteButtons.length; i++) {
    i % 2 === 0 ? noteInputs[i].style.backgroundColor = "#ffffff" :
      noteInputs[i].style.backgroundColor = "#fafafa";

    addNoteButtons[i].addEventListener("click", () => {
      toggleNoteInput(i);
    });

    cancelNoteButtons[i].addEventListener("click", () => {
      cancelAddNote(i);
    });

    const answerNum = saveNoteButtons[i].dataset.answerNum;
    saveNoteButtons[i].addEventListener("click", () => {
      saveNote(i, answerNum);
    });
  }

  addRemoveNoteHandlers();
});
