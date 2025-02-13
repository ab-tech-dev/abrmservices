'use strict';

const addEventOnElement = function(element, type, listener){
    if(element.length > 1){
        for(let i = 0; i < element.length; i++){            
        element[i].addEventListener(type, listener);
        }
    }
    else{
        element.addEventListener(type, listener)
    }
}

//============ NAVBAR ===============//
const navbar = document.querySelector("[data-navbar]");
const navLinks = document.querySelector("[data-nav-link]");
const navToggler = document.querySelector("[data-nav-toggler]");

const toggleNav = function(){
    navbar.classList.toggle("active");
    this.classList.toggle("active");
}

addEventOnElement(navToggler, "click", toggleNav);

const closeNav = function(){
    navbar.classList.remove("active");
    navToggler.classList.remove("active")
}

addEventOnElement(navLinks, "clicks", closeNav);

// Adding the active class to the header
const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

window.addEventListener("scroll", function(){
    if(this.window.scrollY >= 50){
        header.classList.add("active");
        backTopBtn.classList.add("active");
    }else{
        header.classList.remove("active");
        backTopBtn.classList.remove("active")
    }
});

// Tab Button
const tabBtns = document.querySelectorAll("[data-tab-btn]");

let lastClickedTabBtn = tabBtns[0];

const changeTab = function(){
    lastClickedTabBtn.classList.remove("active");
    this.classList.add("active");
    lastClickedTabBtn = this;
}

addEventOnElement(tabBtns, "click", changeTab)

function initAutocomplete() {
    var input = document.getElementById('id_location');
    var autocomplete = new google.maps.places.Autocomplete(input);

    // Bias the autocomplete predictions towards the user's location (optional)
    autocomplete.setComponentRestrictions({'country': ['ng']});  // Restrict to Nigeria (optional)
    
    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            return;
        }

        // You can extract place details like lat/long if needed
        var latitude = place.geometry.location.lat();
        var longitude = place.geometry.location.lng();
        console.log("Selected location: ", place.formatted_address);
    });
}

// Initialize the autocomplete when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initAutocomplete();
    document.addEventListener('DOMContentLoaded', function() {
        if (window.location.hash === '#search-result') {
            const target = document.getElementById('search-result');
            if (target) {
                setTimeout(function() {
                    target.scrollIntoView({ behavior: 'smooth' });
                }, 100);  // Delay to ensure rendering is complete before scrolling
            }
        }
    });


});



// document.addEventListener("click", function(event) {
//     const divs = document.querySelectorAll(".stop");
//     divs.forEach(div => {
//     // Check if the click is outside the div
//         if (!div.contains(event.target)) {
//             document.getElementById('buy-btn').style.color = 'black';
//             document.getElementById('sell-btn').style.color = 'black';
//             document.getElementById('rent-btn').style.color = 'black';
//             document.getElementById('buy-btn').style.background = 'none';
//             document.getElementById('sell-btn').style.background = 'none';
//             document.getElementById('rent-btn').style.background = 'none';
//             document.getElementById('formsr').style.display = 'none';

//             document.getElementById('search-form').style.display = 'none';  // Adjust this as needed
//         }
//     })
// });

// Select the target element or a common parent to observe
const targetNode = document.body;

// Configuration for observing child list changes in the DOM
const config = { childList: true, subtree: true };

// Callback function to execute when mutations are observed
const callback = (mutationsList, observer) => {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            // Check if there are new nodes
            mutation.addedNodes.forEach((node) => {
                // Check if the newly added node is the target container
                if (node.nodeType === 1 && node.classList && node.classList.contains('pac-container') && node.classList.contains('hdpi')) {
                    // Add 'stop' class to the node
                    node.classList.add('stop');
                    
                    // Use setTimeout to allow rendering time and then find the dismissButton
                    setTimeout(() => {
                        const dismissButton = node.querySelector('.dismissButton');
                        if (dismissButton) {
                            dismissButton.classList.add('stop');
                        }
                    }, 0); // Set timeout to 0 for next event loop
                }
            });
        }
    }
};

// Create an observer instance linked to the callback function
const observer = new MutationObserver(callback);

// Start observing the target node for configured mutations
observer.observe(targetNode, config);
