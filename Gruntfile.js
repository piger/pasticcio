module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        less: {
            development: {
                options: {
                    paths: ['pasticcio/static/css']
                },
                files: {
                    "pasticcio/static/css/pasticcio.min.css": "pasticcio/static/css/pasticcio.less"
                }
            }
        },
        watch: {
            css: {
                files: ['pasticcio/static/css/*.less'],
                tasks: ['less'],
                options: {
                    livereload: true
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['less', 'watch']);
};
