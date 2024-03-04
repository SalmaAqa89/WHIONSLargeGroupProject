var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
var recognition = new SpeechRecognition();

recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'en-US';

var toggleButton = document.getElementById('toggle-record-btn');
var isRecording = false; 
var journalEntryField = document.getElementById('id_text');
var ongoingTranscript = '';

toggleButton.addEventListener('click', () => {
  if (!isRecording) {
    recognition.start();
    toggleButton.style.backgroundColor = "red";
    isRecording = true;
  } else {
    recognition.stop();
    toggleButton.style.backgroundColor = "white";
    isRecording = false;
  }
});

recognition.onresult = function(event) {
  var interimTranscript = '';
  for (var i = event.resultIndex; i < event.results.length; ++i) {
    if (event.results[i].isFinal) {
      ongoingTranscript += event.results[i][0].transcript;
    } else {
      interimTranscript += event.results[i][0].transcript;
    }
  }
  journalEntryField.value = ongoingTranscript + interimTranscript;
};

recognition.onend = function() {
  toggleButton.style.backgroundColor = "white";
  isRecording = false;
};

recognition.onerror = function(event) {
  if(event.error == 'no-speech' || event.error == 'audio-capture') {
    alert("Error occurred: " + event.error + ". Try again.");
  };
  toggleButton.style.backgroundColor = "white";
  isRecording = false;
};