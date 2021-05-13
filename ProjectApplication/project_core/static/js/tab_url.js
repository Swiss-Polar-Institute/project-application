$('a[data-toggle="tab"]').on("click", function () {
    const hash = $(this).attr("href").replace('#', '');

    var url = new window.URL(document.location);
    url.searchParams.set('tab', hash);

    window.history.pushState({}, '', url);
});
