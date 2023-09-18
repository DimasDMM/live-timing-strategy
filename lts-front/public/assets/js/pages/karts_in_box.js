class KartsInBoxPage extends Page {
    constructor(apiUrl, eventName) {
        super(apiUrl, true);

        // Name of the event
        this.eventName = eventName;
        // Timestamp of last loaded data
        this.lastTime = 0;
        // Time for callbacks
        this.timeoutRequests = 5000;
        this.timeoutUpdateMsg = 50;
        // Limit results
        this.limitLastBox = 10;
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
                                that.updateKartsProbs(that);
                                that.updateLastKartsBox(that);
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

    updateKartsProbs(that) {
        that.counterLoadingData++;
        that.sendGetRequest(
            '/v1/events/' + encodeURIComponent(that.eventName) + '/karts-box/probs',
            function (data, textStatus, jqXHR) { that.successCallbackKartsProbs(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackKartsProbs(jqXHR, textStatus, errorThrown, that); }
        );
    }

    updateLastKartsBox(that) {
        that.counterLoadingData++;
        that.sendGetRequest(
            '/v1/events/' + encodeURIComponent(that.eventName) + '/karts-box/in/' + that.limitLastBox,
            function (data, textStatus, jqXHR) { that.successCallbackLastKartsBox(data, textStatus, jqXHR, that); },
            function (jqXHR, textStatus, errorThrown) { that.errorCallbackLastKartsBox(jqXHR, textStatus, errorThrown, that); }
        );
    }

    successCallbackKartsProbs(data, textStatus, jqXHR, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#msg-loading-karts-probs').addClass('hide');
        $('#msg-error-karts-probs').addClass('hide');

        let hasMediumStatus = false;
        let parsedProbs = {};
        for (let prob of data['data']) {
            if (prob['kart_status'] == 'medium') {
                hasMediumStatus = true;
            }
            if (!(prob['step'] in parsedProbs)) {
                parsedProbs[prob['step']] = {};
            }
            parsedProbs[prob['step']][prob['kart_status']] = prob['probability'];
        }
        
        let hasTableData = false;
        let tableHtml = that.getTableProbsStart(hasMediumStatus);
        for (let probStep in parsedProbs) {
            let probData = parsedProbs[probStep];

            hasTableData = true;
            tableHtml += that.getTableProbsRow(
                that,
                hasMediumStatus,
                probStep,
                'unknown' in probData ? probData['unknown'] : 0,
                'good' in probData ? probData['good'] : 0,
                'medium' in probData ? probData['medium'] : 0,
                'bad' in probData ? probData['bad'] : 0
            );
        }
        tableHtml += that.getTableProbsEnd();

        if (hasTableData) {
            $('#msg-no-data-karts-probs').addClass('hide');
            $('#karts-probs-table').html(tableHtml);
        } else {
            $('#msg-no-data-karts-probs').removeClass('hide');
        }
    }

    errorCallbackKartsProbs(jqXHR, textStatus, errorThrown, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#msg-error-karts-probs').removeClass('hide');
    }

    successCallbackLastKartsBox(data, textStatus, jqXHR, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#msg-loading-last-box').addClass('hide');
        $('#msg-error-last-box').addClass('hide');
        
        let hasTableData = false;
        let tableHtml = that.getTableLastBoxStart();
        for (let lastBoxData of data['data']) {
            hasTableData = true;
            tableHtml += that.getTableLastBoxRow(
                that,
                lastBoxData['kart_status'],
                lastBoxData['forced_kart_status'],
                lastBoxData['team_name']
            );
        }
        tableHtml += that.getTableLastBoxEnd();

        if (hasTableData) {
            $('#msg-no-data-last-box').addClass('hide');
            $('#last-box-table').html(tableHtml);
        } else {
            $('#msg-no-data-last-box').removeClass('hide');
        }
    }

    errorCallbackLastKarsuccessCallbackLastKartsBox(jqXHR, textStatus, errorThrown, that) {
        that.counterLoadingData--;
        that.queueLoadingData--;
        $('#msg-error-last-box').removeClass('hide');
    }

    updateLastTime(that) {
        that.lastTime = new Date().getTime();
    }

    displayLoadingData() {
        $('#info-last-update').html('Actualizando...');
    }

    displayLastTimeLoadedData() {

    }

    getTableProbsStart(hasMedium = false) {
        return '' +
            '<table class="table table-striped table-dark table-sm">' +
            '    <thead>' +
            '        <tr>' +
            '            <th scope="col">&nbsp;</th>' +
            '            <th scope="col" class="badge-primary">&nbsp;</th>' +
            '            <th scope="col" class="badge-success">&nbsp;</th>' +
            (hasMedium ? '            <th scope="col" class="badge-warning">&nbsp;</th>' : '') +
            '            <th scope="col" class="badge-danger">&nbsp;</th>' +
            '        </tr>' +
            '    </thead>' +
            '<tbody>';
    }

    getTableProbsRow(that, hasMediumStatus, step, probUnknownStatus, probGoodStatus, probMediumStatus, probBadStatus) {
        let tableRow = '<tr>';
        if (step == 0) {
            tableRow += '<th scope="row">Ahora</th>';
        } else {
            tableRow += '<th scope="row">+' + step + ' parada' + (step > 1 ? 's' : '') + '</th>';
        }

        tableRow += '<td>' + probUnknownStatus + '%</td>';
        tableRow += '<td>' + probGoodStatus + '%</td>';
        if (hasMediumStatus) {
            tableRow += '<td>' + probMediumStatus + '%</td>';
        }
        tableRow += '<td>' + probBadStatus + '%</td>';
        tableRow += '</tr>';

        return tableRow;
    }

    getTableProbsEnd() {
        return '</tbody></table>';
    }

    getTableLastBoxStart() {
        return '' +
            '<table class="table table-striped table-dark table-sm">' +
            '    <thead>' +
            '        <tr>' +
            '            <th scope="col">&nbsp;</th>' +
            '            <th scope="col">Equipo</th>' +
            '        </tr>' +
            '    </thead>' +
            '<tbody>';
    }

    getTableLastBoxRow(that, kartStatus, forcedKartStatus, teamName) {
        kartStatus = forcedKartStatus != null ? forcedKartStatus : kartStatus;

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
                badgeClass = 'badge-primary';
        }
        
        return '' +
            '<tr>' +
            '    <th scope="row" class="' + badgeClass + '">&nbsp;</th>' +
            '    <td>' + teamName + '</td>' +
            '</tr>';
    }

    getTableLastBoxEnd() {
        return '</tbody></table>';
    }
}


