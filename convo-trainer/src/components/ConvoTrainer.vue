<template>
  <v-container>
    <v-app-bar>
      <template v-slot:prepend>
        <v-app-bar-nav-icon></v-app-bar-nav-icon>
      </template>

      <v-app-bar-title>Convo Trainer</v-app-bar-title>
      <v-row>
        <v-col sm="1" md="4" offset="8">
          <v-select bg-color="primary" class="pr-4" v-model="selected_language" label="Language" :items="languages" hide-details></v-select>
        </v-col>
      </v-row>

    </v-app-bar>
    <v-row dense class="pt-3">
      <v-col sm="4" md="8">
        <voice-input :language_code="current_language_code" @updateTimestamp="updateTimestamp"></voice-input>
      </v-col>
      <v-col sm="4" md="4">
        <progress-stats :language_code="current_language_code" :timestamp="timestamp" />
      </v-col>
    </v-row>
    <v-row dense>
      <v-col>
        <progress-grid :language_code="current_language_code" :timestamp="timestamp" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

// If you modify this array, also update default language / dialect below.
var langs =
  [
    // ['Afrikaans', ['af-ZA']],
    // ['አማርኛ', ['am-ET']],
    // ['Azərbaycanca', ['az-AZ']],
    // ['বাংলা', ['bn-BD', 'বাংলাদেশ'],
    //   ['bn-IN', 'ভারত']],
    ['Bahasa Indonesia', ['id-ID']],
    // ['Bahasa Melayu', ['ms-MY']],
    // ['Català', ['ca-ES']],
    // ['Čeština', ['cs-CZ']],
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
    // ['Euskara', ['eu-ES']],
    // ['Filipino', ['fil-PH']],
    ['Français', ['fr-FR']],
    // ['Basa Jawa', ['jv-ID']],
    // ['Galego', ['gl-ES']],
    // ['ગુજરાતી', ['gu-IN']],
    // ['Hrvatski', ['hr-HR']],
    // ['IsiZulu', ['zu-ZA']],
    // ['Íslenska', ['is-IS']],
    ['Italiano', ['it-IT', 'Italia'],
      ['it-CH', 'Svizzera']],
    // ['ಕನ್ನಡ', ['kn-IN']],
    // ['ភាសាខ្មែរ', ['km-KH']],
    // ['Latviešu', ['lv-LV']],
    // ['Lietuvių', ['lt-LT']],
    // ['മലയാളം', ['ml-IN']],
    // ['मराठी', ['mr-IN']],
    // ['Magyar', ['hu-HU']],
    // ['ລາວ', ['lo-LA']],
    ['Nederlands', ['nl-NL']],
    // ['नेपाली भाषा', ['ne-NP']],
    ['Norsk bokmål', ['nb-NO']],
    // ['Polski', ['pl-PL']],
    ['Português', ['pt-BR', 'Brasil'],
      ['pt-PT', 'Portugal']],
    // ['Română', ['ro-RO']],
    // ['සිංහල', ['si-LK']],
    // ['Slovenščina', ['sl-SI']],
    // ['Basa Sunda', ['su-ID']],
    // ['Slovenčina', ['sk-SK']],
    // ['Suomi', ['fi-FI']],
    ['Svenska', ['sv-SE']],
    // ['Kiswahili', ['sw-TZ', 'Tanzania'],
    //   ['sw-KE', 'Kenya']],
    // ['ქართული', ['ka-GE']],
    // ['Հայերեն', ['hy-AM']],
    // ['தமிழ்', ['ta-IN', 'இந்தியா'],
    //   ['ta-SG', 'சிங்கப்பூர்'],
    //   ['ta-LK', 'இலங்கை'],
    //   ['ta-MY', 'மலேசியா']],
    // ['తెలుగు', ['te-IN']],
    // ['Tiếng Việt', ['vi-VN']],
    // ['Türkçe', ['tr-TR']],
    // ['اُردُو', ['ur-PK', 'پاکستان'],
    //   ['ur-IN', 'بھارت']],
    ['Ελληνικά', ['el-GR']],
    // ['български', ['bg-BG']],
    // ['Русский', ['ru-RU']],
    // ['Српски', ['sr-RS']],
    // ['Українська', ['uk-UA']],
    ['한국어', ['ko-KR']],
    ['中文', ['cmn-Hans-CN', '普通话 (中国大陆)'],
      ['cmn-Hans-HK', '普通话 (香港)'],
      ['cmn-Hant-TW', '中文 (台灣)'],
      ['yue-Hant-HK', '粵語 (香港)']],
    // ['日本語', ['ja-JP']],
    // ['हिन्दी', ['hi-IN']],
    // ['ภาษาไทย', ['th-TH']]
  ];

var languages = []
for (var i = 0; i < langs.length; i++) {
  languages.push({ value: i, title: langs[i][0] })
}
var selected_language = ref(2)

// Set default language / dialect.
// var selected_dialect = computed(() => {
//   return langs[selected_language.value][1][0]
// })

var current_language_code = computed(() => {
  return langs[selected_language.value][1][0].split("-")[0]
})

var timestamp = ref(Date.now())
function updateTimestamp(timestamp_now) {
  timestamp.value = timestamp_now
}
</script>

<style>
body {
  margin: 0;
}
</style>