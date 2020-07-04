var RefParser = require('json-schema-ref-parser');
var fs = require('fs');
var util = require('util');

if (process.argv.length < 3) {
    console.log(
        "Usage:"+
        "   $ node doc-builder.js <input-path> <output-path>" +
        "       * input-path:     Path to the index.json" +
        "       * output-path:    api-spec output path"
    );
    return;
}

var indexFilePath = process.argv[2];
var outputFilePath = process.argv[3];

RefParser.dereference(indexFilePath)
    .then(function(schema) {
        fs.writeFile(outputFilePath, JSON.stringify(schema, null, 2), 'utf8', function(err) {
          if(err) {
            return console.error(err);
          }
        });
    })
    .catch(function(err) {
        console.error(err);
    });
