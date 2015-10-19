var path = require('path');

var staticRoot = 'genoome/static',
    distPath = staticRoot + '/dist';

function file(name) {
    return path.join(staticRoot, name);
}

function vendorFile(name) {
    return path.join(staticRoot, 'vendor', name);
}

module.exports = {
    css: {
        src: staticRoot + '/css/**/*.css',
        concatFilename: 'genoome.min.css',
        dest: distPath + '/css'
    },
    js: {
        dest: distPath + '/js',
        jsDistros: {
            genoome: [
                file('js/genoome.js')
            ]
        }
    },
    clean: {
        distDir: distPath + '/'
    }
};