'use strict';

var config = require('../../config/config.json');

exports.header = function() {
  var args = Array.prototype.slice.call(arguments);
  var out = config.title;
  for (var i = 0; i < args.length; i++) {
    out = args[i] + ' &laquo; ' + out;
  }
  return out;
};
