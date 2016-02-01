function keyUpValidate(e) {
    var element = $(e.target);
    var grandParent = element.parent().parent();
    if (validateInput(element)) {
        grandParent.removeClass("has-error");
        grandParent.addClass("has-success");
    } else {
        grandParent.removeClass("has-success");
        grandParent.addClass("has-error");
    }
}

function validateInput(element) {
    if (element.attr("type") != "radio") {
        var type = element.attr("class");
        var val = element.val();
        if (val !== '') {
            var grandParent = element.parent().parent();
            if (type.indexOf("float") > -1 || type.indexOf("int") > -1) {
                if (/^[>=<0-9\.]+$/.test(val)) {
                    return true;
                }
            } else if (type.indexOf("str") > -1) {
                if (/^[A-Za-z0-9 ]+$/.test(val)) {
                    return true;
                }
            }
            return false;
        }
    }
    return true;
}


$(window).ready(function () {

    getProductModel().success(function (response) {
        var keys = Object.keys(response);
        keys.sort()

        $('#content').empty();
        $('#content').append('<div class="panel panel-default"><div class="panel-heading"><h3>Find User</h3></div><div class="panel-body"></div><div class="panel-footer"><button id="submit" class="btn btn-primary btn-lg" style="display: block; width: 100%;">Find User</button></div>');
        $('#content div.panel-body').append('<form class="form-horizontal">');

        $.each(keys, function(idx) {
            var k = keys[idx]
            var v = response[k]
            var element;
            if (v == "str") {
                element = '<div class="form-group"><label for="' + k + '" class="control-label col-sm-2">' + k + '</label><div class="col-sm-10"><input id="' + k + '" class="form-control input-sm ' + v + '" type="text" placeholder="' + k + '"/></div></div>';
            } else if (v == "int" || v == "float") {
                element = '<div class="form-group"><label for="' + k + '" class="control-label col-sm-2">' + k + '</label><div class="col-sm-10"><input id="' + k + '" class="form-control input-sm ' + v + '" type="text" placeholder="' + k + '"/></div></div>';
            } else if (v == "bool") {
                element = '<div class="form-group"><label class="control-label col-sm-2">' + k + '</label><div class="col-sm-10"><label class="radio-inline"><input type="radio" name="optradio' + k + '"/>True</label><label class="radio-inline"><input type="radio" name="optradio' + k + '"/>False</label></div></div>';
            }
            element = $(element);
            element.on('keyup', keyUpValidate);
            $('#content form.form-horizontal').append(element);
        });

        $('button#submit').on('click', function (e) {
            var inputs = $('form.form-horizontal').find(':input');
            var errors = 0;
            $.each(inputs, function (idx) {
                var element = $(inputs[idx]);
                if (validateInput(element) == false) {
                    errors = errors + 1;
                }
            });
            if (errors <= 0) {
                var jsonObject = {};
                $.each(inputs, function (idx) {
                    var element = $(inputs[idx]);
                    if (element.attr("type") == "radio") {
                        if (element.is(':checked')) {
                            jsonObject[element.attr("name").replace('optradio', '')] = element.parent().text();
                        }
                    } else {
                        if (element.val() != "") {
                            jsonObject[element.attr("id")] = element.val();
                        }
                    }
                });
                findUser(jsonObject).error(function (response) {
                    if (response.status == 400) {
                        var element = '<img alt="not found" width="300" height="300" src="/simba.png"/><h3>No encuentro to usuario.</h3>';
                        $('#status').hide();
                        $('#status').html($(element));
                        $('#status').fadeIn();
                    }
                }).success(function (response) {
                    var element = '<img alt="found" width="300" height="300" src="/jsral.jpg"/><h3>El usuario que buscas es el ' + response + '</h3>';
                    $('#status').hide();
                    $('#status').html($(element));
                    $('#status').fadeIn();
                });
            } else {
                var element = '<img alt="invalid" width="300" height="300" src="/grumpycat.jpg"/><h3>Informe tiene errores.</h3>';
                $('#status').hide();
                $('#status').html($(element));
                $('#status').fadeIn();
            }
        });

    });

});
