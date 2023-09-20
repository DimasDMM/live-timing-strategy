class CompetitionsOverviewPage extends Page {
    constructor(apiUrl, competitionCode) {
        super(apiUrl, true);

        // Name of the event
        this.competitionId = null
        this.competitionName = null
        this.competitionDescription = null
        this.competitionCode = competitionCode;
        this.competitionTeams = {}

        // Time for callbacks
        this.timeoutRequests = 5000;

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
            function (data, textStatus, jqXHR) {
                that.successCallbackCompetitionInitData(data, textStatus, jqXHR, that);
            },
            function (jqXHR, textStatus, errorThrown) {
                that.errorCallbackCompetitionInitData(jqXHR, textStatus, errorThrown, that);
            }
        );
    }

    successCallbackCompetitionInitData(data, textStatus, jqXHR, that) {
        that.competitionId = data['id']
        that.competitionName = data['name']
        that.competitionDescription = data['description']

        $('#title-competition-name').html(that.competitionName);

        that.refreshTimingData(that, true)
    }

    errorCallbackCompetitionInitData(jqXHR, textStatus, errorThrown, that) {
        window.location.href = '/competitions-index';
    }

    async refreshTimingData(that, firstTime = false) {
        let timeoutRequests = firstTime ? 0 : that.timeoutRequests;
        await that.sleep(timeoutRequests)

        $('#info-last-update-timing').html('Actualizando live-timing...');
        that.sendGetRequest(
            '/c/' + that.competitionId + '/timing',
            that.getBearer(),
            function (data, textStatus, jqXHR) {
                that.successCallbackTimingData(data, textStatus, jqXHR, that, firstTime);
            },
            function (jqXHR, textStatus, errorThrown) {
                that.errorCallbackTimingData(jqXHR, textStatus, errorThrown, that);
            }
        );
    }

    async refreshTeamsData(that, firstTime = false) {
        let timeoutRequests = firstTime ? 0 : that.timeoutRequests;
        await that.sleep(timeoutRequests)

        that.sendGetRequest(
            '/c/' + that.competitionId + '/teams',
            that.getBearer(),
            function (data, textStatus, jqXHR) {
                that.successCallbackTeamsData(data, textStatus, jqXHR, that, firstTime);
            },
            function (jqXHR, textStatus, errorThrown) {
                that.errorCallbackTeamsData(jqXHR, textStatus, errorThrown, that);
            }
        );
    }

    async refreshStatsData(that, firstTime = false) {
        let timeoutRequests = firstTime ? 0 : that.timeoutRequests;
        await that.sleep(timeoutRequests)

        that.sendGetRequest(
            '/c/' + that.competitionId + '/stats',
            that.getBearer(),
            function (data, textStatus, jqXHR) {
                that.successCallbackStats(data, textStatus, jqXHR, that, firstTime);
            },
            function (jqXHR, textStatus, errorThrown) {
                that.errorCallbackStats(jqXHR, textStatus, errorThrown, that);
            }
        );
    }

    successCallbackTimingData(data, textStatus, jqXHR, that, firstTime) {
        $('#msg-loading-timing').addClass('hide');
        $('#msg-error-timing').addClass('hide');
        
        let hasTableData = false;
        let tableHtml = that.getTableStart();
        for (let timingData of data) {
            hasTableData = true;
            tableHtml += that.getTableRow(
                that,
                timingData['kart_status'],
                timingData['fixed_kart_status'],
                timingData['position'],
                timingData['team_id'],
                timingData['lap'],
                timingData['best_time'],
                timingData['last_time'],
                timingData['interval'],
                timingData['interval_unit'],
                timingData['number_pits']
            );
        }
        tableHtml += that.getTableEnd();

        if (hasTableData) {
            $('#msg-no-data-timing').addClass('hide');
            $('#timing-table').html(tableHtml);
        } else {
            $('#msg-no-data-timing').removeClass('hide');
        }

        $('#info-last-update-timing').html('Actualizado');
        that.refreshTimingData(that, false)

        if (firstTime) {
            that.refreshTeamsData(that, true)
        }
    }

    errorCallbackTimingData(jqXHR, textStatus, errorThrown, that) {
        $('#msg-error-timing').removeClass('hide');
        $('#info-last-update-timing').html('Actualizado');
        that.refreshTimingData(that, false)
    }

    successCallbackTeamsData(data, textStatus, jqXHR, that, firstTime) {
        for (let teamData of data) {
            that.competitionTeams[teamData['id']] = {
                'id': teamData['id'],
                'participant_code': teamData['participant_code'],
                'name': teamData['name'],
                'number': teamData['number'],
            }
        }

        if (firstTime) {
            // The first time, apply changes manually instead of waiting to the
            // next call.
            that.applyChangesTeamData(that)
        }

        that.refreshTeamsData(that, false)
    }

    errorCallbackTeamsData(jqXHR, textStatus, errorThrown, that) {
        that.refreshTeamsData(that, false)
    }

    successCallbackStats(data, textStatus, jqXHR, that) {
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
        $('#stats-track-offset').html('--');
    }

    applyChangesTeamData(that) {
        for (let teamId in that.competitionTeams) {
            let teamData = that.competitionTeams[teamId]
            $('#timing-team-' + teamData.id + '-name').html(teamData.name);
        }
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
        teamId,
        lap,
        bestTime,
        lastTime,
        interval,
        interval_unit,
        numberPits
    ) {
        let teamName = that.getTeamName(that, teamId, '--')
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
        
        let htmlRow = '' +
            '<tr id="timing-team-' + teamId + '">' +
            '    <th scope="row" class="' + badgeClass + '">&nbsp;</th>' +
            '    <th id="timing-team-' + teamId + '-position">' + position + '</th>' +
            '    <td id="timing-team-' + teamId + '-name">' + teamName + '</td>' +
            '    <td id="timing-team-' + teamId + '-lap">' + lap + '</td>' +
            '    <td id="timing-team-' + teamId + '-best-time">' + that.getFormattedTime(bestTime) + '</td>' +
            '    <td id="timing-team-' + teamId + '-last-time">' + that.getFormattedTime(lastTime) + '</td>' +
            '    <td id="timing-team-' + teamId + '-interval">' + (interval > 0 ? that.getFormattedInterval(interval, interval_unit) : '-') + '</td>' +
            '    <td id="timing-team-' + teamId + '-number-pits">' + numberPits + '</td>' +
            '</tr>';

        return htmlRow
    }

    getTableEnd() {
        return '</tbody></table>';
    }

    getTeamName(that, teamId, defaultTeamName = '--') {
        if (that.competitionTeams[teamId]) {
            return that.competitionTeams[teamId].name
        }
        return defaultTeamName
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


