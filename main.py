import os
import run
import shutil
import pandas
import json
from embedding.spring.spring import Spring
from embedding.kamada_kawai.kamada_kawai import KamadaKawai
from embedding.node2vec.node2vec import Node2Vec
from embedding.struc2vec.struc2vec import Struc2Vec
from embedding.verse.verse import Verse

def getFiles(path) -> list:
    result = []
    
    if os.path.isfile(path) and path.split('/')[-1] != 'README.md': return result.append(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            f = os.path.join(path, filename)
            if os.path.isfile(f) and filename != 'README.md': 
                result.append(f)
            elif os.path.isdir(f) and filename != 'README.md':
                result.extend(getFiles(f))
    
    return result

if __name__ == "__main__":
    
    #run.use_cores(1)
    
    input = 'data/input_data'
    config_path = 'data/config'
    embedding_result = 'data/embedding_result'
    evaluation_result = 'data/evaluation_result'
    output = 'data/output'
    
    os.makedirs(embedding_result, exist_ok=True)
    os.makedirs(evaluation_result, exist_ok=True)
    os.makedirs(output, exist_ok=True)
    
    embeddings = list()
    embeddings.append(Spring)
    embeddings.append(KamadaKawai)
    embeddings.append(Node2Vec)
    embeddings.append(Struc2Vec)
    embeddings.append(Verse)
        
    evaluations = {
        'average_error_link_prediction': ['EuclidianDistance', 'InnerProduct'],
        'precision_at_k_link_prediction': ['EuclidianDistance', 'InnerProduct'],
        'read_time': ['None']
    }

    similarity_metrics = {
        'spring': ['EuclidianDistance'],
        'kamada_kawai': ['EuclidianDistance'],
        'node2vec': ['EuclidianDistance'],
        'struc2vec': ['EuclidianDistance'],
        'verse': ['EuclidianDistance']
    }
        
    for embedding_variants in os.listdir(embedding_result):
        similarity_metrics[embedding_variants] = similarity_metrics[embedding_variants.split(' ')[0]]
        similarity_metrics[embedding_variants].append('None')
    
    if os.path.exists(f'{config_path}/main.json'):
        with(open(f'{config_path}/main.json', 'r')) as config_file:
            config = json.load(config_file)
        
        if config.get('embeddings', None):
            embeddings = list(map(lambda embedding: globals()[embedding], config['embeddings']))
        
        evaluations = config.get('evaluations', evaluations)
        
        new_similarity_metrics = config.get('similarity_metrics', dict())
        for embedding_variants in os.listdir(embedding_result):
            if not new_similarity_metrics.get(embedding_variants, None):
                key = embedding_variants.split(' ')[0]
                new_similarity_metrics[embedding_variants] = new_similarity_metrics.get(key, similarity_metrics.get(key, []))
        similarity_metrics = new_similarity_metrics
    
    run.group('layout')
    for embedding in embeddings:
        embedding.create_run(getFiles(input), input, embedding_result)
    
    run.run()
    
    run.group('evaluate')
    for embedding in similarity_metrics.keys():
        for evaluation in evaluations.keys():
            run.add(
                f"calculate {evaluation}",
                f"python evaluation/{evaluation}.py \"{embedding_result}/[[embedded_graph]]\" [[sim_metric]]",
                {'embedded_graph': ['/'.join(path.split('/')[2:]) for path in getFiles(f'{embedding_result}/{embedding}')],
                'sim_metric': list(set(similarity_metrics[embedding]) & set(evaluations[evaluation]))},
                stdout_file=f'{evaluation_result}/[[embedded_graph]]/[[sim_metric]]/{evaluation}.csv',
            )

    run.run()
    
    if (os.path.exists('embedding/node2vec/temp')): shutil.rmtree('embedding/node2vec/temp')
    if (os.path.exists('embedding/struc2vec/struc2vec_exe/temp')): shutil.rmtree('embedding/struc2vec/struc2vec_exe/temp')
    if (os.path.exists('embedding/verse/verse_exe/temp')): shutil.rmtree('embedding/verse/verse_exe/temp')
    
    graph_groups = os.listdir(input)
    embeddings = [path for path in os.listdir(evaluation_result) if os.path.isdir(f'{evaluation_result}/{path}')]
    all_data_frame = []
    for graph_group in graph_groups:
        #data_frame = []
        for embedding in embeddings:
            files = getFiles(f'{evaluation_result}/{embedding}/{graph_group}')
            
            for file in [file for file in files if file.endswith('.csv')]:
                df = pandas.read_csv(file)
                #data_frame.append(df)
                all_data_frame.append(df)
        #if data_frame:
            #result = pandas.concat(data_frame)
            #result.to_csv(f'{output}/{graph_group}.csv', index=False)
    if all_data_frame:
        result = pandas.concat(all_data_frame)
        result.to_csv(f'{output}/all_graphs.csv', index=False)