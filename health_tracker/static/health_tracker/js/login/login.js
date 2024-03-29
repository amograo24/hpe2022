function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

$(document).ready(function(){
  document.querySelectorAll("label[for=id_username]")[0].innerHTML = "Well-Being ID:"
  document.querySelectorAll('input[name="username"]')[0].placeholder = "Enter WBID"
  document.querySelectorAll('input[name="password"]')[0].placeholder = "Enter Password"
  document.querySelectorAll("label[for=id_username]")[1].innerHTML = "Health Care Worker/Vendor ID:"
  document.querySelectorAll('input[name="username"]')[1].placeholder = "Enter HCWV ID"
  document.querySelectorAll('input[name="password"]')[1].placeholder = "Enter Password"
  var $width = $(window).width();
  if($width > 929) {
    if(getCookie('side') === 'left'){
      
      $('#slideBox').animate({
        'marginLeft' : '50%'
      });
      $('.topLayer').animate({
        'marginLeft': '0'
      });
    }
    else{
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft' : '100%'
      });
    }
    $('#goRight').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft' : '100%'
      });
      document.cookie = "side=right";
    });
    $('#goLeft').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '50%'
      });
      $('.topLayer').animate({
        'marginLeft': '0'
      });
      document.cookie = "side=left"
    });
  }
  else{
    if(getCookie('side') === 'left'){
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft' : '100%'
      });
    }
    else{
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft': '0'
      });
    }
    $('#goRight').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft' : '100%'
      });
      document.cookie = "side=left";
    });
    $('#goLeft').on('click', function(){
      $('#slideBox').animate({
        'marginLeft' : '0'
      });
      $('.topLayer').animate({
        'marginLeft': '0'
      });
      document.cookie = "side=right";
    });
  }
});