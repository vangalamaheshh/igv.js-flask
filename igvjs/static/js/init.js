function initBrowser(synergist_options) {
  var div,
      options,
      browser;

  div = $("#myDiv")[0];
  options = synergist_options;
  browser = igv.createBrowser(div, options);
}
