class TokenValidationPage extends Page {
    constructor(apiUrl) {
        super(apiUrl)
        this.setEvents()
    }

    setEvents() {
        document.getElementById('btn-validate-token').addEventListener('click', this.eventValidateToken);
    }

    eventValidateToken(e) {
        e.preventDefault();
        let token = document.getElementById('account_token').value
        console.log('Validate token: ' + token)
    }
}


