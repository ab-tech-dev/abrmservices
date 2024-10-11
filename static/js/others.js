


const closeMenu = document.getElementById("close-menu");
const openMenu = document.getElementById("open-menu");
const lists = document.querySelector(".lists");

openMenu.onclick = function () {
  lists.style.display = "flex";
  closeMenu.style.display = "flex";
  closeMenu.style.animation = "rotatE 0.1s linear forwards";
  openMenu.style.animation = "endrotatE 0.1s linear forwards";
  openMenu.style.display = "none";
};

closeMenu.onclick = function () {
  lists.style.display = "none";
  closeMenu.style.display = "none";
  openMenu.style.display = "flex";
  openMenu.style.animation = "rotatE 0.1s linear forwards";
  closeMenu.style.animation = "endrotatE 0.1s linear forwards";
};


var icn = document.querySelector(".icn");
var icn1 = document.querySelector(".icn1");
var icn2 = document.querySelector(".icn2");
var a = document.querySelector(".a");
var sep = document.querySelector(".sep");
var nav = document.querySelector("nav");

window.onload = function () {
  icn2.style.animation = "moveRight 0.5s linear forwards";
  icn1.style.animation = "moveRight 0.6s linear forwards";
  icn.style.animation = "moveRight 0.7s linear forwards";
  a.style.animation = "appear 2s linear forwards";
  sep.style.animation = "moveUp 1.5s linear forwards";
  nav.style.animation = "delay 2s linear forwards";
};

var form1 = document.querySelectorAll(".Form1");
var form2 = document.querySelectorAll(".Form2");
var for1 = document.querySelectorAll(".For1");
var for2 = document.querySelectorAll(".For2");
var form3 = document.querySelectorAll(".Form3");
var Next1 = document.querySelectorAll(".next1");
var Next2 = document.querySelectorAll(".next2");
var Back1 = document.querySelectorAll(".prev2");
var Back2 = document.querySelectorAll(".prev3");
var Submit = document.querySelectorAll(".submit");
var Nex1 = document.querySelectorAll(".next");
var Back = document.querySelectorAll(".pre2");
var Submi = document.querySelectorAll(".submi");
var progress = document.querySelectorAll(".progress");
var progres = document.querySelectorAll(".progres");

Next1.forEach((Next1) => {
  Next1.onclick = function () {
    form1.forEach((form1) => {
      form1.style.display = "none";
    });
    form2.forEach((form2) => {
      form2.style.display = "block";
    });
    progress.forEach((progress) => {
      progress.style.width = "33.33%";
    });
  };
});


Back1.forEach((Back1) => {
  Back1.onclick = function () {
    form1.forEach((form1) => {
      form1.style.display = "block";
    });
    form2.forEach((form2) => {
      form2.style.display = "none";
    });
    form3.forEach((form3) => {
      form3.style.display = "none";
    });
    progress.forEach((progress) => {
      progress.style.width = "0%";
    });
  };
});

Next2.forEach((Next2) => {
  Next2.onclick = function () {
    form1.forEach((form1) => {
      form1.style.display = "none";
    });
    form2.forEach((form2) => {
      form2.style.display = "none";
    });
    form3.forEach((form3) => {
      form3.style.display = "grid";
      form3.style.gridTemplateColumns = "1fr";
    });
    progress.forEach((progress) => {
      progress.style.width = "66.66%";
    });
  };
});

Back2.forEach((Back2) => {
  Back2.onclick = function () {
    form1.forEach((form1) => {
      form1.style.display = "none";
    });
    form2.forEach((form2) => {
      form2.style.display = "block";
    });
    form3.forEach((form3) => {
      form3.style.display = "none";
    });
    progress.forEach((progress) => {
      progress.style.width = "33.33%";
    });
  };
});

Submit.forEach((Submit) => {
  Submit.onclick = function () {
    progress.forEach((progress) => {
      progress.style.width = "100%";
    });
  };
});


const swiper = new Swiper('.swiper', {
  // Optional parameters
  direction: 'vertical',
  loop: true,

  // If we need pagination
  pagination: {
    el: '.swiper-pagination',
  },

  // Navigation arrows
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },

  // And if we need scrollbar
  scrollbar: {
    el: '.swiper-scrollbar',
  },
});


// static/contact/script.js
// static/contact/script.js
document.getElementById('contact-form').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent the default form submission behavior

  // Create an object to hold form data
  const formData = {
      Cfirst_name: document.getElementById('first-name').value,
      Clast_name: document.getElementById('last-name').value,
      Cemail: document.getElementById('email').value,
      Cphone: document.getElementById('phone').value,
      Ctext_area: document.querySelector('textarea[name="Ctext_area"]').value,
      to_name: 'YourRecipientName', // Static recipient name; replace or modify as needed
  };

  // Replace 'YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', and 'YOUR_PUBLIC_KEY' with your actual EmailJS information
  emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', formData)
      .then(function() {
          console.log('SUCCESS!'); // Success message
      }, function(error) {
          console.log('FAILED...', error); // Error message
      });
});

