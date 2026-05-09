const http = require('http');

http.get('http://127.0.0.1:5000/', (resp) => {
  let data = '';
  resp.on('data', (chunk) => { data += chunk; });
  resp.on('end', () => {
    console.log('AI Interviewer HTML exists:', data.includes('id="page-ai-interviewer"'));
    console.log('AI Interviewer nav link exists:', data.includes('ai-interviewer'));
  });
}).on("error", (err) => {
  console.log("Error: " + err.message);
});

http.get('http://127.0.0.1:5000/static/js/app.js', (resp) => {
  let data = '';
  resp.on('data', (chunk) => { data += chunk; });
  resp.on('end', () => {
    console.log('initAIInterviewer exists in JS:', data.includes('initAIInterviewer'));
  });
});
