'use strict';
var requireDir = require('require-dir'),
    gulp = require('gulp');
// Require all tasks in gulp/tasks, including subfolders
requireDir('./gulp/tasks', { recurse: true });

gulp.task('watch', ['watch:css', 'watch:js', 'watch:imgs']);
gulp.task('dist', ['dist:js', 'dist:css', 'dist:imgs']);