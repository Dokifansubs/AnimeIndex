'use strict';

exports.frontpage = function(req, res) {
  res.render('index', {page_title: 'Test'});
};
