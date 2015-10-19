'use strict';
var gulp = require('gulp'),
    del = require('del'),
    config = require('../config.js').clean;

var tasks = {
    clean:function(cb){
        del([config.distDir], cb);
    }
};

gulp.task('clean', tasks.clean);

