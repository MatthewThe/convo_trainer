<template>
    <v-container>
        <v-card>
            <v-card-title>
                Vocabulary progress ({{ props.language_code }})
            </v-card-title>
            <v-card-text>
                <v-row>
                    <v-col class="pa-0" v-for="word in vocabulary_progress" :key="word.rank" cols="auto">
                        <v-tooltip :text="word.word" :disabled="word.word === '0'">
                            <template v-slot:activator="{ props }">
                                <v-btn variant="flat" label v-bind="props" density="compact" :color="word.count > 0 ? 'green' : 'grey'" class="ma-1">
                                    {{ word.rank }}
                                </v-btn>
                            </template>
                        </v-tooltip>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script setup>
import { watch, reactive, ref } from 'vue'
const props = defineProps(['language_code', 'timestamp'])

var vocabulary_progress = ref([])
watch(() => props.timestamp, async (selection, prevSelection) => { 
    update_vocabulary()
})

async function update_vocabulary() {
    var response = await fetch(import.meta.env.VITE_BASE_URL + '/vocabulary_progress/' + props.language_code)
    vocabulary_progress.value = await response.json()
}

await update_vocabulary()
</script>
