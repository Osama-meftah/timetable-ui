        const html = document.documentElement;
        const toggle = document.getElementById('darkModeToggle');

        const currentTheme = localStorage.getItem('theme');

        if (currentTheme === 'dark' || (!currentTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            html.classList.add('dark');
            toggle.checked = true;
        } else {
            html.classList.remove('dark');
            toggle.checked = false;
        }

        toggle.addEventListener('change', () => {
            if (toggle.checked) {
                html.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                html.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }
        });