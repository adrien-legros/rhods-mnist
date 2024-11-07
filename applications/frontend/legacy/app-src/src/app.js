const express = require('express');
const bp = require('body-parser');
const https = require('https');

const path = require('path');
const app = express();

// Get env vars or defaults to model mesh serving on ODS
const knative_svc = process.env.KNATIVE_SVC || 'data-transformation';
const knative_port = process.env.KNATIVE_PORT || 443;
const knative_schema = process.env.KNATIVE_SCHEMA || "https";

app.use('/static', express.static(path.join(__dirname, 'static')))
app.use(bp.json())
app.use(bp.urlencoded({ extended: true }))

// sendFile will go here
app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, '/index.html'));
});

app.post('/predict', function(req, result) {
  console.log("Recieving data: ", req.body.data);
  const postData = JSON.stringify({
    'png': req.body.data,
  });
  var options = {
    host: knative_svc,
    port: knative_port,
    protocol: knative_schema + ':',
    path: '/',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  };
  console.log("options: ", options);
  var prediction;
  let data = [];
  var req = https.request(options, function(res) {
    console.log('STATUS: ' + res.statusCode);
    console.log('HEADERS: ' + JSON.stringify(res.headers));
    res.setEncoding('utf8');
    res.on('data', function (chunk) {
      console.log('BODY: ' + chunk);
      prediction = JSON.parse(chunk);
      result.send({'result': 'true', 'data': prediction.data});
    });
  });
  
  req.on('error', function(e) {
    console.log('problem with request: ' + e.message);
  });
  
  // write data to request body
  req.write(postData);
  req.end();
});

app.listen(8080);
console.log('Server started at https://localhost:8080');