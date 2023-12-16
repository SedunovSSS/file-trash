let = contextMenu = $('.context-menu-open');
let = contextMenu1 = $('.context-menu-open1');
$('.context-menu').on('contextmenu', function (e) {
    e.preventDefault();
    path = e.currentTarget.getAttribute('file-path');
    $(".context_menu_a").each(function() {
        if ($(this).text() == 'Удалить'){
            $(this).attr('href', '/delete?object='+path)
        }
        else{
            $(this).attr('href', '/download?object='+path)
        }
    });
    contextMenu.css({top: e.clientY + 'px', left: e.clientX + 'px' }); 
    contextMenu.show();
    contextMenu1.hide();
});
$(document).on('click', function () {
    contextMenu.hide();
});
$('.context-menu1').on('contextmenu', function (e) {
    e.preventDefault();
    path = e.currentTarget.getAttribute('file-path');
    $(".context_menu_a").each(function() {
        $(this).attr('href', '/delete?object='+path)
    });
    contextMenu1.css({top: e.clientY + 'px', left: e.clientX + 'px' }); 
    contextMenu1.show();
    contextMenu.hide();
});
$(document).on('click', function () {
    contextMenu1.hide();
});