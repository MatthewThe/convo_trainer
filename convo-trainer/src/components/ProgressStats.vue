<template>
    <v-card class="fill-height">
        <v-card-title>
            Vocabulary stats ({{ props.language_code }})
        </v-card-title>
        <v-card-text class="mt-4">
            <!-- <v-row>
                <v-col>
                    <v-data-table-virtual density="compact" :items="vocabulary_stats"></v-data-table-virtual>
                </v-col>
            </v-row> -->
            <v-row>
                <v-progress-linear max="500" v-model="vocabulary_progress_500" color="green" height="25" class="ma-1">
                    <template v-slot:default="{ value }">
                        <strong>{{ Math.round(value*5) }} / 500</strong>
                    </template>
                </v-progress-linear>
            </v-row>
            <v-row>
                <v-progress-linear max="2000" v-model="vocabulary_progress_2000" color="green" height="25" class="ma-1">
                    <template v-slot:default="{ value }">
                        <strong>{{ Math.round(value*20) }} / 2000</strong>
                    </template>
                </v-progress-linear>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script setup>
import { watch, reactive, ref, computed } from 'vue'
const props = defineProps(['language_code', 'timestamp'])

var vocabulary_stats = ref([])
watch(() => [props.language_code, props.timestamp], async () => {
    update_vocabulary()
})

async function update_vocabulary() {
    var response = await fetch(import.meta.env.VITE_BASE_URL + '/vocabulary_stats/' + props.language_code)
    vocabulary_stats.value = await response.json()
}

var vocabulary_progress_2000 = computed(() => {
    return vocabulary_stats.value.find(stat => stat.stat === "Unique words (top 2000)").value
})

var vocabulary_progress_500 = computed(() => {
    return vocabulary_stats.value.find(stat => stat.stat === "Unique words (top 500)").value
})

function get_progress_color(word_count) {
    if (word_count === undefined || word_count === 0) return "grey";
    if (word_count === 1) return "orange";
    if (word_count <= 10) return "yellow";
    if (word_count <= 100) return "green";
    return "purple";
}

await update_vocabulary()
</script>
