class CompetitionsIndexPage extends Page {
    constructor(apiUrl) {
        super(apiUrl, true);
        this.initElements();
        this.initData();
    }

    initElements() {
        if (Cookies.get('user_role') == 'admin') {
            $('#btn-competitions-creator').removeClass('hide');
        }
    }

    initData() {
        this.initCompetitionsIndex();
    }

    // Load data about the current stage
    initCompetitionsIndex() {
        let that = this;
        this.sendGetRequest(
            '/c',
            this.getBearer(),
            function (data, textStatus, jqXHR) { that.successCallbackCompetitionsIndex(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackCompetitionsIndex(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackCompetitionsIndex(data, textStatus, jqXHR, that) {
        $('#competitions-index').html('');
        let hasCompetitionData = false;
        for (let competitionData of data) {
            hasCompetitionData = true;
            $('#competitions-index').append(
                '<div class="col-12 col-lg-4">' +
                '    <div class="card shadow-md shadow-lg-hover border-primary bl-0 br-0 bb-0 bw--2">' +
                '        <div class="card-body">' +
                '            <h5 class="card-title">' + competitionData['name'] + '</h5>' +
                '            <a href="/competitions/' + encodeURIComponent(competitionData['competition_code']) + '" class="btn btn-sm btn-primary btn-soft">' +
                '                <i class="fi fi-atom fs--20"></i>' +
                '                Abrir' +
                '            </a>' +
                '        </div>' +
                '    </div>' +
                '</div>'
            );
        }
        if (!hasCompetitionData) {
            $('#competitions-index').html(
                '<div class="col-12 col-lg-12 alert alert-primary bg-transparent bw--2" role="alert">' +
                '    No hay competiciones disponibles ¯\\_(ツ)_/¯' +
                '</div>'
            );
        }
    }

    errorCallbackCompetitionsIndex(jqXHR, textStatus, errorThrown, that) {
        $('#competitions-index').html(
            '<div class="col-12 col-lg-12 alert alert-danger bg-transparent bw--2" role="alert">' +
            '    <b>Error.</b> No se pueden cargar las competiciones disponibles.' +
            '</div>'
        );
    }
}
