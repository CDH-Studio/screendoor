"use strict";

/* All modal divs on a page */
var modalElements = document.querySelectorAll(".modal");

/* Array of the modal instances */
var modalInstances = M.Modal.init(modalElements, {} /* options */);

/* Upload applicant modal */
var uploadApplicantModal = modalInstances[1];

/* Applicants processing modal  */
var uploadModal = modalInstances[2];

var responseModals = document.querySelectorAll(".modal.response-modal") ? document.querySelectorAll(".modal.response-modal") : null;
var responseModalInstances = document.querySelectorAll(".modal.response-modal") ? M.Modal.init(responseModals, {} /* options */) : null;