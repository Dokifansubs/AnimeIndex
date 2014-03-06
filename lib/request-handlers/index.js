'use strict';

var async = require('async');
var news = require('../repositories/news');
var torrent = require('../repositories/torrent');

exports.frontpage = function(req, res, next) {
  async.parallel({
    news_item: news.getTopNews,
    torrent: torrent.getTorrents
  }, function(err, result) {
    if (err) { return next(err); }
    res.render('views/index', {
      page_title: res.header(),
      news_item: result.news_item,
      torrents: result.torrent,
      sort: 'date'
    });
  });
};
