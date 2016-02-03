function addProduct (e) {
    e.preventDefault();

    getProductModel().success(function (response) {
        console.log(response);
        var keys = Object.keys(response.product);
        keys.sort();
        var fields = [];
        $.each(keys, function (index, k) {
            fields.push(k + " (" + response.product[k] + ")")
        });

        getTemplate("product", function (tpl) {
            var product = $(tpl.render({"fields": fields}));
            product.find('button').on('click', function (e) {
                e.target.closest('div.panel').remove();
            });
            $('#productList').prepend(product);

            var e = {
                "target": product.find('div.panel-body'),
                "data": { "fields": fields},
            };

            var panelBody = product.find('div.panel-body');

            getTemplate("field", function (tpl) {
                var field = $(tpl.render({"fields": e.data.fields}));
                panelBody.append(field);
                field.fadeIn('slow');

                // We do some tomfoolery here for UX purposes
                // It breaks a million principles, but it's usable
                var button = product.find('button.btn-danger');
                button.removeClass('btn-danger');
                button.addClass('btn-success');

                var span = button.find('span');
                span.removeClass('glyphicon-minus-sign');
                span.addClass('glyphicon-plus-sign');

                button.on('click', e.data, addProductField);

            });


        }); // product
    }); // getProductModel
}

function addProductField (e) {
    e.preventDefault();
    var panelBody = $(e.target.closest('div.panel-body'));
    return getTemplate("field", function (tpl) {
        var field = $(tpl.render({"fields": e.data.fields}));
        field.fadeIn('slow');
        panelBody.append(field);
        field.find('span.glyphicon-minus-sign').parent().on('click', function (e) {
            e.preventDefault();
            field.remove();
        });
    });
}

function submitProducts (e) {
    requestObject = {"product": []};
    $('div.product').each(function (productPanel) {
        product = {};
        $(this).children('form').each(function (fieldForm) {
            var fieldName = $(this).find('select.fieldName').find(':selected').text();
            fieldName = fieldName.replace(/ \(.*/, '');
            var fieldOperator = $(this).find('select.fieldOperator').find(':selected').text();
            var fieldValue = $(this).find('input.fieldValue').val();
            if (fieldValue != "") {
                product[fieldName] = fieldOperator + fieldValue;
            }
        });
        if (!$.isEmptyObject(product)) {
            requestObject["product"].push(product);
        }
    });

    var promise = findUser(requestObject);

    promise.success(function (response) {
        $('#request').html("<pre>" + JSON.stringify(requestObject, null, 2) + "</pre>");
        getTemplate("found", function (tpl) {
            var error = $(tpl.render(response));
            error.fadeIn('slow');
            $('#response').html(error);
        });
    });

    promise.error(function (response) {
        $('#request').html("<pre>" + JSON.stringify(requestObject, null, 2) + "</pre>");
        if (response.status == 400) {
            getTemplate("error", function (tpl) {
                var error = $(tpl.render({}));
                error.fadeIn('slow');
                $('#response').html(error);
            });
        } else if (response.status == 404) {
            getTemplate("notfound", function (tpl) {
                var error = $(tpl.render({}));
                error.fadeIn('slow');
                $('#response').html(error);
            });
        }
    });
}


$(window).ready(function () {

    getTemplate("body", function (tpl) {
        var body = $(tpl.render({}));
        body.fadeIn('slow');
        $('#content').prepend(body);
        $('#addProduct').on('click', addProduct);
        $('#submit').on('click', submitProducts);
        getTemplate("status", function (tpl) {
            var status = $(tpl.render({}));
            status.fadeIn('slow');
            $('#status').append(status);
        });
    }); // body

});
