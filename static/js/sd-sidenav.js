/* Register sidenav and related variables */
let elems = document.querySelectorAll('.sidenav-fixed'),
    instances = M.Sidenav.init(elems, {}/* options */),
    elem = document.querySelector('.sidenav-fixed'),
    instance = M.Sidenav.getInstance(elem);

/* Initialize sidenav to close and load storage */
function initSideNav() {
  /* Open sidebar if saved state is to open */
  if ((JSON.parse(localStorage.getItem('sidenavOpen')) && isWindowFullSize())
      || (JSON.parse(localStorage.getItem('sidenavOpen')) == null)) {
    instance.isOpen = false;
    toggleSidebar();
    localStorage.setItem('sidenavOpen', JSON.stringify(instance.isOpen));
    /* Otherwise re-initialize to closed  */
  } else {
    instance.isOpen = true;
    toggleSidebar();
    localStorage.setItem('sidenavOpen', JSON.stringify(instance.isOpen));
  }
  /* Check padding and fix depending on sidebar closed/open status */
  fixPaddingWidth();
}

/* Listener for page load */
window.addEventListener('DOMContentLoaded', (event) => {
  initSideNav();
});

/* Adjusts navbar and body main padding if window is > 992px width */
function fixPaddingWidth() {
  if (!isWindowFullSize()) {
    removeSidenavPadding();
  } else if (isWindowFullSize() && JSON.parse(localStorage.getItem('sidenavOpen'))) {
    addSidenavPadding();
  }
}

/* Listen for window size changes */
window.addEventListener('resize', function() {
  fixPaddingWidth();
});

/* Listen for menu button clicks */
document.querySelector("#toggle_sidenav").addEventListener('click', function() {
  toggleSidebar();
});

/* Toggle sidebar */
function toggleSidebar() {
  instance.isOpen ? closeSideNav() : openSideNav();
  if (isWindowFullSize()) {
    localStorage.setItem('sidenavOpen', JSON.stringify(instance.isOpen));
  }
}

/* Change CSS to add padding when sidenav opened */
function addSidenavPadding() {
  document.getElementById('base-header').style.paddingLeft = "300";
  document.getElementById('base-main').style.paddingLeft = "300";
}

/* Change CSS to remove padding when sidenav closed */
function removeSidenavPadding() {
  document.getElementById('base-header').style.paddingLeft = "0";
  document.getElementById('base-main').style.paddingLeft = "0";
}

/* Is the window above 992 pixels */
function isWindowFullSize() {
  return window.innerWidth > 992;
}

/* Open sidenav */
function openSideNav() {
  instance.open();
  if (isWindowFullSize()) {
    addSidenavPadding();
  }
}

/* Close sidenav */
function closeSideNav() {
  instance.close();
  if (isWindowFullSize()) {
    removeSidenavPadding();
  }
}
