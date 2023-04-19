// Jquery Code For Hamburger and Popup Starts
$(document).ready(() => {
    $('#hamburger-menu').click(() => {
        $('#hamburger-menu').toggleClass('active');
        $('#nav-menu').toggleClass('active');
    })

    $('#show-popup-btn').click(() =>{
        $('#popup-container').show();
    })
    $('#close-btn').click(() =>{
        $('#popup-container').hide();
    })
})   
// Jquery Code For Hamburger and Popup Ends

//Javascript Code For Form Toggle Starts
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("#login");
    const createAccountForm = document.querySelector("#createAccount");

    document.querySelector("#linkCreateAccount").addEventListener("click", e => {
        e.preventDefault();
        loginForm.classList.add("form--hidden");
        createAccountForm.classList.remove("form--hidden");
    });

    document.querySelector("#linkLogin").addEventListener("click", e => {
        e.preventDefault();
        loginForm.classList.remove("form--hidden");
        createAccountForm.classList.add("form--hidden");
    });

    loginForm.addEventListener("submit", e => {
        e.preventDefault();
    });
});
//Javascript Code For Form Toggle Starts

//Javascript Code For OnScroll Color Change Starts
function changeBG() {
    var navBar = document.getElementById("nav");
    var scrollValue = window.scrollY;
    if (scrollValue > 150) {
        navBar.classList.remove("nav-wrapper");
        navBar.classList.add("bg-wrapper"); 
    }
        else {
        navBar.classList.add("nav-wrapper"); 
        navBar.classList.remove("bg-wrapper"); 
        }
    }
window.addEventListener('scroll', changeBG);
//Javascript Code For OnScroll Color Change Ends

// setting owl carousel Using Jquery
let navText = ["<i class='bx bx-chevron-left'></i>", "<i class='bx bx-chevron-right'></i>"]

    $('#hero-carousel').owlCarousel({
        items: 1,
        dots: false,
        loop: true,
        nav:true,
        navText: navText,
        autoplay: true,
        autoplayHoverPause: true
    })

    $('#top-movies-slide').owlCarousel({
        items: 4,
        dots: false,
        loop: true,
        nav:true,
        navText: navText,
        autoplay: true,
        autoplayHoverPause: true
    })

    $('#latest-movies-slide').owlCarousel({
        items: 4,
        dots: false,
        loop: true,
        nav:true,
        navText: navText,
        autoplay: true,
        autoplayHoverPause: true
    })
    
    $('#latest-series-slide').owlCarousel({
        items: 4,
        dots: false,
        loop: true,
        nav:true,
        navText: navText,
        autoplay: true,
        autoplayHoverPause: true
    })

    $('#latest-cartoons-slide').owlCarousel({
        items: 4,
        dots: false,
        loop: true,
        nav:true,
        navText: navText,
        autoplay: true,
        autoplayHoverPause: true
    })

    $('#top-movies-slide').owlCarousel({
        items: 2,
        dots: false,
        loop: true,
        autoplay: true,
        autoplayHoverPause: true,
        responsive: {
            500: {
                items: 3
            },
            1280: {
                items: 4
            },
            1600: {
                items: 6
            }
        }
    })

    $('.movies-slide').owlCarousel({
        items: 2,
        dots: false,
        nav:true,
        navText: navText,
        margin: 15,
        responsive: {
            500: {
                items: 2
            },
            1280: {
                items: 4
            },
            1600: {
                items: 6
            }
        }
    })