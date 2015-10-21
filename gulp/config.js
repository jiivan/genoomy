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
        },
        vendorFiles: [
            vendorFile('jquery-datatables-columnfilter/jquery.dataTables.columnFilter.js'),
            vendorFile('select2/dist/js/select2.full.min.js'),
            vendorFile('jquery/dist/jquery.min.js'),
            vendorFile('datatables/media/js/jquery.dataTables.min.js')
        ]
    },
    clean: {
        distDir: distPath + '/'
    }
};