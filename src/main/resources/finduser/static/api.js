function getDataModel() {
    return $.ajax({
        type: 'GET', cache: 'false', dataType: 'json',
        url: '/finduser/model',
    });
};

function findUser(json_obj) {
    return $.ajax({
        type: 'POST', cache: 'false', dataType: 'json',
        url: '/finduser',
        contentType: 'application/json',
        data: JSON.stringify(json_obj),
    });
};

function getTemplate(name, callback) {
    return $.get('/templates/' + name + '.jsr', function(data) {
        var tpl = $.templates(data);
        callback(tpl);
    });
};
