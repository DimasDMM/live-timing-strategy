class Page {
    constructor(apiUrl) {
        this.apiUrl = 'http://' + apiUrl;
        this.initDefaultEvents();
    }

    initDefaultEvents() {
        let that = this;
        if ($('#btn-logout').length > 0) {
            $('#btn-logout').click(function (e) { that.eventLogout(e, that) });
        }
    }

    setToken(token) {
        this.token = token;
    }

    getToken() {
        return this.token;
    }

    sendGetRequest(path, successCallback, errorCallback) {
        let that = this
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
        window.location.href = '/';
    }
}
