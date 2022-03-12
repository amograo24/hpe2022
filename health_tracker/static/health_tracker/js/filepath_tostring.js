    // document.addEventListener('DOMContentLoaded',FilePathToString);
    let file_name_class = document.querySelectorAll('.file_name_class')
    let file_name_array=[...file_name_class]
    file_name_array.forEach(element => {
       FilePathToString(element.id.slice(4),element.getAttribute("data-name"))
    })

    let file_name_modal = document.querySelectorAll('.modal-filename')
    // console.log(file_name_modal)
    let file_name_main=[...file_name_modal]
    file_name_main.forEach(element => {
       element.innerHTML = String(`${element.getAttribute('data-name')}`).split("/").slice(-1)[0];
    })
    function FilePathToString(id,file) {
       let path_name=String(`${file}`)
       let file_name=path_name.split("/").slice(-1)[0]
       document.querySelector(`#file${id}`).innerHTML=`${file_name}`;
    }