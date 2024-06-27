<template>
  <v-container>
    <v-card outlined>
      <v-card-title>
        Convo Trainer
      </v-card-title>
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
          <v-col class="v-col-sm-4">
            <v-select v-model="selected_language" label="Language" :items="languages" hide-details></v-select>
          </v-col>
          <!---<v-col class="v-col-sm-4">
            <v-select v-model="selected_dialect" label="Dialect" :items="dialects" hide-details
              v-if="dialects.length > 1"></v-select>
          </v-col>-->
        </v-row>
        <v-row dense>
          <v-col class="v-col-sm-1 pb-3 pt-3">
            <v-btn size="x-large" id="start_button" color="primary" fab @click="startButton">
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
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
  <progress-grid :language_code="current_language_code" :timestamp="timestamp"/>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

var recognition = new webkitSpeechRecognition();
var recognizing = false;
var dataChunks = [];
var blob = null;

// If you modify this array, also update default language / dialect below.
var langs =
  [['Afrikaans', ['af-ZA']],
  ['አማርኛ', ['am-ET']],
  ['Azərbaycanca', ['az-AZ']],
  ['বাংলা', ['bn-BD', 'বাংলাদেশ'],
    ['bn-IN', 'ভারত']],
  ['Bahasa Indonesia', ['id-ID']],
  ['Bahasa Melayu', ['ms-MY']],
  ['Català', ['ca-ES']],
  ['Čeština', ['cs-CZ']],
  ['Dansk', ['da-DK']],
  ['Deutsch', ['de-DE']],
  ['English', ['en-AU', 'Australia'],
    ['en-CA', 'Canada'],
    ['en-IN', 'India'],
    ['en-KE', 'Kenya'],
    ['en-TZ', 'Tanzania'],
    ['en-GH', 'Ghana'],
    ['en-NZ', 'New Zealand'],
    ['en-NG', 'Nigeria'],
    ['en-ZA', 'South Africa'],
    ['en-PH', 'Philippines'],
    ['en-GB', 'United Kingdom'],
    ['en-US', 'United States']],
  ['Español', ['es-AR', 'Argentina'],
    ['es-BO', 'Bolivia'],
    ['es-CL', 'Chile'],
    ['es-CO', 'Colombia'],
    ['es-CR', 'Costa Rica'],
    ['es-EC', 'Ecuador'],
    ['es-SV', 'El Salvador'],
    ['es-ES', 'España'],
    ['es-US', 'Estados Unidos'],
    ['es-GT', 'Guatemala'],
    ['es-HN', 'Honduras'],
    ['es-MX', 'México'],
    ['es-NI', 'Nicaragua'],
    ['es-PA', 'Panamá'],
    ['es-PY', 'Paraguay'],
    ['es-PE', 'Perú'],
    ['es-PR', 'Puerto Rico'],
    ['es-DO', 'República Dominicana'],
    ['es-UY', 'Uruguay'],
    ['es-VE', 'Venezuela']],
  ['Euskara', ['eu-ES']],
  ['Filipino', ['fil-PH']],
  ['Français', ['fr-FR']],
  ['Basa Jawa', ['jv-ID']],
  ['Galego', ['gl-ES']],
  ['ગુજરાતી', ['gu-IN']],
  ['Hrvatski', ['hr-HR']],
  ['IsiZulu', ['zu-ZA']],
  ['Íslenska', ['is-IS']],
  ['Italiano', ['it-IT', 'Italia'],
    ['it-CH', 'Svizzera']],
  ['ಕನ್ನಡ', ['kn-IN']],
  ['ភាសាខ្មែរ', ['km-KH']],
  ['Latviešu', ['lv-LV']],
  ['Lietuvių', ['lt-LT']],
  ['മലയാളം', ['ml-IN']],
  ['मराठी', ['mr-IN']],
  ['Magyar', ['hu-HU']],
  ['ລາວ', ['lo-LA']],
  ['Nederlands', ['nl-NL']],
  ['नेपाली भाषा', ['ne-NP']],
  ['Norsk bokmål', ['nb-NO']],
  ['Polski', ['pl-PL']],
  ['Português', ['pt-BR', 'Brasil'],
    ['pt-PT', 'Portugal']],
  ['Română', ['ro-RO']],
  ['සිංහල', ['si-LK']],
  ['Slovenščina', ['sl-SI']],
  ['Basa Sunda', ['su-ID']],
  ['Slovenčina', ['sk-SK']],
  ['Suomi', ['fi-FI']],
  ['Svenska', ['sv-SE']],
  ['Kiswahili', ['sw-TZ', 'Tanzania'],
    ['sw-KE', 'Kenya']],
  ['ქართული', ['ka-GE']],
  ['Հայերեն', ['hy-AM']],
  ['தமிழ்', ['ta-IN', 'இந்தியா'],
    ['ta-SG', 'சிங்கப்பூர்'],
    ['ta-LK', 'இலங்கை'],
    ['ta-MY', 'மலேசியா']],
  ['తెలుగు', ['te-IN']],
  ['Tiếng Việt', ['vi-VN']],
  ['Türkçe', ['tr-TR']],
  ['اُردُو', ['ur-PK', 'پاکستان'],
    ['ur-IN', 'بھارت']],
  ['Ελληνικά', ['el-GR']],
  ['български', ['bg-BG']],
  ['Русский', ['ru-RU']],
  ['Српски', ['sr-RS']],
  ['Українська', ['uk-UA']],
  ['한국어', ['ko-KR']],
  ['中文', ['cmn-Hans-CN', '普通话 (中国大陆)'],
    ['cmn-Hans-HK', '普通话 (香港)'],
    ['cmn-Hant-TW', '中文 (台灣)'],
    ['yue-Hant-HK', '粵語 (香港)']],
  ['日本語', ['ja-JP']],
  ['हिन्दी', ['hi-IN']],
  ['ภาษาไทย', ['th-TH']]];

var languages = []
for (var i = 0; i < langs.length; i++) {
  languages.push({ value: i, title: langs[i][0] })
}
var selected_language = ref(11)

// Set default language / dialect.
var selected_dialect = computed(() => {
  return langs[selected_language.value][1][0]
})

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
    if (window.getSelection) {
      window.getSelection().removeAllRanges();
      var range = document.createRange();
      range.selectNode(document.getElementById('final_span'));
      window.getSelection().addRange(range);
    }
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
    console.log(final_transcript);
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
  recognition.lang = selected_dialect.value;
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

var current_language_code = computed(() => {
  return langs[selected_language.value][1][0].split("-")[0]
})

function saveAudio(timestamp) {
  const fd = new FormData();
  fd.set('file', blob, timestamp + '.webm');
  fd.append("timestamp", timestamp);
  fd.append("language_code", current_language_code.value);
  fetch(import.meta.env.VITE_BASE_URL + '/upload', { method: 'POST', body: fd })
}

async function analyzeText(timestamp) {
  const fd = new FormData();
  fd.append("timestamp", timestamp);
  fd.append("text", final_transcript);
  fd.append("language_code", current_language_code.value);
  await fetch(import.meta.env.VITE_BASE_URL + '/analyze_text', { method: 'POST', body: fd })
}

var timestamp = ref(Date.now())
async function submitAudio() {
  const timestamp_now = Date.now()
  saveAudio(timestamp_now)
  await analyzeText(timestamp_now)

  timestamp.value = timestamp_now
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