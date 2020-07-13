class EventIndexPage extends Page {
    constructor(apiUrl) {
        super(apiUrl, true);
        console.log('CHILD CONS');
        this.initEvents();
        this.initData();
    }

    initEvents() {
        // Nothing
    }

    initData() {
        this.initEventIndex();
    }

    // Load data about the current stage
    initEventIndex() {
        let that = this;
        this.sendGetRequest(
            '/v1/events',
            function (data, textStatus, jqXHR) { that.successCallbackEventIndex(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackEventIndex(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackEventIndex(data, textStatus, jqXHR, that) {
        $('#event-index').html('');
        for (let eventData of data['data']) {
            $('#event-index').append(
                '<div class="col-12 col-lg-4">' +
                '    <div class="card shadow-md shadow-lg-hover border-primary bl-0 br-0 bb-0 bw--2">' +
                '        <div class="card-body">' +
                '            <h5 class="card-title">' + eventData['name'] + '</h5>' +
                '            <a href="/event/' + encodeURIComponent(eventData['name']) + '" class="btn btn-sm btn-primary btn-soft">' +
                '                <i class="fi fi-atom fs--20"></i>' +
                '                Abrir' +
                '            </a>' +
                '        </div>' +
                '    </div>' +
                '</div>'
            );
        }
    }

    errorCallbackEventIndex(jqXHR, textStatus, errorThrown, that) {
        $('#event-index').html(
            '<div class="col-12 col-lg-12 alert alert-danger bg-transparent bw--2" role="alert">' +
            '    <b>Error.</b> No se pueden cargar los eventos disponibles.' +
            '</div>'
        );
    }

    updateLastTime(that) {
        that.lastTime = new Date().getTime();
    }

    displayLoadingData() {
        $('#info-last-update').html('Actualizando...');
    }

    displayLastTimeLoadedData() {

    }
}


