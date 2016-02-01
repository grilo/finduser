function getProductModel() {
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

