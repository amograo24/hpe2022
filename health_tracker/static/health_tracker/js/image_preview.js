let img_class=document.querySelectorAll('.img_class')
let img_class_array=[...img_class]
img_class_array.forEach(element => {
   main(element.id.slice(3),element.getAttribute("data-image"))
})

function handleBlob(blobResponse,id)
{
   const imageObjectURL = URL.createObjectURL(blobResponse)
   document.querySelector(`#img${id}`).style.backgroundImage=`url(${imageObjectURL})`
}

function main(id,file_path)
{
   let token = $("input[name='csrfmiddlewaretoken']").val()
   let url = `/get_file/${file_path}`
   let header = {'X-CSRFToken': token}
  console.log(url)
   let request = fetch(url, {method: "POST", headers: header})
   request.then(resp => resp.blob())
   .then((blobResponse) => {this.handleBlob(blobResponse,`${id}`)} )
   
}
$(document).ready(main)