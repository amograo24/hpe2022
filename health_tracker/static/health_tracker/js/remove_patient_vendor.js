let delete_patient_btn = document.querySelectorAll('.delete_patient');
delete_patient_btn.forEach(button => {
   button.addEventListener('click', (e) => {
      e.preventDefault();
      let elearray = [...document.querySelectorAll('.delete_patient_modal')];
      // console.log(elearray);
      for(let i = 0; i < elearray.length; i++){
         if(elearray[i].dataset.pos == button.dataset.pos){
            elearray[i].style.display = 'block';
         }
      }
   });
});

let cancel_patient_btn = document.querySelectorAll('.delete_patient_cancel');
cancel_patient_btn.forEach(button => {
   button.addEventListener('click', (e) => {
      e.preventDefault();
      let elearray = [...document.querySelectorAll('.delete_patient_modal')];
      // console.log(elearray);
      for(let i = 0; i < elearray.length; i++){
         if(elearray[i].dataset.pos == button.dataset.pos){
            elearray[i].style.display = 'none';
         }
      }
   });
});

let delete_patient_class = document.querySelectorAll('.delete_patient_main')
delete_patient_class.forEach(button => {button.addEventListener('click',event => {
   let id=event.target.id.split('remove_person')[1]
   let patient=button.getAttribute("data-person")
   let to_delete="yes"

   DeletePatient(id,patient,to_delete)
})})

function DeletePatient(id,patient,to_delete) {
   fetch(`/remove/${patient}`,{
      method:"POST",
      headers:{'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value }, //csrf token getAttribute('content')
      body:JSON.stringify({
         to_delete:to_delete // who is the logged in dude?
      })
   })
   .then(response => response.json())
   .then(data => {
      if (data.status===200) {
         location.reload()
      }
   })
}