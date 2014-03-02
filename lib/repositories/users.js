'use strict';

var mysql = require('./mysql');

exports.table = mysql.prefix + 'users';
