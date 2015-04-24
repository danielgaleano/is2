$(document).ready(function() {

    // $('#form_proyecto').submit(function(event){
    //     if(fecha_inicio > fecha_fin){
    //     alert("Please select a different End Date.");
    //         event.preventDefault();
    //     };
        
    // });
    
    $('#selectall').click(function(event) {  //on click 
        if(this.checked) { // check select status
            $('.checkbox1').each(function() { //loop through each checkbox
                this.checked = true;  //select all checkboxes with class "checkbox1"               
            });
        }else{
            $('.checkbox1').each(function() { //loop through each checkbox
                this.checked = false; //deselect all checkboxes with class "checkbox1"                       
            });         
        }
    });
    $( '#id_permissions :checkbox[value="20"]' )
        .attr( "title", "Se debe utilizar además el permiso listar usuario" ).tooltip({ placement: 'left'});
    $( '#id_permissions :checkbox[value="21"]' )
        .attr( "title", "Se debe utilizar además el permiso listar usuario" ).tooltip({ placement: 'left'});
    $( '#id_permissions :checkbox[value="22"]' )
        .attr( "title", "Se debe utilizar además el permiso listar usuario" ).tooltip({ placement: 'left'});

    $('#id_permissions :checkbox[value="20"]').click(function(event){
        if (this.checked) {
            $('#id_permissions :checkbox[value="23"]').each(function() { //loop through each checkbox
                this.checked = true;  //select all checkboxes with class "checkbox1"               
            });
        }else{
            $('#id_permissions :checkbox[value="23"]').each(function() { //loop through each checkbox
                this.checked = false; //deselect all checkboxes with class "checkbox1"                       
            });
        }
    });
    $('#id_permissions :checkbox[value="21"]').click(function(event){
        if (this.checked) {
            $('#id_permissions :checkbox[value="23"]').each(function() { //loop through each checkbox
                this.checked = true;  //select all checkboxes with class "checkbox1"               
            });
        }else{
            $('#id_permissions :checkbox[value="23"]').each(function() { //loop through each checkbox
                this.checked = false; //deselect all checkboxes with class "checkbox1"                       
            });
        }
    });
    $('#id_permissions :checkbox[value="22"]').click(function(event){
        if (this.checked) {
            $('#id_permissions :checkbox[value="23"]').each(function() { //loop through each checkbox
                this.checked = true;  //select all checkboxes with class "checkbox1"               
            });
        }else{
            $('#id_permissions :checkbox[value="23"]').each(function() { //loop through each checkbox
                this.checked = false; //deselect all checkboxes with class "checkbox1"                       
            });
        }
    });
    
    $('.errorlist').addClass('alert alert-danger');


    
    $( "#id_fecha_inicio" ).datepicker({
        isRTL: false,
        format: 'dd/mm/yyyy',
        autoclose:true,
        language: 'es',
        orientation: "auto",

    });

        $( "#id_fecha_fin" ).datepicker({
        isRTL: false,
        format: 'dd/mm/yyyy',
        autoclose:true,
        language: 'es',
        orientation: "auto",

    });

    var fecha_inicio  = $("#id_fecha_inicio").val(); //2013-09-5
    var fecha_fin    = $("#id_fecha_fin").val(); //2013-09-10


    
    
});