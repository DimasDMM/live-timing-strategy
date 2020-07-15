class EventCreatorPage extends Page {
    constructor(apiUrl) {
        super(apiUrl, true);
        this.initElements();
        this.initData();
    }

    initElements() {
        if (Cookies.get('user_role') != 'admin') {
            window.location.href = '/'; // 401
        }
    }

    initData() {
        // Nothing
    }
}
