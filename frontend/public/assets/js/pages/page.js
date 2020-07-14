class Page {
    constructor(apiUrl, tokenValidation = false) {
        this.apiUrl = 'http://' + apiUrl;
        // Validate token and redirect if not valid
        this.tokenValidation = tokenValidation;
        // Timeout for callbacks
        this.timeout = 3000;

        this.loadCookiesData();
        this.initDefaultEvents();
        this.initDefaultTokenValidation();
    }

    loadCookiesData() {
        this.token = Cookies.get('user_token');
        this.userName = Cookies.get('user_name');
        this.userRole = Cookies.get('user_role');
    }

    initDefaultEvents() {
        let that = this;
        if ($('#btn-logout').length > 0) {
            $('#btn-logout').click(function (e) { that.eventLogout(e, that) });
        }
    }

    initDefaultTokenValidation() {
        if (!this.tokenValidation) {
            return;
        }

        if (this.getToken()) {
            let that = this;
            this.sendGetRequest(
                '/token/validate',
                function (data, textStatus, jqXHR) { that.successCallbackDefaultToken(data, textStatus, jqXHR, that); },
                function (jqXHR, textStatus, errorThrown) { that.errorCallbackDefaultToken(jqXHR, textStatus, errorThrown, that); }
            );
        }
    }

    successCallbackDefaultToken(data, textStatus, jqXHR, that) {
        that.setCookiesData(data['data']);
    }

    errorCallbackDefaultToken(jqXHR, textStatus, errorThrown, that) {
        if (errorThrown == 'Unauthorized') {
            that.setToken(null);
            that.unsetCookiesData();
        } else {
            that.redirectOffline();
        }
    }

    sendGetRequest(path, successCallback, errorCallback) {
        $.ajax({
            url: this.apiUrl + path,
            contentType: 'application/json; charset=utf-8',
            cache: false,
            crossDomain: true,
            type: 'GET',
            dataType: 'json',
            headers: {
                'X-Request-Id': this.getToken()
            }
        })
        .done(successCallback)
        .fail(errorCallback);
    }

    setToken(token) {
        this.token = token;
    }

    getToken() {
        return this.token;
    }

    setCookiesData(data) {
        Cookies.set('user_name', data['name']);
        Cookies.set('user_token', data['token']);
        Cookies.set('user_role', data['role']);
    }

    unsetCookiesData() {
        Cookies.set('user_name', null);
        Cookies.set('user_token', null);
        Cookies.set('user_role', null);
    }

    eventLogout(e, that) {
        $(e.target).html('<i class="fi fi-power"></i> Saliendo...').attr('disabled', 'disabled');
        that.unsetCookiesData();
        that.redirectOffline();
    }

    redirectOffline() {
        window.location.href = '/';
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
