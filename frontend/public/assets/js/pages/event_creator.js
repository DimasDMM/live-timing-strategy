class EventCreatorPage extends Page {
    constructor(apiUrl) {
        super(apiUrl, true);
        this.initElements();
        this.initEvents();
    }

    initElements() {
        if (Cookies.get('user_role') != 'admin') {
            window.location.href = '/'; // 401
        }
    }

    initEvents() {
        let that = this;
        $('#btn-create-event').click(function (e) { that.eventCreateEvent(e, that) });
    }

    eventCreateEvent(e, that) {
        e.preventDefault();
        $('#btn-create-event').attr('disabled', 'disabled').html('Enviando...');

        let formData = $('#form-event-creator').serializeArray();
        let parsedData = {};
        for (let item of formData) {
            let val = !isNaN(item['value']) ? parseInt(item['value']) : item['value'];
            let name = '';
            if (item['name'].match(/^configuration\_(.+)$/)) {
                if (!('configuration' in parsedData)) {
                    parsedData['configuration'] = {};
                }

                let name = item['name'].match(/^configuration\_(.+)$/)[1];
                parsedData['configuration'][name] = val;
            } else {
                name = item['name'];
                parsedData[name] = val;
            }
        }

        super.sendPostRequest(
            '/v1/events',
            parsedData,
            function (data, textStatus, jqXHR) { that.successCallbackCreateEvent(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackCreateEvent(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackCreateEvent(data, textStatus, jqXHR, that) {
        $('#btn-create-event').html('Redirigiendo...');
        window.location.href = '/event-index';
    }

    errorCallbackCreateEvent(jqXHR, textStatus, errorThrown, that) {
        if (errorThrown == 'Unauthorized') {
            window.location.href = '/'; // 401
        } else {
            that.displayError('Algo salió mal ¯\\_(ツ)_/¯');
        }

        $('#btn-create-event').removeAttr('disabled').html('Crear evento');
    }

    displayError(message) {
        $('#msg-error').removeClass('hide').html(message);
    }

    hideError() {
        $('#msg-error').addClass('hide');
    }
}
