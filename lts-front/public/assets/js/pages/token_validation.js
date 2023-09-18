class TokenValidationPage extends Page {
    constructor(apiUrl) {
        super(apiUrl)
        this.initEvents()
    }

    initEvents() {
        let that = this;
        $('#btn-validate-token').click(function (e) { that.eventValidateToken(e, that) });
    }

    eventValidateToken(e, that) {
        e.preventDefault();
        let token = $('#account_token').val()
        if (token == '') {
            that.displayError('Token no válido.');
        }

        super.setToken(token)
        $('#btn-validate-token').attr('disabled', 'disabled').html('Validando...');
        that.hideError();
        super.sendGetRequest(
            '/token/validate',
            function (data, textStatus, jqXHR) { that.successCallbackToken(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackToken(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackToken(data, textStatus, jqXHR, that) {
        super.setCookiesData(data['data']);
        $('#btn-validate-token').html('Redirigiendo...');
        window.location.href = '/event-index';
    }

    errorCallbackToken(jqXHR, textStatus, errorThrown, that) {
        if (errorThrown == 'Unauthorized') {
            that.displayError('Token no válido ¯\\_(ツ)_/¯');
        } else {
            that.displayError('Algo salió mal ¯\\_(ツ)_/¯');
        }

        that.setToken(null);
        $('#btn-validate-token').removeAttr('disabled').html('Validar token');
    }

    displayError(message) {
        $('#msg-error').removeClass('hide').html(message);
    }

    hideError() {
        $('#msg-error').addClass('hide');
    }
}


