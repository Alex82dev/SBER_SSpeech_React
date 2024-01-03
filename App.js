import React, { useState } from 'react';

const App = () => {
  const [token, setToken] = useState('');
  const [text, setText] = useState('');
  const [outputFile, setOutputFile] = useState('');

  const handleSynthesize = () => {
    const data = {
      token: token,
      text: text,
      output_file: outputFile
    };

    fetch('/synthesize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        console.log('Speech synthesis successful');
      } else {
        console.log('Speech synthesis failed');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  return (
    <div>
      <input type="text" value={token} onChange={e => setToken(e.target.value)} placeholder="Access Token" />
      <input type="text" value={text} onChange={e => setText(e.target.value)} placeholder="Text to synthesize" />
      <input type="text" value={outputFile} onChange={e => setOutputFile(e.target.value)} placeholder="Output file" />
      <button onClick={handleSynthesize}>Synthesize</button>
    </div>
  );
};

export default App;
