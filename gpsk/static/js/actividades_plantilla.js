$(document).ready(function(){
$("#active_sortable").sortable({
    items: "li.actividad",
    placeholder: "sort_placeholder",
    connectWith: '#inactive_sortable, #trashed_sortable',
    update: function(event,ui) {
        var result_active = $('#active_sortable').sortable('serialize');
        $.ajax({
            type: "POST",
            data: result_active + '&csrfmiddlewaretoken={{ csrf_token }}&active=true',
            url: "/flujos/create/"
        });
    }
}).disableSelection();

$("#inactive_sortable").sortable({
    items: "li.actividad",
    placeholder: "sort_placeholder",
    connectWith: '#active_sortable, #trashed_sortable',
    update: function(event,ui) {
        var result_inactive = $('#inactive_sortable').sortable('serialize');
        var id_array = $(this).sortable('toArray');
        $.ajax({
            type: "POST",
            data: result_inactive + '&csrfmiddlewaretoken={{ csrf_token }}&inactive=true',
            url: "/flujos/create/"
        });
    }
}).disableSelection();
});