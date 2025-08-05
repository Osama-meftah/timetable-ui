class SearchComponent {
    constructor(params) {
        this.input = document.querySelector(params.inputSelector);
        this.apiManager = params.apiManager; // كائن APIFormManager
        this.queryKey = params.queryKey || 'search'; // مفتاح الاستعلام مثل ?group=
        this.delay = params.delay || 300;
        this.timer = null;

        if (!this.input || !this.apiManager) {
            console.error("SearchComponent: inputSelector أو apiManager مفقود.");
            return;
        }

        this.init();
    }

    init() {
        this.input.addEventListener('input', () => {
            clearTimeout(this.timer);
            const value = this.input.value.trim();
            console.log(value)

            this.timer = setTimeout(() => {
                const query = {};
                query[this.queryKey] = value;
                this.apiManager.fetchData(query); // إرسال الاستعلام إلى APIFormManager
            }, this.delay);
        });
    }
}
