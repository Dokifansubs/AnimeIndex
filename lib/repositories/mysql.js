'use strict';

var mysql = require('mysql');
var config = require('../../config/config.json');

var pool = mysql.createPool(config.mysql);
pool.prefix = config.mysql.prefix;
pool.format = mysql.format;
module.exports = pool;
