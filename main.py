import os
import run
import shutil
from subprocess import call, DEVNULL

def getFiles(path) -> list:
    result = []

    if os.path.isfile(path) and path.split('/')[-1] != 'README.md': return result.append(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            f = os.path.join(path, filename)
            if os.path.isfile(f) and filename != 'README.md': result.append(f)
            else: result.extend(getFiles(f))
    
    return result

if __name__ == "__main__":

    if os.path.exists('embedding/verse_exe/temp'):
        shutil.rmtree('embedding/verse_exe/temp')
    if os.path.exists('embedding/struc2vec_exe/temp'):
        shutil.rmtree('embedding/struc2vec_exe/temp')
    
    embeddings = list()
    embeddings.append('spring')
    embeddings.append('kamada_kawai')
    embeddings.append('node2vec')
    embeddings.append('struc2vec')
    embeddings.append('verse')
    
    run.group('embed')
    os.makedirs('embedding_result', exist_ok=True)
    run.add(
        "layout",
        "python embedding/[[embedding]].py [[edgelist]]",
        {'embedding': embeddings,
        'edgelist': getFiles('input_data')},
    )
    
    evaluations = list()
    evaluations.append('average_error_link_prediction.py')
    evaluations.append('precision_at_k_link_prediction.py 10')
    evaluations.append('precision_at_k_link_prediction.py 15')
    evaluations.append('precision_at_k_link_prediction.py 25')
    
    os.makedirs('evaluation_result', exist_ok=True)
    run.add(
        "evaluate",
        "python evaluation/[[evaluation]] [[edgelist]] embedding_result/[[embedding]]/[[edgelist]] ",
        {'evaluation': evaluations,
         'embedding': embeddings,
         'edgelist': getFiles('input_data')},
    )

    run.add(
        "plot",
        "evaluation/evaluation_result_plot.R",
        {},
    )

    run.run()