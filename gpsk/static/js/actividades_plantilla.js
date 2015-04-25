var lista_final;

$(document).ready(function(){
$("#active_sortable").sortable({
    items: "li.actividad",
    placeholder: "ui-state-highlight",
    connectWith: '#inactive_sortable',
    update: function(event,ui) {
        var result_active = $('#active_sortable').sortable('serialize');
        $.ajax({
            type: "POST",
            data: result_active + '&csrfmiddlewaretoken={{ csrf_token }}&active=true',
            url: "/flujos/create/"
        });
        var order = $("#active_sortable").sortable("toArray");
        console.log(order);
    }
}).disableSelection();

$("#inactive_sortable").sortable({
    items: "li.actividad",
    placeholder: "ui-state-highlight",
    connectWith: '#active_sortable',
    update: function(event,ui) {
        var result_inactive = $('#inactive_sortable').sortable('serialize');
        console.log(result_inactive);
        var order = $("#inactive_sortable").sortable("toArray");

        lista_final = result_inactive;
        //return false
        //console.log(order);
    }
}).disableSelection();

var form_id = $('#form-plantilla-flujo');

form_id.submit( function (ev){

    ev.preventDefault();


    $.ajax({
        type: "POST",
        data: lista_final+ '&csrfmiddlewaretoken={{ csrf_token }}&inactive=true&',
        url: "/flujos/create/",
        success: function (data) {
            //return false
            //alert("Llego esto:"+data);
            //$('#invisible-li').hide();
            //console.log("Success");
            window.location.href = "http://127.0.0.1:8000/flujos/";
        }
    });
    //return false


});



});