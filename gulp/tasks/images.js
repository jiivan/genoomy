'use strict';
var gulp = require('gulp'),
    imagemin = require('gulp-imagemin'),
    config = require('../config.js').images;

var tasks = {
    imgs: function() {
        return gulp.src(config.imagesDirs)
            .pipe(imagemin({
                progressive: true,
                svgoPlugins: [{removeViewBox: false}]
            }))
            .pipe(gulp.dest(config.imagesDest));
    }
};

gulp.task('dist:imgs', tasks.imgs);
gulp.task('watch:imgs', function () {
    gulp.watch(config.imagesDirs, ["dist:imgs"]);
});