function addProduct (e) {
    e.preventDefault();

    getProductModel().success(function (response) {
        var keys = Object.keys(response);
        keys.sort();

        getTemplate("product", function (tpl) {
            var product = $(tpl.render({"fields": keys}));
            product.find('button').on('click', function (e) {
                e.target.closest('div.panel').remove();
            });
            $('#productList').prepend(product);

            var e = {
                "target": product.find('div.panel-body'),
                "data": { "fields": keys },
            };

            addProductField(e).done(function (response) {
                // We do some tomfoolery here for UX purposes
                // It breaks a million principles, but it's usable
                var button = product.find('button.btn-danger');
                button.removeClass('btn-danger');
                button.addClass('btn-success');

                var span = button.find('span');
                span.removeClass('glyphicon-minus-sign');
                span.addClass('glyphicon-plus-sign');

                button.off('click').on('click', e.data, addProductField);
            });

        }); // product
    }); // getProductModel
}

function addProductField (e) {
    var panelBody = $(e.target.closest('div.panel-body'));
    return getTemplate("field", function (tpl) {
        var field = $(tpl.render({"fields": e.data.fields}));
        field.fadeIn('slow');
        panelBody.append(field);
        field.find('span.glyphicon-minus-sign').parent().on('click', function (e) {
            field.remove();
        });
    });
}

function submitProducts (e) {
    requestObject = [];
    $('div.product').each(function (productPanel) {
        product = {};
        $(this).children('form').each(function (fieldForm) {
            var fieldName = $(this).find('select.fieldName').find(':selected').text();
            var fieldOperator = $(this).find('select.fieldOperator').find(':selected').text();
            var fieldValue = $(this).find('input.fieldValue').val();
            product[fieldName] = fieldOperator + fieldValue;
        });
        requestObject.push(product);
    });
    var promise = findUser(requestObject);

    promise.success(function (response) {
        console.log("Everything OK");
    });

    promise.error(function (response) {
        console.log("Oops, something ugly!");
    });
}


$(window).ready(function () {

    getTemplate("body", function (tpl) {
        var body = $(tpl.render({}));
        body.fadeIn('slow');
        $('#content').prepend(body);
        $('#addProduct').on('click', addProduct);
        $('#submit').on('click', submitProducts);
    }); // body

});
