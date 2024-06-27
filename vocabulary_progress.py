import string
import os
from collections import Counter

import pandas as pd


class WordCounter:
    def __init__(self, language_code: str):
        print(f"initializing word counter for {language_code}")
        self.words_df = pd.read_csv(
            f"https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/{language_code}/{language_code}_50k.txt",
            sep=" ",
            header=None,
            names=["word", "frequency"],
        )
        self.words_df["rank"] = self.words_df.index + 1

        self.result_file = f"./vocabulary_progress/{language_code}_progress.tsv"

    def add_word_counts(self, words: str):
        words = words.lower()
        words = words.translate(str.maketrans("", "", string.punctuation))
        words = words.split()

        word_counts = Counter(words)
        word_counts_df = pd.DataFrame(word_counts.items(), columns=["word", "count"])

        result_df = pd.merge(word_counts_df, self.words_df, on="word", how="left")
        return result_df

    def combine_results(self, df1: pd.DataFrame, df2: pd.DataFrame):
        merged_df = pd.concat([df1, df2])

        result_df = merged_df.groupby(
            ["word", "frequency", "rank"], as_index=False
        ).sum()
        return result_df.sort_values("rank")

    def add_results(self, df2: pd.DataFrame):
        result_df = self.get_results()
        result_df = self.combine_results(result_df, df2)
        result_df.to_csv(self.result_file, sep="\t", index=False)
        return result_df
    
    def get_results(self):
        if os.path.isfile(self.result_file):
            result_df = pd.read_csv(self.result_file, sep="\t")
        else:
            result_df = pd.DataFrame()
        return result_df
