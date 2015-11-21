$(document).ready(function() {
    $('#product_backlog').DataTable( {
        "order": [[ 1, "asc" ]],
        "pageLength": 50,
        "autoWidth": false,
        "columnDefs": [
            { "orderable": false, "targets": [ 0, 8, 9] }
          ],
        "language": {
            "lengthMenu": "Mostrar _MENU_ resultados por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay resultados disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ )",
            "search": "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Ultima",
                "next":       ">",
                "previous":   "<"
            },
        }
    } );
    $('.dataTables_filter').addClass('pull-left');
    $('#product_backlog_priorizado').DataTable( {
        "order": [[ 0, "asc" ]],
        "pageLength": 50,
        "paging": false,
        "autoWidth": false,
        "columnDefs": [
            { "orderable": false, "targets": 3 }
          ],
        "sDom": '',
        "language": {
            "lengthMenu": "Mostrar _MENU_ resultados por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay resultados disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ )",
            "search": "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Ultima",
                "next":       ">",
                "previous":   "<"
            },
        }
    } );
    $('#sprint_backlog_priorizado').DataTable( {
        "order": [[ 0, "asc" ]],
        "pageLength": 50,
        "paging": false,
        "autoWidth": false,
        "columnDefs": [
            { "orderable": false, "targets": [ 4, 5] }
          ],
        "sDom": '',
        "language": {
            "lengthMenu": "Mostrar _MENU_ resultados por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay resultados disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ )",
            "search": "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Ultima",
                "next":       ">",
                "previous":   "<"
            },
        }
    } );
    $('#sprint_backlog').DataTable( {
        "order": [[ 0, "asc" ]],
        "pageLength": 50,
        "autoWidth": false,
        "columnDefs": [
            { "orderable": false, "targets": 6 }
          ],
        "language": {
            "lengthMenu": "Mostrar _MENU_ resultados por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay resultados disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ )",
            "search": "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Ultima",
                "next":       ">",
                "previous":   "<"
            },
        }
    } );
    $('#user_story_tareas').DataTable( {
        "order": [[ 7, "desc" ]],
        "pageLength": 50,
        "autoWidth": false,
        "aoColumnDefs": [
            { "sType": "string", "aTargets": [ 7 ] }
        ],
        "language": {
            "lengthMenu": "Mostrar _MENU_ resultados por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay resultados disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ )",
            "search": "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Ultima",
                "next":       ">",
                "previous":   "<"
            },
        }
    } );
    $('#user_story_notas').DataTable( {
        "order": [[ 2, "desc" ]],
        "pageLength": 50,
        "autoWidth": false,
        "aoColumnDefs": [
            { "sType": "string", "aTargets": [ 2 ] }
        ],
        "language": {
            "lengthMenu": "Mostrar _MENU_ resultados por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay resultados disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ )",
            "search": "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Ultima",
                "next":       ">",
                "previous":   "<"
            },
        }
    } );
    $('#user_story_adjuntos').DataTable( {
        "order": [[ 0, "desc" ]],
        "pageLength": 50,
        "autoWidth": false,
        "sDom": '',
        "language": {
            "lengthMenu": "Mostrar _MENU_ resultados por página",
            "zeroRecords": "No se encontraron resultados",
            "info": "Página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay resultados disponibles",
            "infoFiltered": "(filtrado de un total de _MAX_ )",
            "search": "Buscar:",
            "paginate": {
                "first":      "Primera",
                "last":       "Ultima",
                "next":       ">",
                "previous":   "<"
            },
        }
    } );
} );