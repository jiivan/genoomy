'use strict';
var gulp = require('gulp'),
    config = require('../config.js').images;

var tasks = {
    imgs: function() {
        return gulp.src(config.imagesDirs)
            .pipe(gulp.dest(config.imagesDest));
    }
};

gulp.task('dist:imgs', tasks.imgs);