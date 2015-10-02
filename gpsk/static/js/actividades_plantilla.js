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

var form_id = $('#form-plantilla-flujo-create');
//var plantilla_nombre = $('#nombre').val();

form_id.submit( function (ev){

    var plantilla_nombre = document.getElementById('nombre').value;
    console.log("Out "+plantilla_nombre);

    ev.preventDefault();

    if( !plantilla_nombre){
        $('#error-agregado').append('<div id="hay-error" class="alert alert-danger col-lg-6" role="alert">'+
  			                            '<i class="fa fa-fw fa-warning"></i>'+
  			                            '<span class="sr-only">Error:</span>'+
 			                            'Escriba un nombre de plantilla de flujo.'+
 			                            '</div>'
 			                );
        return false;
    }

    $.ajax({
        type: "POST",
        //data: {'nombre_plantilla':plantilla_nombre},
        data: lista_final+ '&csrfmiddlewaretoken={{ csrf_token }}&inactive=true&nombre_plantilla='+plantilla_nombre,
        url: "/flujos/create/",
        success: function (data) {
            //return false
            //console.log("Llego esto:"+data);
            //$('#invisible-li').hide();
           //console.log("Success "+data['nombre_plantilla']);
            //datos = JSON.parse(data);
            //var error_id_repetido = $('#hay-error-repetido');
            //var error_id_vacio = $('#hay-error-vacio');
            result_repetido = $(data).find("#hay-error-repetido");
            result_vacio = $(data).find("#hay-error-vacio");
            console.log(result_repetido);
            console.log(result_vacio);
            if( result_repetido.length){
                //console.log(error_id_repetido);

                $('#error-agregado').append('<div id="hay-error" class="alert alert-danger col-lg-6" role="alert">'+
  			                            '<i class="fa fa-fw fa-warning"></i>'+
  			                            '<span class="sr-only">Error:</span>'+
 			                            'Ya existe una plantilla de flujo ese nombre, escriba otro nombre.'+
 			                            '</div>'
 			                );
            }

            else{
                //console.log(data);

                console.log("Success "+plantilla_nombre);
                //console.log("data= "+data['nombre_plantilla']);
                //window.location.href = "http://127.0.0.1:8000/flujos/";
                window.location.href = window.location.origin + "/flujos/";
            }

        },
        error: function(xhr,errmsg,err) {
                // Show an error
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }

    });
    return false


});

var form_id = $('#form-plantilla-flujo-update');
//var plantilla_nombre = $('#nombre').val();

form_id.submit( function (ev){

    var plantilla_nombre = document.getElementById('nombre').value;
    console.log("Out "+plantilla_nombre);

    ev.preventDefault();


    $.ajax({
        type: "POST",
        //data: {'nombre_plantilla':plantilla_nombre},
        data: lista_final+ '&csrfmiddlewaretoken={{ csrf_token }}&inactive=true&nombre_plantilla='+plantilla_nombre,
        url: window.location.href,
        success: function (data) {
            //return false
            //alert("Llego esto:"+data);
            //$('#invisible-li').hide();
           //console.log("Success "+data['nombre_plantilla']);
            console.log("Success "+ plantilla_nombre);
            console.log("location "+ window.location.origin + "/flujos/");
            //window.location.href = "http://127.0.0.1:8000/flujos/";
            window.location.href = window.location.origin + "/flujos/";
        },
        error: function(xhr,errmsg,err) {
                // Show an error
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }

    });
    return false


});


});