let delete_file_btn = document.querySelectorAll('.delete_file');
delete_file_btn.forEach(button => {
   button.addEventListener('click', (e) => {
      e.preventDefault();
      let elearray = [...document.querySelectorAll('.delete_file_modal')];
      for(let i = 0; i < elearray.length; i++){
         if(elearray[i].dataset.pos == button.dataset.pos){
            elearray[i].style.display = 'block';
         }
      }
   });
});

let cancel_file_btn = document.querySelectorAll('.delete_file_cancel');
cancel_file_btn.forEach(button => {
   button.addEventListener('click', (e) => {
      e.preventDefault();
      let elearray = [...document.querySelectorAll('.delete_file_modal')];
      for(let i = 0; i < elearray.length; i++){
         if(elearray[i].dataset.pos == button.dataset.pos){
            elearray[i].style.display = 'none';
         }
      }
   });
});

let delete_file_main_class = document.querySelectorAll('.delete_file_main')
delete_file_main_class.forEach(button => {button.addEventListener('click',event => {
   let id=event.target.id.split('delete_file_main')[1]
   let file_name=button.getAttribute("data-filename")
   let to_delete="yes"

   DeleteFile(id,file_name,to_delete)
})})

function DeleteFile(id,filename,to_delete) {
   fetch(`/delete_file/${filename}`,{
      method:"POST",
      headers:{'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value }, 
      body:JSON.stringify({
         to_delete:to_delete 
      })
   })
   .then(response => response.json())
   .then(data => {
      if (data.status===200) {
         location.reload()
      }
   })
}