document.addEventListener('DOMContentLoaded', function () {
  var elems = document.querySelectorAll('.sidenav');
  var instances = M.Sidenav.init(elems, options);
});

$(document).ready(function () {
  const $nav = $('#navbar');

  $('.sidenav').sidenav();

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();

      scrollIntoViewWithOffset(this.getAttribute('href'), $nav.height());
    });
  });

  $(' input#subject_text, textarea#message').characterCounter();

  $(function () {
    $(document).scroll(function () {
      $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
    });
  });

  function scrollIntoViewWithOffset(selector, offset) {
    window.scrollTo({
      behavior: 'smooth',
      top:
        document.querySelector(selector).getBoundingClientRect().top -
        document.body.getBoundingClientRect().top -
        offset,
    });
  }

  gsap.from('#hero__content', { duration: 1, opacity: 0, y: 50 });

  gsap.from('.card', {
    scrollTrigger: '.card',
    duration: 0.25,
    opacity: 0,
    y: 50,
    stagger: 0.25,
  });

  gsap.from('.col-t', {
    scrollTrigger: '.col-t',
    duration: 0.75,
    opacity: 0,
    y: 50,
    stagger: 0.25,
  });

  gsap.from('.input-field', {
    scrollTrigger: '.input-field',
    duration: 1,
    opacity: 0,
    y: 50,
    stagger: 0.25,
  });

  gsap.from('.col-l', {
    scrollTrigger: '.col-l',
    duration: 0.75,
    opacity: 0,
    x: -50,
  });

  gsap.from('.col-r', {
    scrollTrigger: '.col-r',
    duration: 0.5,
    opacity: 0,
    x: 50,
  });
});
