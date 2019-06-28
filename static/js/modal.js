/* Initializes modal pop-ups for deleting positions and uploading applicants */
const modalElements = document.querySelectorAll('.modal');
const modalInstances = M.Modal.init(modalElements, {} /* options */ );
const uploadModal = modalInstances[2];
