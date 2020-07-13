class OverviewPage extends Page {
    constructor(apiUrl) {
        this.tokenValidation = true
        super(apiUrl);

        // Timestamp of last loaded data
        this.lastTime = 0;
        // Time for callbacks
        this.timeout = 3000;

        this.initEvents();
        this.initData();
    }

    initEvents() {
        // Nothing
    }

    initData() {
        this.initDataStage();
    }

    // Load data about the current stage
    initDataStage() {
        let that = this;
        setTimeout(
            function() {
                that.sendGetRequest(
                    '/token/validate',
                    function (data, textStatus, jqXHR) { that.successCallbackStage(data, textStatus, jqXHR, that); },
                    function (jqXHR, textStatus, errorThrown) { that.errorCallbackStage(jqXHR, textStatus, errorThrown, that); }
                );
            },
            this.timeout
        );
    }

    successCallbackStage(data, textStatus, jqXHR, that) {
        that.initDataStage();
    }

    errorCallbackStage(jqXHR, textStatus, errorThrown, that) {
        that.initDataStage();
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


