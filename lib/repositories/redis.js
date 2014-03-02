'use strict';

var redis = require('redis');
var config = require('../../config/config.json');

var clients = {
  cache: redis.createClient(config.redis.cache.port, config.redis.cache.host),
  persistent: redis.createClient(config.redis.persistent.port, config.redis.persistent.host),
};

module.exports = function(type) {
  if (!clients[type]) {
    throw new Error('Error, unsupported redis type.');
  }
  return clients[type];
};
