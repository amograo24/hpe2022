$(document).ready(function(){
  var $width = $(window).width();
  if($width > 929) {
    $('#goRight').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft' : '100%'
      });
    });
    $('#goLeft').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '50%'
      });
      $('.topLayer').animate({
        'marginLeft': '0'
      });
    });
  }
  else{
    $('#goRight').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft' : '100%'
      });
    });
    $('#goLeft').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft': '0'
      });
    });
  }
});