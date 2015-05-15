var userstory_url = "{% url sprints:ver_tareas_ajax pk_proyecto=proyecto.id pk_sprint=sprint.id pk_user_story=userstory.id %}"
console.log(userstory_url);
$(document).ready(function() {
var user_story_id = $('#user_story_id').val();
    $('#tipos').on('change', inicio);
    function inicio(){
        var tipo = $(this).val();
        $.ajax({
            data : {'tipo': tipo, 'id_us': user_story_id},
            url : '/sprints/tareas/tipos/',
            type : 'get',
            success : function(data){
                var html = ""
                console.log(data.length);
                if(data.length > 0){
                    for(var i = 0; i<data.length; i++){
                        html += '<tr>'+
                                    '<td>'+ data[i].descripcion +'</td>'+
                                    '<td>'+ data[i].horas_de_trabajo +'</td>'+
                                    '<td>'+ data[i].actividad +'</td>'+
                                    '<td>'+ data[i].estado +'</td>'+
                                    '<td>'+ data[i].usuario +'</td>'+
                                    '<td>'+ data[i].fecha +'</td>'+
                                '</tr>'
                    }
                }
                else {
                    html += ""
                }
                $('#tabla_tareas').html(html);
            }
        });
    }
});