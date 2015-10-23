'use strict';
var gulp = require('gulp'),
    sourcemaps = require('gulp-sourcemaps'),
    uglify = require('gulp-uglify'),
    concat = require('gulp-concat'),
    rename = require('gulp-rename'),
    config = require('../config.js').js;

var tasks = {
    jsCompileTask:function(name, filelist) {
        return function() {
            gulp.src(filelist)
                .pipe(sourcemaps.init())
                .pipe(concat(name + '.js'))
                .pipe(gulp.dest(config.dest))
                .pipe(uglify())
                .pipe(rename(name + '.min.js'))
                .pipe(sourcemaps.write('.'))
                .pipe(gulp.dest(config.dest));
        };
    },
    jsWatchTask:function (name, fileList) {
        return function(){
            gulp.watch(fileList, ["dist:js:" + name]);
        };
    }
};

function jsCompileDistros(){
    var compileTask, watchTask, fileList, jsDistroNames = [];
    for (var distroName in config.jsDistros) {
        fileList = config.jsDistros[distroName];

        compileTask = tasks.jsCompileTask(distroName, fileList);
        watchTask = tasks.jsWatchTask(distroName, fileList);
        gulp.task('dist:js:' + distroName, compileTask);
        gulp.task('watch:js:' + distroName, watchTask);

        jsDistroNames.push(distroName);
    }


    gulp.src(config.vendorFiles)
        .pipe(gulp.dest(config.dest));

    gulp.task('dist:js', jsDistroNames.map(function(n){ return 'dist:js:' + n;}));

    gulp.task("watch:js", jsDistroNames.map(function(n) { return "watch:js:" + n; }));
}

jsCompileDistros();