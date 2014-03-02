'use strict';

var news = require('../repositories/news');

exports.frontpage = function(req, res, next) {
  news.getTopNews(function(err, news_item) {
    if (err) { return next(err); }

    res.render('views/index', {
      page_title: res.header(),
      news_item:news_item
    });
  });
};
