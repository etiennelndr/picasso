function scrollto(div) {
    $('html,body').animate(
        {
            scrollTop: $('#' + div).offset().top,
        },
        'slow'
    );
}