
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const topMainNavbar = document.querySelector('.top-main');
    const mainContent = document.getElementById('mainContent');
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const pageTitle = document.getElementById('pageTitle');
    const navLinks = document.querySelectorAll('aside nav a');

    
    let isDesktopSidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener("click", () => {
            const header = document.querySelector("header");
            
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle("open-mobile-sidebar");
                
                if (header) {
                    const currentMargin = header.style.marginTop;
                    
                    if (currentMargin === "655px") {
                        header.style.marginTop = "0px";
                    } else {
                        header.style.marginTop = "655px";
                    }
                }
            } else {
                if (header) header.style.marginTop = "0px";
                
                isDesktopSidebarCollapsed = !isDesktopSidebarCollapsed;
                applyDesktopSidebarState();
                localStorage.setItem("sidebarCollapsed", isDesktopSidebarCollapsed);
            }
        });
    }
    // if (toggleSidebarBtn) {
    //   toggleSidebarBtn.addEventListener("click", () => {
    //     if (window.innerWidth <= 768) {
    //         sidebar.classList.toggle("open-mobile-sidebar");
    //         // header = document.querySelector("header").style.marginTop
    //         // console.log(header);
    //         // if (header === "655px" && window.innerWidth <= 768) {
    //         //     header = "0px";
    //         // }
    //         // else if (header === "0px" && window.innerWidth <= 768) {
    //         //     header = "655px";
                
    //         // }

            
    //     } else {
    //         document.querySelector("header").style.marginTop = "0px";
    //       isDesktopSidebarCollapsed = !isDesktopSidebarCollapsed;
    
    //       applyDesktopSidebarState();
    
    //       localStorage.setItem("sidebarCollapsed", isDesktopSidebarCollapsed);
    //     }
    //   });
    // }
    function updatePageTitle(title) {
        if (pageTitle) {
            pageTitle.textContent = title;
        }
    }

    
    function applyDesktopSidebarState() {
        if (isDesktopSidebarCollapsed) {
            topMainNavbar.style.marginRight = "85px"; 
            sidebar.classList.add('sidebar-collapsed');
            mainContent.classList.add('main-content-collapsed');
        } else {
            topMainNavbar.style.marginRight = "256px"; 
            sidebar.classList.remove('sidebar-collapsed');
            mainContent.classList.remove('main-content-collapsed');
        }
    }

    
    function resetMobileSidebarState() {
        sidebar.classList.remove('open-mobile-sidebar'); 
        
        sidebar.style.position = '';
        sidebar.style.height = '';
        sidebar.style.width = '';
        sidebar.style.top = '';
        sidebar.style.right = '';        
    }

    
    function handleLayoutOnLoadAndResize() {
        if (window.innerWidth > 768) {
            
            resetMobileSidebarState();
            
            applyDesktopSidebarState();
        } else {
            
            sidebar.classList.remove('sidebar-collapsed');
            mainContent.classList.remove('main-content-collapsed');
            topMainNavbar.style.marginRight = ''; 
            
        }
    }

    
    handleLayoutOnLoadAndResize();

    
    window.addEventListener('resize', handleLayoutOnLoadAndResize);

    
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        const linkPageTitle = link.dataset.pageTitle;

        if (linkHref === currentPath || (currentPath === '/' && linkPageTitle === 'لوحة التحكم')) {
            link.classList.add('text-indigo-300', 'bg-indigo-800');
            link.classList.remove('text-gray-300');
            updatePageTitle(linkPageTitle);
        } else {
            link.classList.remove('text-indigo-300', 'bg-indigo-800');
            link.classList.add('text-gray-300');
        }

        
        link.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open-mobile-sidebar'); 
            }

            
            navLinks.forEach(item => {
                item.classList.remove('text-indigo-300', 'bg-indigo-800');
                item.classList.add('text-gray-300');
            });

            
            this.classList.add('text-indigo-300', 'bg-indigo-800');
            this.classList.remove('text-gray-300');

            updatePageTitle(this.dataset.pageTitle);
        });
    });

    
    
});