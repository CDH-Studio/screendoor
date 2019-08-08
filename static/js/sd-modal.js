"use strict";

/* Initializes modal pop-ups for deleting positions and uploading applicants */
var modalElements = document.querySelectorAll(".modal");
var modalInstances = M.Modal.init(modalElements, {} /* options */);
var uploadApplicantModal = modalInstances[1];
var uploadModal = modalInstances[2];

var responseModals = document.querySelectorAll(".modal.response-modal") ? document.querySelectorAll(".modal.response-modal") : null;
var responseModalInstances = document.querySelectorAll(".modal.response-modal") ? M.Modal.init(responseModals, {} /* options */) : null;