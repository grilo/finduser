function addModel (e) {
    e.preventDefault();

    var modelName = e.data.name;
    var modelFields = e.data.fields;

    var keys = Object.keys(modelFields);
    keys.sort();
    var fields = [];
    $.each(keys, function (index, k) {
        fields.push(k + " (" + e.data.fields[k] + ")")
    });

    getTemplate("formModel", function (tpl) {
        //var fieldsControl = $(tpl.render({"fields": fields}));
        var fieldsControl = $(tpl.render({"model": modelName}));
        fieldsControl.find('button').on('click', function (e) {
            e.target.closest('div.panel').remove();
        });
        $('#' + modelName + 'List').prepend(fieldsControl);

        var e = {
            "target": fieldsControl.find('div.panel-body'),
            "data": { "fields": fields},
        };

        var panelBody = fieldsControl.find('div.panel-body');

        getTemplate("field", function (tpl) {
            var field = $(tpl.render({"fields": e.data.fields}));
            panelBody.append(field);
            field.fadeIn('slow');

            // We do some tomfoolery here for UX purposes
            // It breaks a million principles, but it's usable
            var button = fieldsControl.find('button.btn-danger');
            button.removeClass('btn-danger');
            button.addClass('btn-success');

            var span = button.find('span');
            span.removeClass('glyphicon-minus-sign');
            span.addClass('glyphicon-plus-sign');

            button.on('click', e.data, addField);

        });

    }); // model
}

function addField (e) {
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

function submitForm (e) {
    console.log(e.data);

    requestObject = {};

    var len = e.data.models.length;
    for (var i = 0; i < len ; i++) {
        var modelName = e.data.models[i];
        console.log(modelName);

        requestObject[modelName] = [];
        $('div.' + modelName).each(function (modelPanel) {
            model = {};
            $(this).children('form').each(function (fieldForm) {
                var fieldName = $(this).find('select.fieldName').find(':selected').text();
                fieldName = fieldName.replace(/ \(.*/, '');
                var fieldOperator = $(this).find('select.fieldOperator').find(':selected').text();
                var fieldValue = $(this).find('input.fieldValue').val();
                if (fieldValue != "") {
                    model[fieldName] = fieldOperator + fieldValue;
                }
            });
            if (!$.isEmptyObject(model)) {
                requestObject[modelName].push(model);
            }
        });
    }

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

        getDataModel().success(function (response) {
            for (var key in response) {
                var root = $('div.panel-body');
                getTemplate("addModel", function (tpl) {
                    var model = $(tpl.render({"model": key}));
                    model.fadeIn('slow');
                    root.append(model);
                    $('#add' + key).on('click', { name: key, fields: response[key] }, addModel);
                });
            }

            var models = Object.keys(response);
            $('#submit').on('click', {models: models}, submitForm);

        });

        getTemplate("status", function (tpl) {
            var status = $(tpl.render({}));
            status.fadeIn('slow');
            $('#status').append(status);
        });
    }); // body

});
