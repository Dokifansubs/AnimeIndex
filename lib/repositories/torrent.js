'use strict';

var _ = require('lodash');
var mysql = require('./mysql');
var redis = require('./redis')('cache');
var helper = require('../helpers/torrent');

var table = exports.table = mysql.prefix + 'files';
var stable = exports.stable = 'xbt_files';
var ctable = exports.ctable = mysql.prefix + 'categories';

var getTorrents_query = 'SELECT ??, ??, ?? AS category_id, ??, ?? AS created, ??, ??, ??, ?? FROM ?? JOIN ?? ON ?? = ?? JOIN ?? ON ?? = ??';
var getTorrents_format = [
  //Select
  table + '.info_hash',
  ctable + '.name',
  ctable + '.id', //as category_id
  table + '.filename',
  table + '.data', //as created
  table + '.size',
  stable + '.leechers',
  stable + '.seeders',
  stable + '.completed',
  //From
  table,
  //Join
  stable,
  stable + '.info_hash',
  table + '.bin_hash',
  //Join
  ctable,
  ctable + '.id',
  table + '.category'
];

var allowed_sorts = {
  'size': table + '.size',
  'name': table + '.filename',
  'seed': stable + '.seeders',
  'leech': stable + '.leechers',
  'complete': stable + '.completed'
};

exports.getTorrents = function(options, cb) {
  //Chech if cb is null. If it is, we assume options is
  //our callback and options is empty.
  if (!cb && options) {
    cb = options;
    options = {};
  }
  if (!options) { options = {}; }

  //Get our query.
  var query = getTorrents_query;
  var format = _.clone(getTorrents_format);

  //Create our default options.
  var sort = 'DESC';
  var order_by = table + '.data';
  var per_page = options.per_page || 25;
  var page = options.page || 1;

  //Check if requesting specific sorting.
  if (options.sort) {
    //Support for ASC sorting be prefixing with + so
    //ASC order for dates would be '+date'
    if (options.sort[0] === '+') {
      sort = 'ASC';
      options.sort = options.sort.slice(1);
    }
    order_by = allowed_sorts[options.sort] || order_by;
  }

  //Check if we're querying specific category or name.
  if (options.category || options.query) {
    query += ' WHERE 1 = 1';

    //Append category to query if that is requested.
    if (options.category) {
      query += ' AND ?? = ?';
      format.push(ctable + '.id', Number(options.category) || 0);
    }

    //Append filename to query if that is requested.
    if (options.query) {
      query += ' AND ?? LIKE ?';
      //Replace all spaces with % to allow for multi word searching.
      format.push(table + '.filename', '%' + options.query.replace(/\ /g, '%') + '%');
    }
  }
  
  //Append our sort order
  query += ' ORDER BY ?? ' + sort;
  query += ' LIMIT ?, ?';
  format.push(order_by, (page - 1) * per_page, per_page);

  //Check if we're running default options.
  if (!options.query && !options.category && order_by === table + '.data' && sort === 'DESC' && page === 1 && per_page === 25) {
    //If we're running default options, there is a chance we may
    //already have it cached. Check it.
    redis.SMEMBERS('torrent_list_default', function(err, res) {
      if (err) {
        console.log('Error while getting list from cache:', err);
        return runMySQL();
      }

      //Check if we have it cached.
      if (!res || res.length === 0) {
        return runMySQL();
      }
      
      //Get all the items from cache.
      redis.multi(
        res.map(function(item) { return ['hgetall', item]; })
      ).exec(function(err, res) {
        if (err) {
          console.log('Error while getting from cache:', err);
          return runMySQL();
        }

        //Check if we have full list of items (some might have expired/been removed)
        if (_.indexOf(res, null) > -1) {
          console.log('Found empty entries in cache. Querying mysql.');
          return runMySQL();
        }

        //Return our list. We sort by time because the cache
        //list might be in any order: http://redis.io/commands/sadd
        res.sort(function(a, b) { return new Date(b.created) - new Date(a.created); });
        cb(null, helper.format(res));
      });
    });
  } else {
    runMySQL();
  }

  function runMySQL() {
    mysql.query(mysql.format(query, format), function(err, rows) {
      if (err) { return cb(err); }

      //Check if we're running default options
      if (!options.query && !options.category && order_by === table + '.data' && sort === 'DESC' && page === 1 && per_page === 25) {
        //Cache!
        redis.multi([
          ['DEL', 'torrent_list_default'],
          ['SADD', 'torrent_list_default', _.pluck(rows, 'info_hash').map(function(item) { return 'torrent_item:' + item; })],
          //Expire list in 3 hours.
          ['EXPIRE', 'torrent_list_default', 60*60*3]
        ]).exec(function(err) {
          if (err) {
            return console.log('Error while preparing to cache torrents:', err);
          }
          redis.multi(
            //Insert all items to cache
            rows.map(function(item) { return ['hmset', 'torrent_item:' + item.info_hash, item]; }).concat(
            //Expire them in 3 hours.
            rows.map(function(item) { return ['EXPIRE', 'torrent_item:' + item.info_hash, 60*60*3]; }))
          ).exec(function(err) {
            if (err) {
              console.log('Error while caching torrent items:', err);
            }
          });
        });
      }
      cb(null, helper.format(rows));
    });
  }
};
