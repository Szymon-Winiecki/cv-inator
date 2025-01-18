from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

class OffersComparator:

    def __init__(self, embeddings_dir, fields_to_compare_with_embeddings, fields_to_compare_with_list_comp):

        self.embeddings_dir = embeddings_dir
        self.fields_to_compare_with_embeddings = fields_to_compare_with_embeddings
        self.fields_to_compare_with_list_comp = fields_to_compare_with_list_comp

        self.__load_data()

        self.num_offers = self.embeddings.shape[0]
        self.num_fields = len(fields_to_compare_with_embeddings) + len(fields_to_compare_with_list_comp)

    def __load_data(self):
        info_files = [f for f in self.embeddings_dir.iterdir() if f.is_file() and f.suffix == '.json']
        summary_files = []
        embeddings = None
        embedded_fields = []
        model_name = ''

        first_file = True
        for file_ind, info_path in enumerate(info_files):
            info = json.load(open(info_path, 'r'))

            if first_file:
                model_name = info['model']
            elif model_name != info['model']:
                raise ValueError('Different models in the input files')
            
            if first_file:
                embedded_fields = info['embedded_fields']
            elif embedded_fields != info['embedded_fields']:
                raise ValueError('Different embedded fields in the input files')
            
            summary_files.append(info['input_file'])


            embeddings_file = info_path.parent / (info_path.stem.replace('_info', '') + '.npy')
            embedding = np.load(embeddings_file)

            if first_file:
                embeddings = np.zeros((len(info_files), embedding.shape[0], embedding.shape[1]))
                first_file = False
            
            embeddings[file_ind] = embedding

        lists_to_compare = {}
        for field in self.fields_to_compare_with_list_comp:
            lists_to_compare[field] = []

        for summary_file in summary_files:
            summary = json.load(open(summary_file, 'r'))['offer_summary']
            for field in self.fields_to_compare_with_list_comp:
                lists_to_compare[field].append(summary[field])


        model = SentenceTransformer(model_name)

        self.embeddings = embeddings
        self.embedded_fields = embedded_fields
        self.model = model
        self.lists_to_compare = lists_to_compare
        self.info_files = info_files

    def __compare_lists(self, lists, to_offer=-1):

        if to_offer < 0:
            similarities = np.zeros((len(lists), len(lists)))
        else:
            similarities = np.zeros((1, len(lists)))

        lists = [ set([l.lower() for l in list]) for list in lists ]

        if to_offer < 0:
            for a, listA in enumerate(lists):
                for b, listB in enumerate(lists):
                    if a == b:
                        similarities[a, b] = 1
                        continue
                    common = len(listA & listB)
                    similarities[a, b] = common / len(listB) if len(listB) > 0 else 1
                    similarities[b, a] = common / len(listA) if len(listA) > 0 else 1

        else:
            for b, listB in enumerate(lists):
                if to_offer == b:
                    similarities[0, b] = 1
                    continue
                common = len(lists[to_offer] & listB)
                similarities[0, b] = common / len(listB) if len(listB) > 0 else 1

        return similarities

    def calc_similarity(self, to_offer=-1):
        if to_offer < 0:
            partial_similarities = np.zeros((self.num_fields, self.num_offers, self.num_offers))
            similarities = np.zeros((self.num_offers, self.num_offers))

            field_ind = 0

            for field in self.fields_to_compare_with_embeddings:
                ind_in_embeddings = self.embedded_fields.index(field)
                partial_similarities[field_ind] = self.model.similarity(self.embeddings[:, ind_in_embeddings], self.embeddings[:, ind_in_embeddings])
                similarities += self.fields_to_compare_with_embeddings[field] * partial_similarities[field_ind]
                field_ind += 1
        
        else:
            partial_similarities = np.zeros((self.num_fields, 1, self.num_offers))
            similarities = np.zeros((1, self.num_offers))

            field_ind = 0

            for field in self.fields_to_compare_with_embeddings:
                ind_in_embeddings = self.embedded_fields.index(field)
                partial_similarities[field_ind] = self.model.similarity(self.embeddings[to_offer, ind_in_embeddings], self.embeddings[:, ind_in_embeddings])
                similarities += self.fields_to_compare_with_embeddings[field] * partial_similarities[field_ind]
                field_ind += 1
            
        for field in self.fields_to_compare_with_list_comp:
            partial_similarities[field_ind] = self.__compare_lists(self.lists_to_compare[field], to_offer=to_offer)
            similarities += self.fields_to_compare_with_list_comp[field] * partial_similarities[field_ind]
            field_ind += 1

        similarities /= sum(self.fields_to_compare_with_embeddings.values()) + sum(self.fields_to_compare_with_list_comp.values())

        return similarities, partial_similarities
    
    def calc_concatenated_embeddings(self):
        return self.embeddings.reshape((self.num_offers, -1))
    
    def get_most_similar(self, to_offer=-1, top_n=-1):
        similarities, _ = self.calc_similarity(to_offer=to_offer)

        if top_n >= 0:
            most_similar = np.argsort(similarities, axis=1)[:, -top_n:]
        else:
            most_similar = np.argsort(similarities, axis=1)

        most_similar = np.flip(most_similar, axis=1)

        most_similar_dicts = []

        for i in range(most_similar.shape[0]):
            most_similar_dicts.append([{'name': self.info_files[ind].name, 'similarity': similarities[i, ind]} for ind in most_similar[i]])

        return most_similar_dicts
    

    def plot_similarity(self, similarities, output_path, to_offer=-1):
        fig, ax = plt.subplots()
        cax = ax.matshow(similarities, cmap='viridis')
        plt.colorbar(cax)

        ax.set_xticks(np.arange(similarities.shape[1]))
        ax.set_yticks(np.arange(similarities.shape[0]))

        ax.set_xticklabels([f.name for f in self.info_files], rotation='vertical')

        if to_offer < 0:
            ax.set_yticklabels([f.name for f in self.info_files])
        else:
            ax.set_yticklabels([self.info_files[to_offer].name])

        for i in range(similarities.shape[0]):
            for j in range(similarities.shape[1]):
                text = ax.text(j, i, round(similarities[i, j], 2), ha='center', va='center', color='w')

        plt.tight_layout()
        plt.savefig(output_path)

    def plot_pca(self, embeddings, output_path):
        pca = PCA(n_components=2)
        embeddings_pca = pca.fit_transform(embeddings)

        fig, ax = plt.subplots()
        for i in range(len(self.info_files)):
            ax.scatter(embeddings_pca[i, 0], embeddings_pca[i, 1], label=self.info_files[i].name)
            ax.annotate(self.info_files[i].name, (embeddings_pca[i, 0], embeddings_pca[i, 1]))
        
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path)