import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class SimilarityVisualizer:
    
    @staticmethod
    def plot_similarity(similarities : np.ndarray, to_labels : list, of_labels : list, output_path : Path):
        fig, ax = plt.subplots()
        cax = ax.matshow(similarities, cmap='viridis')
        plt.colorbar(cax)

        ax.set_xticks(np.arange(similarities.shape[1]))
        ax.set_yticks(np.arange(similarities.shape[0]))

        ax.set_xticklabels(of_labels, rotation='vertical')
        ax.set_yticklabels(to_labels)

        for i in range(similarities.shape[0]):
            for j in range(similarities.shape[1]):
                text = ax.text(j, i, round(similarities[i, j], 2), ha='center', va='center', color='w')

        plt.tight_layout()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)