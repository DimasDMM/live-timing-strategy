class CompetitionsOverviewPage extends Page {
    constructor(apiUrl, competitionCode) {
        super(apiUrl, true);

        // Name of the event
        this.competitionName = null
        this.competitionDescription = null
        this.competitionCode = competitionCode;

        // Timestamp of last loaded data
        this.lastTime = 0;

        // Time for callbacks
        this.timeoutRequests = 5000;
        this.timeoutRegreshMsg = 50;

        // Counter to know how many process are updating data
        this.counterLoadingData = 0;
        this.queueLoadingData = 0;

        this.initEvents();
        this.initData(competitionCode);
    }

    initEvents() {
        // Nothing
    }

    initData(competitionCode) {
        let that = this;
        this.sendGetRequest(
            '/c/filter/code/' + competitionCode,
            this.getBearer(),
            function (data, textStatus, jqXHR) { that.successCallbackCompetitionInitData(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackCompetitionInitData(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackCompetitionInitData(data, textStatus, jqXHR, that) {
        this.competitionName = data['name']
        this.competitionDescription = data['description']

        $('#title-competition-name').html(this.competitionName);

        this.refreshData(true)
    }

    errorCallbackCompetitionInitData(jqXHR, textStatus, errorThrown, that) {
        window.location.href = '/competitions-index';
    }

    refreshData(firstTime = false) {
        let that = this;
        let timeoutRequests = firstTime ? 0 : this.timeoutRequests;
        let timeoutRegreshMsg = firstTime ? 0 : this.timeoutRegreshMsg;
        setTimeout(
            function() {
                if (that.counterLoadingData > 0) {
                    $('#info-last-update').html('Actualizando ' + that.counterLoadingData + ' elemento(s)...');
                } else {
                    $('#info-last-update').html('Actualizado');
                    if (that.queueLoadingData == 0) {
                        that.queueLoadingData = 2;
                        setTimeout(
                            function() {
                                that.updateTimingData(that);
                                that.updateStatsData(that);
                            },
                            timeoutRequests
                        );
                    }
                }
                that.refreshData();
            },
            timeoutRegreshMsg
        );
    }

    updateTimingData(that) {
        that.counterLoadingData++;
        that.sendGetRequest(
            '/c/' + that.competitionCode + '/timing/all/onlap',
            function (data, textStatus, jqXHR) { that.successCallbackTiming(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackTiming(jqXHR, textStatus, errorThrown, that); }
        );
    }

    updateStatsData(that) {
        that.counterLoadingData++;
        that.sendGetRequest(
            '/c/' + that.competitionCode + '/stats',
            function (data, textStatus, jqXHR) { that.successCallbackStats(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackStats(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackTiming(data, textStatus, jqXHR, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#msg-loading-timing').addClass('hide');
        $('#msg-error-timing').addClass('hide');
        
        let hasTableData = false;
        let tableHtml = that.getTableStart();
        for (let timingData of data['data']) {
            hasTableData = true;
            tableHtml += that.getTableRow(
                that,
                timingData['kart_status'],
                timingData['kart_status_guess'],
                timingData['position'],
                timingData['team_name'],
                timingData['lap'],
                timingData['best_time'],
                timingData['time'],
                timingData['interval'],
                timingData['interval_unit'],
                timingData['number_stops']
            );
        }
        tableHtml += that.getTableEnd();

        if (hasTableData) {
            $('#msg-no-data-timing').addClass('hide');
            $('#timing-table').html(tableHtml);
        } else {
            $('#msg-no-data-timing').removeClass('hide');
        }
    }

    errorCallbackTiming(jqXHR, textStatus, errorThrown, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#msg-error-timing').removeClass('hide');
    }

    successCallbackStats(data, textStatus, jqXHR, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;

        let statsData = {};
        for (let item of data['data']) {
            statsData[item['name']] = item['value'];
        }

        if (statsData['status'] == 'offline') {
            $('#stats-track-offset').html('offline');
        } else {
            if (statsData['stage'] == 'race') {
                let offsetTime = that.getFormattedTime(Math.abs(statsData['reference_current_offset']));
                let symbol = statsData['reference_current_offset'] >= 0 ? '+' : '-';
                $('#stats-track-offset').html(symbol + offsetTime + ' seg');
            } else {
                $('#stats-track-offset').html('Aún no disponible');
            }
        }
    }

    errorCallbackStats(jqXHR, textStatus, errorThrown, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#stats-track-offset').html('--');
    }

    getTableStart() {
        return '' +
            '<table class="table table-striped table-dark table-sm">' +
            '    <thead>' +
            '        <tr>' +
            '            <th scope="col">&nbsp;</th>' +
            '            <th scope="col">Pos.</th>' +
            '            <th scope="col">Equipo</th>' +
            '            <th scope="col">Vuelta</th>' +
            '            <th scope="col">Mejor tiempo</th>' +
            '            <th scope="col">Última vuelta</th>' +
            '            <th scope="col">Interv.</th>' +
            '            <th scope="col">Pits</th>' +
            '        </tr>' +
            '    </thead>' +
            '<tbody>';
    }

    getTableRow(
        that,
        kartStatus,
        kartStatusGuess,
        position,
        teamName,
        lap,
        bestTime,
        lastTime,
        interval,
        interval_unit,
        numberStops
    ) {
        let badgeClass = ''
        switch (kartStatus) {
            case 'good':
                badgeClass = 'badge-success';
                break;
            case 'medium':
                badgeClass = 'badge-warning';
                break;
            case 'bad':
                badgeClass = 'badge-danger';
                break;
            default:
                if (kartStatusGuess == 'good') {
                    badgeClass = 'stripped-blue-success';
                } else if (kartStatusGuess == 'medium') {
                    badgeClass = 'stripped-blue-warning';
                } else if (kartStatusGuess == 'bad') {
                    badgeClass = 'stripped-blue-danger';
                } else {
                    badgeClass = 'badge-primary';
                }
        }
        
        return '' +
            '<tr>' +
            '    <th scope="row" class="' + badgeClass + '">&nbsp;</th>' +
            '    <th>' + position + '</th>' +
            '    <td>' + teamName + '</td>' +
            '    <td>' + lap + '</td>' +
            '    <td>' + that.getFormattedTime(bestTime) + '</td>' +
            '    <td>' + that.getFormattedTime(lastTime) + '</td>' +
            '    <td>' + (interval > 0 ? that.getFormattedInterval(interval, interval_unit) : '-') + '</td>' +
            '    <td>' + numberStops + '</td>' +
            '</tr>';
    }

    getTableEnd() {
        return '</tbody></table>';
    }
    
    getFormattedInterval(interval, interval_unit) {
        if (interval_unit == 'milli') {
            return '+' + this.getFormattedTime(interval);
        } else if (interval_unit == 'laps') {
            let str_interval = '+' + interval + ' ' + (interval > 1 ? 'vueltas' : 'vuelta');
            return str_interval;
        } else {
            return '??';
        }
    }
}


