window.onload = function() {
    var remainingBanners = document.getElementById('remaining-banners');
    var bottomContainer = document.querySelector('.page-bottom-infinity');
    var articleHeight = document.querySelector('.article').offsetHeight;
    var remainingBanners = document.querySelector('.remaining-banners');
    var remainingBannersHeight = remainingBanners.offsetHeight;
    var Banners = document.querySelectorAll('.banner-slot');

    remainingBanners.style.maxHeight = articleHeight + 'px';

    let totalHeight = 0;

    Banners.forEach(block => {
        totalHeight += block.offsetHeight + 20;
        if (totalHeight > remainingBanners.offsetHeight) {
            bottomContainer.appendChild(block);
    }
    })


}