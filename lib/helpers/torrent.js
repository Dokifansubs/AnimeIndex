'use strict';

var moment = require('moment');



var formatBytes = exports.formatBytes = function (bytes) {
  if (bytes === 0) return '0 KB';
  var sizes = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
  i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  return (+(bytes / Math.pow(1024, i)).toFixed(2)).toString() + ' ' + sizes[i];
};

exports.format = function(torrents) {
  for (var i = 0; i < torrents.length; i++) {
    var age = new moment(new Date()).diff(new moment(torrents[i].created), 'hour');
    if (age >= 48) {
      age = Math.floor(age / 24).toString() + ' days';
    } else {
      age = age.toString() + age === 1 ? 'hour' : ' hours';
    }
    torrents[i].age = age;
    torrents[i].friendly_size = formatBytes(torrents[i].size);

    torrents[i].name_prefix = torrents[i].name;
    if (torrents[i].name.indexOf('(') > -1) {
      torrents[i].name_prefix = torrents[i].name.slice(0, torrents[i].name.indexOf('(') - 1);
      var lang = torrents[i].name.slice(torrents[i].name.indexOf('(') + 1).slice(0, -1);
      torrents[i].name_suffix = lang === 'English' ? 'ENG' : 'Non-E';
    }
  }
  return torrents;
};