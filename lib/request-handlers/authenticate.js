'use strict';

exports.form = function(req, res) {
  res.render('views/auth/login', {page_title: res.header('Login')});
};
