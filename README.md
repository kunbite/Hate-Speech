# TEXT ANALYTICS FOR OFFENSIVE SPEECH CLASSIFICATION

This project focused on classifying tweets as offensive or non-offensive using machine learning models, specifically RoBERTa and FastText, applied to the OLID dataset. The study compared the performance of these models and explored the impact of dataset size on their effectiveness. RoBERTa outperformed FastText in accuracy but required more computational resources, while FastText was quicker and more memory-efficient.

# Objective
The project aimed to classify tweets as offensive or non-offensive using the OLID dataset, implementing two different machine learning models: RoBERTa and FastText.

# Key Achievements
Successfully classified tweets into offensive and non-offensive categories.<br/>
Evaluated the performance of both models against the state-of-the-art BERT model.<br/>
Explored the impact of varying dataset sizes on model performance.

# Technologies Used
Models: RoBERTa, FastText <br/>
Dataset: OLID (Offensive Language Identification Dataset)<br/>
Tools: Google Colab, Python (sklearn package for data splitting)

# Key Findings

## Model Performance
RoBERTa achieved an F1 score of 0.75, outperforming FastText, which scored 0.70, but both were below the state-of-the-art BERT model, which scored 0.82.
The accuracy and F1 score of the models improved with the increase in the amount of training data.<br/>

##  Data Size Effect
Significant improvement in model performance was observed when the dataset size increased from 25% to 50%, with minimal gains beyond 50%.

# Conclusions
RoBERTa is more accurate for tweet classification tasks compared to FastText but requires more computational resources and time.
FastText, while less accurate, is much faster and more memory efficient.
Machine Learning Models:

# RoBERTa
Pre-trained on a large corpus of text, capable of understanding complex language patterns.<br/>
Fine-tuned for the specific task of tweet classification.

# FastText 
Utilizes subword information to handle misspellings, slang, and acronyms in tweets.<br/>
Efficient and quick in processing large amounts of data.<br/>

# Implications

RoBERTa: Suitable for applications requiring high accuracy and capable of handling complex language, but at the cost of higher computational resources.<br/>

FastText: Ideal for scenarios where quick processing and memory efficiency are crucial, despite a trade-off in accuracy.
