// const closeMenu = document.getElementById("close-menu");
// const openMenu = document.getElementById("open-menu");
// const lists = document.querySelector(".lists");

// openMenu.onclick = function () {
//   lists.style.display = "flex";
//   closeMenu.style.display = "flex";
//   closeMenu.style.animation = "rotatE 0.1s linear forwards";
//   openMenu.style.animation = "endrotatE 0.1s linear forwards";
//   openMenu.style.display = "none";
// };

// closeMenu.onclick = function () {
//   lists.style.display = "none";
//   closeMenu.style.display = "none";
//   openMenu.style.display = "flex";
//   openMenu.style.animation = "rotatE 0.1s linear forwards";
//   closeMenu.style.animation = "endrotatE 0.1s linear forwards";
// };


// var icn = document.querySelector(".icn");
// var icn1 = document.querySelector(".icn1");
// var icn2 = document.querySelector(".icn2");
// var a = document.querySelector(".a");
// var sep = document.querySelector(".sep");
// var nav = document.querySelector("nav");

// window.onload = function () {
//   icn2.style.animation = "moveRight 0.5s linear forwards";
//   icn1.style.animation = "moveRight 0.6s linear forwards";
//   icn.style.animation = "moveRight 0.7s linear forwards";
//   a.style.animation = "appear 2s linear forwards";
//   sep.style.animation = "moveUp 1.5s linear forwards";
//   nav.style.animation = "delay 2s linear forwards";
// };
// const swiper = new Swiper(".swiper", {
//   // Optional parameters
//   autoplay: {
//     delay: 4000
//   },

//   direction: "horizontal",
//   loop: true,
//   effect: "coverflow",
//   grabCursor: false,
//   centeredSlides: true,
//   coverflowEffect: {
//     rotate: 0,
//     stretch: 0,
//     depth: 100,
//     modifier: 2
//   },

//   breakpoints: {
//     0: {
//       slidesPerView: 1,
//       centeredSlides: false,

//       autoplay: {
//         delay: 4000
//       }
//     },

//     600: {
//       slidesPerView: 3,
//       direction: "horizontal",
//       loop: true,
//       effect: "coverflow",
//       grabCursor: false,
//       centeredSlides: true,
//       coverflowEffect: {
//         rotate: 0,
//         stretch: 0,
//         depth: 100,
//         modifier: 2
//       },
//       autoplay: {
//         delay: 4000
//       }
//     },

//     1200: {
//       slidesPerView: 5,
//       direction: "horizontal",
//       loop: true,
//       effect: "coverflow",
//       grabCursor: false,
//       centeredSlides: true,
//       coverflowEffect: {
//         rotate: 0,
//         stretch: 0,
//         depth: 100,
//         modifier: 2
//       },
//       autoplay: {
//         delay: 4000
//       }
//     }
//   }
// });

var form1 = document.querySelectorAll(".Form1");
var form2 = document.querySelectorAll(".Form2");
var form3 = document.querySelectorAll(".Form3");
var Next1 = document.querySelectorAll(".next1");
var Next2 = document.querySelectorAll(".next2");
var Back1 = document.querySelectorAll(".prev2");
var Back2 = document.querySelectorAll(".prev3");
var Submit = document.querySelectorAll(".submit");
var progress = document.querySelectorAll(".progress");

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

var faqs = document.querySelectorAll(".faqs");
var we = document.querySelectorAll(".we");

const change = function () {
  we.forEach((we) => {
    we.classList.toggle("uil-minus-square-full");
  });
};

faqs.forEach((faqs) => {
  faqs.addEventListener("click", () => {
    faqs.classList.toggle("open");
  });
});

const swiper = new Swiper(".swiper", {
  // Optional parameters
  autoplay: {
    delay: 4000
  },

  direction: "horizontal",
  loop: true,
  effect: "coverflow",
  grabCursor: false,
  centeredSlides: true,
  coverflowEffect: {
    rotate: 0,
    stretch: 0,
    depth: 100,
    modifier: 2
  },

  breakpoints: {
    0: {
      slidesPerView: 1,
      centeredSlides: false,

      autoplay: {
        delay: 4000
      }
    },

    600: {
      slidesPerView: 3,
      direction: "horizontal",
      loop: true,
      effect: "coverflow",
      grabCursor: false,
      centeredSlides: true,
      coverflowEffect: {
        rotate: 0,
        stretch: 0,
        depth: 100,
        modifier: 2
      },
      autoplay: {
        delay: 4000
      }
    },

    1200: {
      slidesPerView: 5,
      direction: "horizontal",
      loop: true,
      effect: "coverflow",
      grabCursor: false,
      centeredSlides: true,
      coverflowEffect: {
        rotate: 0,
        stretch: 0,
        depth: 100,
        modifier: 2
      },
      autoplay: {
        delay: 4000
      }
    }
  }
});

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

var ani = document.querySelector(".sec");
var page = document.querySelectorAll(".page");
var icn = document.querySelector(".icn");
var icn1 = document.querySelector(".icn1");
var icn2 = document.querySelector(".icn2");
var a = document.querySelector(".a");
var sep = document.querySelector(".sep");
var nav = document.querySelector("nav");

window.onload = function () {
  ani.classList.toggle("showtime");

  page.forEach((page) => {
    page.style.animation = "appear 1s linear forwards";
  });

  icn2.style.animation = "moveRight 0.5s linear forwards";
  icn1.style.animation = "moveRight 0.6s linear forwards";
  icn.style.animation = "moveRight 0.7s linear forwards";
  a.style.animation = "appear 2s linear forwards";
  sep.style.animation = "moveUp 1.5s linear forwards";
  nav.style.animation = "delay 2s linear forwards";
};
