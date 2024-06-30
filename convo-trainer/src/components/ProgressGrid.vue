<template>
    <v-card>
        <v-card-title>
            Vocabulary progress ({{ props.language_code }})
        </v-card-title>
        <v-card-text class="mt-2">
            <v-row>
                <v-col class="pa-0" v-for="word in vocabulary_progress" :key="word.rank" cols="auto">
                    <v-tooltip :text="word.word" :disabled="word.word === '0'">
                        <template v-slot:activator="{ props }">
                            <v-btn variant="flat" label v-bind="props" density="compact"
                                :color="get_progress_color(word.count)" class="ma-1">
                                {{ word.rank }}
                            </v-btn>
                        </template>
                    </v-tooltip>
                </v-col>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script setup>
import { watch, reactive, ref } from 'vue'
const props = defineProps(['language_code', 'timestamp'])

var vocabulary_progress = ref([])
watch(() => [props.language_code, props.timestamp], async () => {
    update_vocabulary()
})

async function update_vocabulary() {
    var response = await fetch(import.meta.env.VITE_BASE_URL + '/vocabulary_progress/' + props.language_code)
    vocabulary_progress.value = await response.json()
}

function get_progress_color(word_count) {
    if (word_count === undefined || word_count === 0) return "grey";
    if (word_count === 1) return "orange";
    if (word_count <= 10) return "yellow";
    if (word_count <= 100) return "green";
    return "purple";
}

await update_vocabulary()
</script>
