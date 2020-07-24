class ConfigurationPage extends Page {
    constructor(apiUrl, eventName) {
        super(apiUrl, true);

        // Name of the event
        this.eventName = eventName;

        this.initEvents();
        this.initData();
    }

    initEvents() {
        let that = this;
        $('#btn-modify-configuration').click(function (e) { that.eventModifyConfiguration(e, that) });
    }

    initData() {
        $('#info-last-update').html('Actualizado');
        let that = this;
        this.sendGetRequest(
            '/v1/events/' + encodeURIComponent(that.eventName) + '/configuration',
            function (data, textStatus, jqXHR) { that.successCallbackConfiguration(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackConfiguration(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackConfiguration(data, textStatus, jqXHR, that) {
        for (let item of data['data']) {
            $('input[name="configuration_' + item['name'] + '"]').val(item['value']);
        }

        $('#msg-loading').addClass('hide');
        $('#form-configuration').removeClass('hide');
    }

    errorCallbackConfiguration(jqXHR, textStatus, errorThrown, that) {
        $('#msg-loading').addClass('hide');
        $('#msg-error').removeClass('hide').html('No se han podido cargar los datos ¯\\_(ツ)_/¯');
    }

    eventModifyConfiguration(e, that) {
        e.preventDefault();
        $('#btn-modify-configuration').attr('disabled', 'disabled').html('Enviando...');
        $('#msg-success').addClass('hide');
        $('#msg-error').addClass('hide');

        let formData = $('#form-configuration').serializeArray();
        let parsedData = {};
        for (let item of formData) {
            let val = !isNaN(item['value']) ? parseInt(item['value']) : item['value'];
            let name = '';
            if (item['name'].match(/^configuration\_(.+)$/)) {
                let name = item['name'].match(/^configuration\_(.+)$/)[1];
                parsedData[name] = val;
            }
        }

        super.sendPutRequest(
            '/v1/events/' + encodeURIComponent(that.eventName) + '/configuration',
            parsedData,
            function (data, textStatus, jqXHR) { that.successCallbackModifyConfiguration(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackModifyConfiguration(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackModifyConfiguration(data, textStatus, jqXHR, that) {
        $('#msg-success').removeClass('hide');
        $('#btn-modify-configuration').removeAttr('disabled').html('Modificar parámetros');
    }

    errorCallbackModifyConfiguration(jqXHR, textStatus, errorThrown, that) {
        $('#msg-error').removeClass('hide').html('No se han podido modificar los datos ¯\\_(ツ)_/¯');
        $('#btn-modify-configuration').removeAttr('disabled').html('Modificar parámetros');
    }
}


