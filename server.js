'use strict';

var express = require('express');
var bootstrap = require('bootstrap3-stylus');
var stylus = require('stylus');
var nib = require('nib');

var app = express();

function compile(str, path) {
  return stylus(str).set('filename', path).use(bootstrap()).use(nib()).import('nib');
}

app.use(express.compress());
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.cookieParser());
app.use(express.cookieSession({secret: 'sdgni2ng2'}));
app.use(express.csrf());
app.use(express.static(__dirname + '/static'));
app.set('views', __dirname + '/static/templates');
app.set('view engine', 'jade');
app.use(stylus.middleware({
  src: __dirname + '/static',
  force: true,
  compile: compile
}));

var index = require('./lib/request-handlers/index');
app.get('/', index.frontpage);

app.listen(3000, function() {
  console.log('listening on localhost:3000');
});
