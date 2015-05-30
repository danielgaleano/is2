$(document).ready(function() {
    $('td[data-href]').on("click", function() {
        document.location = $(this).data('href');
        console.log($(this).data('href'));
    });

});