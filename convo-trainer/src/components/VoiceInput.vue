<template>
  <v-card class="fill-height">
    <v-card-text>
      <div id="info">
        <v-alert v-if="info_message === 'info_start'">Click on the microphone icon and begin speaking for as long as
          you like.</v-alert>
        <v-alert v-if="info_message === 'info_speak_now'" class="hidden">Speak now.</v-alert>
        <v-alert v-if="info_message === 'info_no_speech'" class="hidden" type="warning">
          No speech was detected. You may need to adjust your
          <a href="//support.google.com/chrome/bin/answer.py?hl=en&amp;answer=1407892">microphone settings</a>.
        </v-alert>
        <v-alert v-if="info_message === 'info_no_microphone'" class="hidden" type="error">
          No microphone was found. Ensure that a microphone is installed and that
          <a href="//support.google.com/chrome/bin/answer.py?hl=en&amp;answer=1407892">microphone settings</a> are
          configured correctly.
        </v-alert>
        <v-alert v-if="info_message === 'info_allow'" class="hidden">Click the "Allow" button above to enable your
          microphone.</v-alert>
        <v-alert v-if="info_message === 'info_denied'" class="hidden" type="error">Permission to use microphone was
          denied.</v-alert>
        <v-alert v-if="info_message === 'info_blocked'" class="hidden" type="error">
          Permission to use microphone is blocked. To change, go to chrome://settings/contentExceptions#media-stream
        </v-alert>
        <v-alert v-if="info_message === 'info_upgrade'" class="hidden" type="warning">
          Web Speech API is not supported by this browser. Upgrade to
          <a href="//www.google.com/chrome">Chrome</a> version 25 or later.
        </v-alert>
      </div>
      <v-row dense>
        <v-col>
          <div id="results" class="mt-2">
            <div id="final_span" variant="h6"></div>
            <div id="interim_span" variant="body1"></div>
          </div>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col sm="1" md="2" class="pb-3 pt-3">
          <v-btn size="x-large" id="start_button" color="primary" fab>
            <v-icon>{{ microphone_icon }}</v-icon>
          </v-btn>
        </v-col>
        <v-col>
          <audio id="recording-audio" class="float-left ma-2" controls>Your browser does not support the audio
            element.</audio>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col>
          <v-btn size="x-large" color="primary" @click="submitAudio">
            Analyze text
            <v-icon right>mdi-send</v-icon>
          </v-btn>
        </v-col>
        <v-col>
          <v-btn size="x-large" color="secondary" :href="get_deepl_link()" target="_blank">
            DeepL <v-icon right>mdi-open-in-new</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const props = defineProps(['language_code', 'timestamp'])

var recognition = new webkitSpeechRecognition();
var recognizing = false;
var dataChunks = [];
var blob = null;

var info_message = ref('info_start');

var microphone_icon = ref('mdi-microphone')
var final_transcript = '';
var ignore_onend;
var start_timestamp;
if (!('webkitSpeechRecognition' in window)) {
  upgrade();
} else {
  recognition.continuous = true;
  recognition.interimResults = false;

  recognition.onstart = function () {
    recognizing = true;
    info_message.value = 'info_speak_now';
  };

  recognition.onerror = function (event) {
    if (event.error == 'no-speech') {
      microphone_icon.value = 'mdi-microphone';
      info_message.value = 'info_no_speech';
      ignore_onend = true;
    }
    if (event.error == 'audio-capture') {
      microphone_icon.value = 'mdi-microphone';
      info_message.value = 'info_no_microphone';
      ignore_onend = true;
    }
    if (event.error == 'not-allowed') {
      if (event.timeStamp - start_timestamp < 100) {
        info_message.value = 'info_blocked';
      } else {
        info_message.value = 'info_denied';
      }
      ignore_onend = true;
    }
  };

  recognition.onend = function () {
    recognizing = false;
    if (ignore_onend) {
      return;
    }
    microphone_icon.value = 'mdi-microphone';
    if (!final_transcript) {
      info_message.value = 'info_start';
      return;
    }

    info_message.value = 'info_start';
  };

  recognition.onresult = function (event) {
    var interim_transcript = '';
    if (typeof (event.results) == 'undefined') {
      recognition.onend = null;
      recognition.stop();
      upgrade();
      return;
    }
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;
      } else {
        interim_transcript += event.results[i][0].transcript;
      }
    }
    final_transcript = capitalize(final_transcript);
    final_span.innerHTML = linebreak(final_transcript);
    interim_span.innerHTML = linebreak(interim_transcript);
  };
}

