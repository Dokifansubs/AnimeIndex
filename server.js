'use strict';

var express = require('express');
var bootstrap = require('bootstrap3-stylus');
var stylus = require('stylus');
var nib = require('nib');

var app = express();

function compile(str, path) {
  return stylus(str).set('filename', path).use(bootstrap()).use(nib()).import('nib');
}

//Core related middlehandlers
app.use(express.compress());
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.cookieParser());
app.use(express.cookieSession({secret: 'sdgni2ng2'}));
app.use(express.csrf());
app.use(express.favicon(__dirname + '/static/favicon.ico'));
app.set('views', __dirname + '/static/templates');
app.set('view engine', 'jade');
app.use(stylus.middleware({
  src: __dirname + '/static',
  force: true,
  debug:true,
  compile: compile
}));
app.use(express.static(__dirname + '/static'));

//Custom middle handlers
var common = require('./lib/helpers/common');
app.use(function(req, res, next) {
  res.header = common.header;
  next();
});

//Routes
var index = require('./lib/request-handlers/index');
app.get('/', index.frontpage);

var authenticate = require('./lib/request-handlers/authenticate');
app.get('/login', authenticate.form);

//Start the server
app.listen(3000, function() {
  console.log('listening on localhost:3000');
});
