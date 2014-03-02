'use strict';

var mysql = require('./mysql');
var redis = require('./redis')('cache');
var users = require('./users');

var table = exports.table = 'news';

var getTopNews_query = 'SELECT ??, ??, ??, ??, ??, ?? FROM ?? JOIN ?? ON ?? = ?? ORDER BY ?? DESC LIMIT 1';
getTopNews_query = mysql.format(getTopNews_query, [
  //Select
  table + '.id',
  table + '.user_id',
  table + '.created',
  table + '.title',
  table + '.content',
  users.table + '.username',
  //From
  table,
  users.table,
  //On
  table + '.user_id',
  users.table + '.id',
  //Order by
  table + '.created'
]);

exports.getTopNews = function(cb) {

  //Check to see if we already have it cached.
  redis.hgetall('cache:top_news', function(err, res) {
    //Return the cache if we have it.
    if (res) { return cb(null,  res); }

    //Otherwise query the mysql databse.
    mysql.query(getTopNews_query, function(err, rows) {
      if (err) { return cb(err); }

      //Store the result in redis.
      redis.hmset('cache:top_news', rows[0]);

      //Expire in 1 day.
      redis.EXPIRE('cache:top_news', 60*60*24);

      return cb(null, rows[0]);
    });
  });
};
