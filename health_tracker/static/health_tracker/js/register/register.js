function check_type(event)
{
    let value = $("#id_division").val()
    if(value.toLowerCase()=="nou")
    {
        $("#id_department").hide()
        $("label[for=\"id_department\"]").hide()
        $("label[for=\"id_reg_no\"]").hide()
        $("#id_reg_no").hide()

        $("#id_reg_no").val("0000")
        $("#id_department").prop('required',false)
        $("#id_aadharid").show()
        $('label[for="id_aadharid"]').show()
        $("#id_aadharid").val("")
        

    }else{
        $("#id_reg_no").val("")
        $("#id_aadharid").val("000000000000")
        $("#id_aadharid").hide()
        $('label[for="id_aadharid"]').hide()
        $("#id_department").hide()
        $("label[for=\"id_department\"]").hide()
        $("label[for=\"id_reg_no\"]").show()
        $("#id_reg_no").show()
        $("#id_department").prop('required',false)
    }
    if(value.toLowerCase() == "i/sp" || value.toLowerCase() == "msh"){
        $("label[for=\"id_full_name\"]").text("Company Name")

    }else if(value.toLowerCase() == "nou" || value.toLowerCase() == "d/hcw/ms")
    {
        $("label[for=\"id_full_name\"]").text("Full Name")
    }
    if(value.toLowerCase() == "d/hcw/ms"){
        $("#id_department").show()
        $("#id_department").prop('required',true)
        $("label[for=\"id_department\"]").show()
    }
}

function main()
{
    $("#id_aadharid").hide()
    $("#id_aadharid").val("000000000000")
    $('label[for="id_aadharid"]').hide()
    $("#id_department").prop('required',true)
    $("#id_division").change(check_type)
    check_type(1)

}


$(document).ready(main)