function upgrade() {
  start_button.style.visibility = 'hidden';
  info_message.value = 'info_upgrade';
}

var two_line = /\n\n/g;
var one_line = /\n/g;
function linebreak(s) {
  return s.replace(two_line, '<p></p>').replace(one_line, '<br>');
}

var first_char = /\S/;
function capitalize(s) {
  return s.replace(first_char, function (m) { return m.toUpperCase(); });
}

function startButton() {
  final_transcript = '';
  recognition.lang = props.language_code;
  try {
    recognition.start();
  } catch { }
  ignore_onend = false;
  final_span.innerHTML = '';
  interim_span.innerHTML = '';
  microphone_icon.value = 'mdi-microphone-off';
  info_message.value = 'info_allow';
  start_timestamp = Date.now();
}

function saveAudio(timestamp) {
  const fd = new FormData();
  fd.set('file', blob, timestamp + '.webm');
  fd.append("timestamp", timestamp);
  fd.append("language_code", props.language_code);
  fetch(import.meta.env.VITE_BASE_URL + '/upload', { method: 'POST', body: fd })
}

async function analyzeText(timestamp) {
  const fd = new FormData();
  fd.append("timestamp", timestamp);
  fd.append("text", final_transcript);
  fd.append("language_code", props.language_code);
  await fetch(import.meta.env.VITE_BASE_URL + '/analyze_text', { method: 'POST', body: fd })
}

const emit = defineEmits(["updateTimestamp"])
async function submitAudio() {
  const timestamp_now = Date.now()
  saveAudio(timestamp_now)
  await analyzeText(timestamp_now)

  emit("updateTimestamp", timestamp_now);
}

function get_deepl_link() {
  if (props.language_code == "de" || props.language_code == "en") {
    return "https://www.deepl.com/en/write#" + props.language_code + "/" + encodeURIComponent(final_transcript)
  } else {
    return "https://www.deepl.com/en/translator#" + props.language_code + "/en/" + encodeURIComponent(final_transcript)
  }
}

// Check the supported format to use
var format = (MediaRecorder.isTypeSupported('audio/webm; codecs=opus')) ? 'audio/webm; codecs=opus' : 'audio/ogg; codecs=opus';

// Check if media access is possible
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {

  // Get media access
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(function (stream) {
      var recorder = new MediaRecorder(stream);

      // Save recording data as it becomes available
      recorder.ondataavailable = function (e) {
        dataChunks.push(e.data);
      };

      // When recorder is stopped, let's capture the recording
      recorder.onstop = function (e) {
        var audioBlock = document.querySelector('#recording-audio');

        blob = new Blob(dataChunks, { type: format });
        dataChunks = [];

        var audioURL = window.URL.createObjectURL(blob);
        audioBlock.src = audioURL;

        recognition.stop();
      };

      var recordBtn = document.querySelector('#start_button');

      // Event for clicking record button
      recordBtn.addEventListener('click', function (e) {
        if (recognizing) {
          console.log('RECORD STOPPING');
          recorder.stop();
          return;
        }
        console.log('RECORD STARTING');
        recorder.start();
        startButton();
      });
    })
    .catch(function (err) {
      // Denied media access
      console.warn('Error occured when getting user media: ' + err);
    });

} else {
  console.warn('Media usage not supported');
}
</script>

<style>
body {
  margin: 0;
}

#info {
  font-size: 16px;
}

#results {
  font-size: 14px;
  font-weight: bold;
  border: 1px solid #ddd;
  padding: 15px;
  text-align: left;
  min-height: 150px;
}

.interim {
  color: gray;
}

.final {
  color: black;
  padding-right: 3px;
}

.hidden {
  display: none;
}
</style>