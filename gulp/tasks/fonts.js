'use strict';
var gulp = require('gulp'),
    config = require('../config.js').fonts;

var tasks = {
    fonts: function() {
        return gulp.src(config.fontsDirs)
            .pipe(gulp.dest(config.fontsDestDir));
    }
};

//gulp.task('dist:fonts', tasks.fonts);
