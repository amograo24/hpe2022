function check_type(event)
{
    let value = $("#id_division").val()
    if(value.toLowerCase()=="nou")
    {
        $("#id_department").hide()
        $("#id_reg_no").hide()
    }else{
        $("#id_department").show()
        $("#id_reg_no").show()
    }
}

function main()
{
    $("#id_division").change(check_type)

}


$(document).ready(main)