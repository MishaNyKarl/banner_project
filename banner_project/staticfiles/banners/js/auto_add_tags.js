(function($) {
    $(document).ready(function() {
    console.log('work')
        // Проверяем, что кнопка для добавления тегов отображается
        if ($('#id_verticals').length && $('#id_tags').length) {
            var addButton = $('<button type="button" class="add-tags-button">Добавить теги по вертикали</button>');
            addButton.insertAfter('#id_verticals');  // Кнопка появляется после поля с вертикалями

            addButton.on('click', function() {
                var selectedVerticals = $('#id_verticals').val();  // Получаем выбранные вертикали

                if (selectedVerticals && selectedVerticals.length > 0) {
                    $.ajax({
                        url: '/admin/get_tags_by_verticals/',  // URL для запроса тегов по вертикалям
                        data: {
                            'verticals': selectedVerticals
                        },
                        success: function(data) {
                            // Очистим текущие теги и добавим новые
                            $('#id_tags').val(data.selected_tags);
                            alert('Теги добавлены!');
                        }
                    });
                } else {
                    alert('Выберите вертикаль!');
                }
            });
        }
    });
})(django.jQuery);