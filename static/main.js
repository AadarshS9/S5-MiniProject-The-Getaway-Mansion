const menu = document.querySelector(".menu");
const menulist = document.querySelector('nav ul');

menu.addEventListener('click', ()=>{
  menulist.classList.toggle("show");
});






//FORM CALENDAR//
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth() + 1; //January is 0!
var yyyy = today.getFullYear();
if (dd < 10) {
   dd = '0' + dd;
}
if (mm < 10) {
   mm = '0' + mm;
}   
today = yyyy + '-' + mm + '-' + dd;
document.getElementById("checkin_date").setAttribute("min", today);

function getDays(){
  var checkin_date = new Date(document.getElementById('checkin_date').value);
  var checkout_date = new Date(document.getElementById('checkout_date').value);
  var time_difference = checkout_date.getTime() - checkin_date.getTime();
  var days_difference = time_difference / (1000*3600*24);
  document.getElementById('days').value = days_difference;
}

