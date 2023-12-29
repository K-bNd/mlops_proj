function transcribeAudio() {
    // Get audio URL from the form
    const audioUrl = document.getElementById('audioUrl').value;

    // Get the uploaded audio file
    const audioFile = document.getElementById('audioFile').files[0];

    // Check if either audio URL or file is provided
    if (!audioUrl && !audioFile) {
        alert('Please provide either an audio URL or upload a file.');
        return;
    }

    if (audioUrl && audioFile) {
        alert('Please provide only one of audio URL or file.');
        return;
    }

    const formData = new FormData();

    if (audioFile) {
        formData.append('audioFile', audioFile);
    }

    const endpoint = audioUrl ? `/url_transcript` : '/file_transcript';
    const data = audioUrl ? JSON.stringify({ file: audioUrl }) : formData;
    // Make a request to the FastAPI endpoint

    fetch(endpoint, {
        method: 'GET',
        body: formData,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update the result in the #transcription-result div
            document.getElementById('transcription-result').innerText = `Transcription: ${data.transcript}`;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            // Handle error, e.g., display an error message
            document.getElementById('transcription-result').innerText = 'Error transcribing audio';
        });
}
