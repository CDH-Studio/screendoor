"use strict";

/* Sidenav instance */
var elems = document.querySelectorAll(".sidenav-fixed"),
    instances = M.Sidenav.init(elems, {} /* options */),
    elem = document.querySelector(".sidenav-fixed"),
    instance = M.Sidenav.getInstance(elem);

/* Local variable to keep track of whether sidenav is open
   This is required because the materialize.js logic on which
   the sidebar is built is very annoying and doesn't work well */
var sidebarIsOpen = false;

/* a elements clicking on which will open or close sidenav */
var sidenavToggles = document.getElementsByClassName("toggle-sidenav");

/* Is the window above 992 pixels */
var isWindowFullSize = function isWindowFullSize() {
  return window.innerWidth > 992;
};

/* Change CSS to add padding when sidenav opened */
var addSidenavPadding = function addSidenavPadding() {
  document.getElementById("base-header").style.paddingLeft = "300";
  document.getElementById("base-main").style.paddingLeft = "300";
};

/* Change CSS to remove padding when sidenav closed */
var removeSidenavPadding = function removeSidenavPadding() {
  document.getElementById("base-header").style.paddingLeft = "0";
  document.getElementById("base-main").style.paddingLeft = "0";
};

/* Adjusts navbar and body main padding if window is > 992px width */
var fixPaddingWidth = function fixPaddingWidth() {
  if (!isWindowFullSize()) {
    removeSidenavPadding();
  } else if (isWindowFullSize() && JSON.parse(localStorage.getItem("sidenavOpen"))) {
    addSidenavPadding();
  }
};

/* Open sidenav */
var openSideNav = function openSideNav() {
  document.getElementById("slide-out").classList.remove("hide");
  document.getElementById("slide-out").classList.remove("sidenav-closed");
  document.getElementById("slide-out").classList.add("sidenav-open");
  sidebarIsOpen = true;
  // instance.open();
  if (isWindowFullSize()) {
    addSidenavPadding();
  } else {
    instance.open();
  }
};

/* Close sidenav */
var closeSideNav = function closeSideNav() {
  document.getElementById("slide-out").classList.add("sidenav-closed");
  document.getElementById("slide-out").classList.remove("sidenav-open");
  sidebarIsOpen = false;
  // instance.close();
  if (isWindowFullSize()) {
    removeSidenavPadding();
  } else {
    instance.close();
  }
};

/* Toggle sidebar */
var toggleSidebar = function toggleSidebar() {
  sidebarIsOpen ? closeSideNav() : openSideNav();
  if (isWindowFullSize()) {
    localStorage.setItem("sidenavOpen", JSON.stringify(sidebarIsOpen));
  }
};

/* Initialize sidenav to close and load storage */
var initSideNav = function initSideNav() {
  /* Open sidebar if saved state is to open */
  if (JSON.parse(localStorage.getItem("sidenavOpen")) && isWindowFullSize() || JSON.parse(localStorage.getItem("sidenavOpen")) == null) {
    sidebarIsOpen = false;
    toggleSidebar();
    localStorage.setItem("sidenavOpen", JSON.stringify(sidebarIsOpen));
    /* Otherwise re-initialize to closed  */
  } else {
    sidebarIsOpen = true;
    toggleSidebar();
    localStorage.setItem("sidenavOpen", JSON.stringify(sidebarIsOpen));
  }
  /* Check padding and fix depending on sidebar closed/open status */
  fixPaddingWidth();
};

/* Listen for window size changes */
window.addEventListener("resize", function () {
  fixPaddingWidth();
});

/* Listener for page load */
window.addEventListener("DOMContentLoaded", function (event) {
  initSideNav();
});

/* Listen for menu button clicks */
for (var i = 0; i < sidenavToggles.length; i++) {
  sidenavToggles[i].addEventListener("click", function () {
    toggleSidebar();
  });
}