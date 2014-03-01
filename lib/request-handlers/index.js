'use strict';

exports.frontpage = function(req, res) {
  res.render('views/index', {page_title: res.header()});
};
