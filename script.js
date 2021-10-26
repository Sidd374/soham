// setTimeout(function() {
//     const loading = document.querySelector('.loading');
//     const main = document.querySelector('.main');
//     loading.style.display = "none";
//     main.style.display = "block";
   
// }, 3000);

setTimeout(function() {
  var top = document.getElementsByClassName("top");
  var bottom = document.getElementsByClassName("bottom");
  var cards = document.querySelector('.cards');
  cards.style.left = "50%";
  var cards2 = document.querySelector('.cards_2');
  cards2.style.left = "5%";
  [...top].map((i) => {
      i.style.transform = 'rotateY(0deg)'
  });
  [...bottom].map((i) => {
      i.style.transform = 'rotateY(-180deg)'
  });
}, 1500);



var lFollowX = 0,
    lFollowY = 0,
    x = 0,
    y = 0,
    friction = 1 / 30;

function moveBackground() {
  x += (lFollowX - x) * friction;
  y += (lFollowY - y) * friction;
  
  translate = 'translate(' + x + 'px, ' + y + 'px) scale(1.1)';

  $('.main').css({
    '-webit-transform': translate,
    '-moz-transform': translate,
    'transform': translate
  });

  window.requestAnimationFrame(moveBackground);
}

$(window).on('mousemove click', function(e) {

  var lMouseX = Math.max(-100, Math.min(100, $(window).width() / 2 - e.clientX));
  var lMouseY = Math.max(-100, Math.min(100, $(window).height() / 2 - e.clientY));
  lFollowX = (20 * lMouseX) / 100; // 100 : 12 = lMouxeX : lFollow
  lFollowY = (10 * lMouseY) / 100;

});

moveBackground();




$('.btn').on('click',function(e) {
  document.querySelector('.button_1').style.display = 'block';
  document.querySelector('.button_2').style.display = 'block';
  if(this.hash == '#form'){
    document.querySelector('.button_1').style.display = 'none';
    document.querySelector('.main_blur').style.display = 'none';
    setTimeout(function(){
      document.querySelector('.overlay').style.display = 'block';
    },500);
  }
  if(this.hash == '#landing_page'){
    document.querySelector('.button_2').style.display = 'none';
    setTimeout(function(){
      document.querySelector('.overlay').style.display = 'none';
    },200);
    setTimeout(function(){
      document.querySelector('.main_blur').style.display = 'block';
    },2000);
  }

  if(this.hash !== ''){
    e.preventDefault();
    const hash = this.hash;
    $('html, body').animate({
      scrollTop: $(hash).offset().top
    }, 1500);
  };
});

$(window).bind('mousewheel', function(event) {
  document.querySelector('.button_2').style.display = 'block';
  document.querySelector('.button_1').style.display = 'block';
  document.querySelector('.main_blur').style.opacity = '1';
  if (event.originalEvent.wheelDelta >= 0) {
    document.getElementsByTagName("BODY")[0].style.transform = 'translateY(0%)';
    document.querySelector('.button_2').style.display = 'none';
    setTimeout(function(){
      document.querySelector('.overlay').style.display = 'none';
    },200);
    setTimeout(function(){
      document.querySelector('.main_blur').style.display = 'block';
    },2000);
  }
  else {
    document.getElementsByTagName("BODY")[0].style.transform = 'translateY(-50%)';
    document.querySelector('.main_blur').style.display = 'none';
    document.querySelector('.main_blur').style.opacity = '0';
    document.querySelector('.button_1').style.display = 'none';
    setTimeout(function(){
      document.querySelector('.overlay').style.display = 'block';
    },1000);
  }
});




