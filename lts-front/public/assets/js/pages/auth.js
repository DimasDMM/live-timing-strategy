class AuthPage extends Page {
    constructor(apiUrl) {
        super(apiUrl)
        this.initEvents()
    }

    initEvents() {
        let that = this;
        $('#btn-validate-token').click(function (e) {
            that.eventValidateToken(e, that)
        });
    }

    eventValidateToken(e, that) {
        e.preventDefault();
        let token = $('#account_token').val()
        if (token == '') {
            that.displayError('Token no válido.');
        }

        $('#btn-validate-token').attr('disabled', 'disabled').html('Validando...');
        that.hideError();
        super.sendPostRequest(
            '/auth',
            null,
            {'key': token},
            function (data, textStatus, jqXHR) {
                that.successCallbackAuth(token, data, textStatus, jqXHR, that);
            },
            function (jqXHR, textStatus, errorThrown) {
                that.errorCallbackAuth(jqXHR, textStatus, errorThrown, that);
            }
        );
    }

    successCallbackAuth(token, data, textStatus, jqXHR, that) {
        super.setCookiesData(data['bearer'], data['name'], data['role']);
        $('#btn-validate-token').html('Redirigiendo...');
        window.location.href = '/competitions-index';
    }

    errorCallbackAuth(jqXHR, textStatus, errorThrown, that) {
        if (errorThrown == 'Unauthorized') {
            that.displayError('Token no válido ¯\\_(ツ)_/¯');
        } else {
            that.displayError('Algo salió mal ¯\\_(ツ)_/¯');
        }
        $('#btn-validate-token').removeAttr('disabled').html('Entrar');
    }

    displayError(message) {
        $('#msg-error').removeClass('hide').html(message);
    }

    hideError() {
        $('#msg-error').addClass('hide');
    }
}


