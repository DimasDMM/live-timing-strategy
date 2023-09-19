class Page {
    constructor(apiUrl, bearerValidation = false) {
        this.apiUrl = apiUrl;
        // Validate token and redirect if not valid
        this.bearerValidation = bearerValidation;
        // Timeout for callbacks
        this.timeout = 3000;

        this.loadCookiesData();
        this.initDefaultEvents();
        this.initDefaultBearerValidation();
    }

    loadCookiesData() {
        this.bearer = Cookies.get('bearer');
        this.userName = Cookies.get('user_name');
        this.userRole = Cookies.get('user_role');
    }

    initDefaultEvents() {
        let that = this;
        if ($('#btn-logout').length > 0) {
            $('#btn-logout').click(function (e) { that.eventLogout(e, that) });
        }
    }

    initDefaultBearerValidation() {
        if (!this.bearerValidation) {
            return;
        }

        if (this.getBearer()) {
            let that = this;
            this.sendGetRequest(
                '/auth/validate',
                this.getBearer(),
                function (data, textStatus, jqXHR) { that.successCallbackDefaultAuth(data, textStatus, jqXHR, that); },
                function (jqXHR, textStatus, errorThrown) { that.errorCallbackDefaultAuth(jqXHR, textStatus, errorThrown, that); }
            );
        }
    }

    successCallbackDefaultAuth(data, textStatus, jqXHR, that) {
        that.setCookiesData(data['bearer'], data['name'], data['role']);
    }

    errorCallbackDefaultAuth(jqXHR, textStatus, errorThrown, that) {
        if (errorThrown == 'Unauthorized') {
            that.setToken(null);
            that.unsetCookiesData();
        } else {
            that.redirectOffline();
        }
    }

    sendGetRequest(path, authorization, successCallback, errorCallback) {
        let headers = {}
        if (authorization) {
            headers['Authorization'] = 'Bearer ' + authorization
        }

        $.ajax({
            url: this.apiUrl + path,
            contentType: 'application/json; charset=utf-8',
            cache: false,
            crossDomain: true,
            type: 'GET',
            dataType: 'json',
            headers: headers,
        })
        .done(successCallback)
        .fail(errorCallback);
    }

    sendPutRequest(path, authorization, data, successCallback, errorCallback) {
        let headers = {}
        if (authorization) {
            headers['Authorization'] = 'Bearer ' + authorization
        }

        $.ajax({
            url: this.apiUrl + path,
            contentType: 'application/json; charset=utf-8',
            cache: false,
            crossDomain: true,
            type: 'PUT',
            dataType: 'json',
            data: JSON.stringify(data),
            headers: headers,
        })
        .done(successCallback)
        .fail(errorCallback);
    }

    sendPostRequest(path, authorization, data, successCallback, errorCallback) {
        let headers = {}
        if (authorization) {
            headers['Authorization'] = 'Bearer ' + authorization
        }

        $.ajax({
            url: this.apiUrl + path,
            contentType: 'application/json; charset=utf-8',
            cache: false,
            crossDomain: true,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data),
            headers: headers,
        })
        .done(successCallback)
        .fail(errorCallback);
    }

    setBearer(bearer) {
        this.bearer = bearer;
    }

    getBearer() {
        return this.bearer;
    }

    setCookiesData(bearer, userName, userRole) {
        if (bearer) {
            Cookies.set('bearer', bearer);
        }
        Cookies.set('user_name', userName);
        Cookies.set('user_role', userRole);
    }

    unsetCookiesData() {
        Cookies.set('bearer', null);
        Cookies.set('user_name', null);
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
