class OverviewPage extends Page {
    constructor(apiUrl, eventName) {
        super(apiUrl, true);

        // Name of the event
        this.eventName = eventName;
        // Timestamp of last loaded data
        this.lastTime = 0;
        // Time for callbacks
        this.timeoutRequests = 5000;
        this.timeoutUpdateMsg = 50;
        // Counter to know how many process are updating data
        this.counterLoadingData = 0;
        this.queueLoadingData = 0;

        this.initEvents();
        this.initData();
    }

    initEvents() {
        // Nothing
    }

    initData() {
        this.updateData(true);
    }

    updateData(firstTime = false) {
        let that = this;
        let timeoutRequests = firstTime ? 0 : this.timeoutRequests;
        let timeoutUpdateMsg = firstTime ? 0 : this.timeoutUpdateMsg;
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
                that.updateData();
            },
            timeoutUpdateMsg
        );
    }

    updateTimingData(that) {
        that.counterLoadingData++;
        that.sendGetRequest(
            '/v1/events/' + encodeURIComponent(that.eventName) + '/timing/all/onlap',
            function (data, textStatus, jqXHR) { that.successCallbackTiming(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackTiming(jqXHR, textStatus, errorThrown, that); }
        );
    }

    updateStatsData(that) {
        that.counterLoadingData++;
        that.sendGetRequest(
            '/v1/events/' + encodeURIComponent(that.eventName) + '/stats',
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
                timingData['time'],
                timingData['gap']
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
            let offsetTime = that.getFormattedTime(statsData['reference_current_offset']);
            let symbol = statsData['reference_current_offset'] >= 0 ? '+' : '-';
            $('#stats-track-offset').html(symbol + offsetTime + ' seg');
        }
    }

    errorCallbackTiming(jqXHR, textStatus, errorThrown, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#stats-track-offset').html('--');
    }

    updateLastTime(that) {
        that.lastTime = new Date().getTime();
    }

    displayLoadingData() {
        $('#info-last-update').html('Actualizando...');
    }

    displayLastTimeLoadedData() {

    }

    getTableStart() {
        return '' +
            '<table class="table table-striped table-dark table-sm">' +
            '    <thead>' +
            '        <tr>' +
            '            <th scope="col">Cal.</th>' +
            '            <th scope="col">Pos.</th>' +
            '            <th scope="col">Equipo</th>' +
            '            <th scope="col">Última vuelta</th>' +
            '            <th scope="col">Gap</th>' +
            '        </tr>' +
            '    </thead>' +
            '<tbody>';
    }

    getTableRow(that, kartStatus, kartStatusGuess, position, teamName, lapTime, gap) {
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
            '    <td>' + that.getFormattedTime(lapTime) + '</td>' +
            '    <td>' + (gap > 0 ? '+' + that.getFormattedTime(gap) : '-') + '</td>' +
            '</tr>'
    }

    getTableEnd() {
        return '</tbody></table>';
    }

    getFormattedTime(time) {
        let milli = time % 1000;
        time = Math.trunc(time / 1000);
        let seconds = time % 60;
        let minutes = Math.trunc(time / 60);
        
        let formatted = '';
        let hasPrev = false;
        if (minutes > 0) {
            formatted += minutes + ':';
            hasPrev = true;
        }

        if (hasPrev) {
            formatted += (seconds >= 10 ? seconds : ('0' + seconds)) + '.';
        } else {
            formatted += seconds + '.';
        }

        formatted += milli >= 100 ? milli : (milli >= 10 ? '0' + milli : '00' + milli);

        return formatted;
    }
}

