var gulp = require('gulp'),
    sourcemaps = require('gulp-sourcemaps'),
    concat = require('gulp-concat'),
    sass = require('gulp-sass'),
    minifyCss = require('gulp-minify-css'),
    postcss = require('gulp-postcss'),
    autoprefixer = require('autoprefixer-core'),
    config = require('../config.js').css;

var tasks = {
    css: function () {
        gulp.src(config.src)
            .pipe(sourcemaps.init())
            .pipe(sass().on('error', sass.logError))
            .pipe(postcss([autoprefixer({browsers: ['last 2 versions']})]))
            .pipe(concat(config.concatFilename))
            .pipe(minifyCss({compatibility: 'ie8'}))
            .pipe(sourcemaps.write('.'))
            .pipe(gulp.dest(config.dest));
    }
};

gulp.task('dist:css', tasks.css);
gulp.task('watch:css', function () {
    gulp.watch(config.src, ["dist:css"]);
});