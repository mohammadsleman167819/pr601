import numpy as np
from ..models import Job_Post,ML_record  
from .ML import generate_data
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score
from sklearn.metrics import silhouette_score
from joblib import dump
from datetime import date  
from django.db.models import Max

def train_model(add_data, start_date,number_of_clusters,word2vec_vector_size,word2vec_window_size,word2vec_word_min_count):


    from gensim.models import Word2Vec

    if(add_data==1):
        generate_data()
  
    
    job_posts = Job_Post.objects.filter(added_date__gte=start_date)
    end_date = job_posts.aggregate(max_date=Max('added_date'))['max_date']
    
    number_of_records = job_posts.count()
    if word2vec_word_min_count==-1:
        word2vec_word_min_count = number_of_records//number_of_clusters
        reduction_factor = 0.15  
        word2vec_word_min_count_reduced = word2vec_word_min_count - (word2vec_word_min_count * reduction_factor)
        word2vec_word_min_count = word2vec_word_min_count_reduced
    
    new_record = ML_record.objects.create(ch_score=".....", 
                            sh_score=".....",
                            number_of_clusters=number_of_clusters,
                            total_records=number_of_records,
                            word2vec_vector_size=word2vec_vector_size,
                            word2vec_window_size=word2vec_window_size,
                            word2vec_word_min_count=word2vec_word_min_count,
                            from_date = start_date,
                            end_date = end_date)

    word2vecmodel = Word2Vec(
    window = word2vec_window_size, 
    min_count = word2vec_word_min_count,
    vector_size = word2vec_vector_size)
    
    text_data = list(job_posts.values_list('clusterable_text', flat=True))
    
    word2vecmodel.build_vocab(text_data)
    word2vecmodel.train(text_data,total_examples=word2vecmodel.corpus_count,epochs = word2vecmodel.epochs)
    dump(word2vecmodel, 'word2vecmodel.joblib')

    def text_to_vector(text):
      words = text.split()
      return word2vecmodel.wv.get_mean_vector(words)

    vectors=[]
    for text in text_data:
        vectors.append(text_to_vector(text))
        

    vectors_2d = np.stack(vectors)
    model = KMeans(n_clusters = number_of_clusters, init='k-means++', max_iter=5000,n_init='auto')
   
    labels = model.fit_predict(vectors_2d)
     
    dump(model, 'Kmeans_model.joblib')  

    for i in range(len(job_posts)):
        job_posts[i].cluster=labels[i]
        job_posts[i].save()
   
    ch_score = calinski_harabasz_score(vectors_2d, labels)
    print(ch_score)
    new_record.ch_score = str(ch_score)
    new_record.save()
    sil_score = silhouette_score(vectors_2d, labels)
    print(sil_score)
    new_record.sh_score = str(sil_score) 
    new_record.save()