# -*- coding: utf-8 -*-
"""code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12Ujqk3LKL5ipKEOhvR9Tn4b3p3FMtuAV

# Student ID: 2202398

**Code References**  
The model training, validation and prediction codes used in this assignment are adapted from the lab 10 solution and the following websites:
* https://fasttext.cc/docs/en/supervised-tutorial.html
* https://scikit-learn.org/stable/user_guide.html
* https://thinkinfi.com/fasttext-for-text-classification-python
* https://jesusleal.io/2020/10/20/RoBERTA-Text-Classification
* https://stackoverflow.com

Let's install all required libraries.
"""

!pip install transformers
!pip install fasttext

"""Let's import all required packages."""

import numpy as np
import torch
import os
import re
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import fasttext
from transformers import RobertaTokenizer, RobertaForSequenceClassification, AdamW

from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, accuracy_score, precision_score
from sklearn.metrics import recall_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.linear_model import LogisticRegression

import nltk
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

"""**Let's set student id as a variable, that will be used different places**"""

student_id = 2202398

"""Let's set `seed` for all libraries as student id"""

# set same seeds for all libraries

#numpy seed
np.random.seed(student_id)

#torch seed
torch.manual_seed(student_id)

"""# Common Codes

**Let's first allow the GDrive access**
"""

# Mount Google Drive
from google.colab import drive
drive.mount('/content/gdrive', force_remount=True)

# Set Assignment folder path in my GDrive
GOOGLE_DRIVE_PATH_AFTER_MYDRIVE = os.path.join('./CE807/Assignment2/', str(student_id))
GOOGLE_DRIVE_PATH = os.path.join('gdrive', 'MyDrive', GOOGLE_DRIVE_PATH_AFTER_MYDRIVE)
print('List files: ', os.listdir(GOOGLE_DRIVE_PATH))

"""**Let's add a method to load a CSV file into a pandas dataframe**"""

def load_csv_file(file_location):
  return pd.read_csv(file_location)

"""Let's see train file"""

train_file = os.path.join(GOOGLE_DRIVE_PATH, 'train.csv')

train_df = load_csv_file(train_file)
train_df.head()

"""**Let's split the train file into seperate files of 25%, 50%, 75% and 100% unbiased dataset.**  
The unbiased split is achieved by employing the `StratifiedShuffleSplit` available in [sklearn](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedShuffleSplit.html) to ensure that each resulting dataset has a similar distribution of values in the label column.  
The implementation in the function is to first split the records into dataframes of 25% each, and then merge the previous one to generate the current file in context. i.e. File 1 (25%) is the initial subset at 0 while File 2 (50%) is the initial subset at 0 + subset at 1.
"""

# Initialize an empty dataframe.
# This will hold all processed subset from our split
train_set = pd.DataFrame({'' : []})

# Initialize splitter with 4 splits of 25% content each
splitter = StratifiedShuffleSplit(n_splits=4, test_size=0.25)

# Loop through each splitted set
for i, (train_index, test_index) in enumerate(splitter.split(train_df, train_df['label'])):
  data_set = train_df.iloc[test_index]

  if(train_set.empty):
    # Train set will be empty during the first iteration
    # so we set the first subset and save to file
    train_set = data_set
  else:
    # For subsequent iterations, simply add the current set to the previous 
    # data and save to file
    train_set = pd.concat([train_set, data_set])

  train_file_name = f'train_{(i+1) * 25}.csv'
  train_file_path = os.path.join(GOOGLE_DRIVE_PATH, train_file_name)
  train_set.to_csv(train_file_path, index=False)
  print('Saved train file', train_file_name,'to assignment folder')

"""**Let's set data and model paths**"""

val_file = os.path.join(GOOGLE_DRIVE_PATH, 'valid.csv')
print('Validation file: ', val_file)

test_file = os.path.join(GOOGLE_DRIVE_PATH, 'test.csv')
print('Test file: ', test_file)

train_25_file = os.path.join(GOOGLE_DRIVE_PATH, 'train_25.csv')
print('Train 25% file: ', train_25_file)

train_50_file = os.path.join(GOOGLE_DRIVE_PATH, 'train_50.csv')
print('Train 50% file: ', train_50_file)

train_75_file = os.path.join(GOOGLE_DRIVE_PATH, 'train_75.csv')
print('Train 75% file: ', train_75_file)

train_100_file = os.path.join(GOOGLE_DRIVE_PATH, 'train_100.csv')
print('Train 25% file: ', train_100_file)

print('\n')
MODEL_1_DIRECTORY = os.path.join(GOOGLE_DRIVE_PATH, 'models', '1') # Model 1 directory
print('Model 1 directory: ', MODEL_1_DIRECTORY)

MODEL_1_25_DIRECTORY = os.path.join(MODEL_1_DIRECTORY,'25') # Model 1 trained using 25% of train data directory
print('Model 1 directory with 25% data: ', MODEL_1_25_DIRECTORY)

MODEL_1_50_DIRECTORY = os.path.join(MODEL_1_DIRECTORY,'50') # Model 1 trained using 50% of train data directory
print('Model 1 directory with 50% data: ', MODEL_1_50_DIRECTORY)

MODEL_1_75_DIRECTORY = os.path.join(MODEL_1_DIRECTORY,'75') # Model 1 trained using 25% of train data directory
print('Model 1 directory with 75% data: ', MODEL_1_75_DIRECTORY)

MODEL_1_100_DIRECTORY = os.path.join(MODEL_1_DIRECTORY,'100') # Model 1 trained using 100% of train data directory
print('Model 1 directory with 100% data: ', MODEL_1_100_DIRECTORY)

print('\n')
model_1_25_output_test_file = os.path.join(MODEL_1_25_DIRECTORY, 'output_test.csv') # Output file using Model 1 trained using 25% of train data 
print('Output file name using model 1 using 25% of train data: ',model_1_25_output_test_file)

model_1_50_output_test_file = os.path.join(MODEL_1_50_DIRECTORY, 'output_test.csv') # Output file using Model 1 trained using 50% of train data 
print('Output file name using model 1 using 50% of train data: ',model_1_50_output_test_file)

model_1_75_output_test_file = os.path.join(MODEL_1_75_DIRECTORY, 'output_test.csv') # Output file using Model 1 trained using 75% of train data 
print('Output file name using model 1 using 75% of train data: ',model_1_75_output_test_file)

model_1_100_output_test_file = os.path.join(MODEL_1_100_DIRECTORY, 'output_test.csv') # Output file using Model 1 trained using 100% of train data 
print('Output file name using model 1 using 100% of train data: ',model_1_100_output_test_file)

print('\n')
MODEL_2_DIRECTORY = os.path.join(GOOGLE_DRIVE_PATH, 'models', '2') # Model 2 directory
print('Model 2 directory: ', MODEL_2_DIRECTORY)

MODEL_2_25_DIRECTORY = os.path.join(MODEL_2_DIRECTORY,'25') # Model 2 trained using 25% of train data directory
print('Model 2 directory with 25% data: ', MODEL_2_25_DIRECTORY)

MODEL_2_50_DIRECTORY = os.path.join(MODEL_2_DIRECTORY,'50') # Model 2 trained using 50% of train data directory
print('Model 2 directory with 50% data: ', MODEL_2_50_DIRECTORY)

MODEL_2_75_DIRECTORY = os.path.join(MODEL_2_DIRECTORY,'75') # Model 2 trained using 25% of train data directory
print('Model 2 directory with 75% data: ', MODEL_2_75_DIRECTORY)

MODEL_2_100_DIRECTORY = os.path.join(MODEL_2_DIRECTORY,'100') # Model 2 trained using 100% of train data directory
print('Model 2 directory with 100% data: ', MODEL_2_100_DIRECTORY)

print('\n')
model_2_25_output_test_file = os.path.join(MODEL_2_25_DIRECTORY, 'output_test.csv') # Output file using Model 2 trained using 25% of train data 
print('Output file name using model 2 using 25% of train data: ',model_2_25_output_test_file)

model_2_50_output_test_file = os.path.join(MODEL_2_50_DIRECTORY, 'output_test.csv') # Output file using Model 2 trained using 50% of train data 
print('Output file name using model 2 using 50% of train data: ',model_2_50_output_test_file)

model_2_75_output_test_file = os.path.join(MODEL_2_75_DIRECTORY, 'output_test.csv') # Output file using Model 2 trained using 75% of train data 
print('Output file name using model 2 using 75% of train data: ',model_2_75_output_test_file)

model_2_100_output_test_file = os.path.join(MODEL_2_100_DIRECTORY, 'output_test.csv') # Output file using Model 2 trained using 100% of train data 
print('Output file name using model 2 using 100% of train data: ',model_2_100_output_test_file)

"""**Let's create a function to remove english stopwords**  
This function uses Python's NLTK library to tokenize the text and then remove english stopwords. The remaining tokens is then converted back to a sentence by concatenated them with whitespaces
"""

def remove_stopwords(text):
  stop_words = set(stopwords.words('english'))
  tokens = nltk.word_tokenize(text)
  tokens = [token for token in tokens if token not in stop_words]

  return ' '.join(tokens)

"""**Let's create a function to cleanup texts**  
Cleanup processes performed on the text includes:
* Converting all characters to lowercase
* Removing extra spaces, tabs and breaklines
* Removing non-alphanumeric characters from the tweet
* Remove english stopwords using the `remove_stopwords` function defined above
"""

def cleanup_text(text):
  text = text.lower() # Convert to lower case
  text = ' '.join(text.split()) # Strip breaklines, tabs and extra whitespace
  text = re.sub(r'[^\w\s]+', '', text) # Strip non-alphanumeric characters
  
  return remove_stopwords(text)

"""**Let's create a function to compute performance**  
We are going to use different performance matrics like Accuracy, Recall (macro), Precision (macro), F1 (macro) and Confusion Matrix for the performance evaluation. We will print all the matrics and display Confusion Matrix with proper X & Y axis labels
"""

def compute_performance(y_true, y_pred, action='test'):
  """
    prints different performance matrics like  Accuracy, Recall (macro), Precision (macro), and F1 (macro).
    This also display Confusion Matrix with proper X & Y axis labels.
    Also, returns F1 score

    Args:
        y_true: numpy array or list
        y_pred: numpy array or list
        action: string
        

    Returns:
        float
  """

  print('Computing different preformance metrics on', action, 'set of Dataset')
  accuracy = accuracy_score(y_true, y_pred)
  recall = recall_score(y_true, y_pred, average = 'macro')
  precision = precision_score(y_true, y_pred, average = 'macro')
  f1 = f1_score(y_true, y_pred, average = 'macro')

  if action != 'comparison':
    print('Accuracy:', accuracy)
    print('Recall (macro):', recall)
    print('Precision (macro):', precision)
    print('F1 Score (macro):', f1)
    print('\nConfusion Matrix:')
    c_matrix = confusion_matrix(y_true, y_pred, labels = ['OFF', 'NOT'])
    c_matrix_display = ConfusionMatrixDisplay(c_matrix, display_labels=['OFF', 'NOT']).plot()
    plt.show()
  
  print('\n')

  return f1

"""# Method 1 Start

**Let's create a function to prepare data set for FastText classification**  
FastText processes data in plain text format where each line of text is made up of the classification label identified by a prefix, followed by the classified text. This function generates the required text format from a specified OLID data file and saves it in the applicable model directory.  

As part of the processing, the tweet is also cleaned up by removing extra spaces and special characters, and also removing english stopwords.
"""

def prepare_dataset1(data_file, model_dir = None, action = 'test'):
  # Create a working copy of the data file so the original remains untouched
  data = data_file.copy()
  data['tweet'] = data['tweet'].apply(cleanup_text)

  if action == 'train':
    # If data preparation is for model training, generate and persist the train
    # dataset file.
    dataset_file = os.path.join(model_dir, f'{action}_dataset.txt')
    with open(dataset_file, "w", encoding="utf-8") as f:
      for i in range(len(data)):
        f.write("__label__" + str(data.iloc[i]["label"]) + " " + data.iloc[i]["tweet"] + "\n")

    return dataset_file, data['tweet']
  else:
    # Not for training a model Just return cleaned tweet items
    return data['tweet']

"""**Let's create a function to train the FastText model**  
This function accepts the prepared plain text file and trains a FastText model
"""

def train_model1(dataset_file):
  print('Let\'s start training FastText model')
  return fasttext.train_supervised(input=dataset_file)

"""**Let's create a function to save model in GDrive**  
This function accepts the model to be saved and the directory in Google Drive where it should be saved to. It returns the full path to the saved model
"""

def save_model1(model, model_dir):
  # save the model to disk
  model_file = os.path.join(model_dir, 'model.bin')
  model.save_model(model_file)
  print('Saved model to ', model_file)

  return model_file

"""**Let's create a function to load a saved model from GDrive**  
This function accepts the path of a saved FastText model and loads it. It returns the loaded model
"""

def load_model1(model_file):
  # Load model from disk
  model = fasttext.load_model(model_file)
  print('Loaded model from ', model_file)

  return model

"""**Let's create a function to execute FastText predictions on a dataset**  
This function accepts the FastText model to use for the predictions and the dataset to be predicted. FastText model does a single prediction so this function loops through the items in the dataset and predicts each one. The result is then returned as a list of predicted labels
"""

def model1_predictions(model, dataset):
  predicted_labels = []
  for index, tweet in dataset.items():
    label, probability = model.predict(tweet)
    predicted_labels.append(label[0].replace('__label__', ''))
  
  return predicted_labels

"""## Training Method 1 Code
Your test code should be a stand alone code that must take `train_file`, `val_file`,  and `model_dir` as input. You could have other things as also input, but these three are must. You would load both files, and train using the `train_file` and validating using the `val_file`. You will `print` / `display`/ `plot` all performance metrics, loss(if available) and save the output model in the `model_dir`.

Note that at the testing time, you need to use the same pre-processing and model. So, it would be good that you make those as seperate function/pipeline whichever it the best suited for your method. Don't copy-paste same code twice, make it a fucntion/class whichever is best. 
"""

def train_method1(train_file, val_file, model_dir):
  """
    Takes train_file, val_file and model_dir as input.
    It trained on the train_file datapoints, and validate on the val_file datapoints.
    While training and validating, it print different evaluataion metrics and losses, wheverever necessary.
    After finishing the training, it saved the best model in the model_dir.

    ADD Other arguments, if needed.

  Args:
    train_file: Train file name
    val_file: Validation file name
    model_dir: Model output Directory

  """

  train_df = load_csv_file(train_file)
  val_df = load_csv_file(val_file)

  train_label = train_df['label']
  val_label = val_df['label']
  
  train_dataset_file, train_dataset = prepare_dataset1(train_df, model_dir, action ='train') 
  val_dataset = prepare_dataset1(val_df, model_dir, action = 'valid')
  
  model = train_model1(train_dataset_file)

  model_file = save_model1(model, model_dir)

  train_pred_labels = model1_predictions(model, train_dataset)
  val_pred_labels = model1_predictions(model, val_dataset)

  print('Train Split')
  train_f1_score = compute_performance(train_label, train_pred_labels, action='train')

  print('Validation Split')
  val_f1_score = compute_performance(val_label, val_pred_labels, action='valid')

  return model_file

print('Train using of 25% of data')
model_1_25_file = train_method1(train_25_file, val_file, MODEL_1_25_DIRECTORY)

print('Train using of 50% of data')
model_1_50_file = train_method1(train_50_file, val_file, MODEL_1_50_DIRECTORY)

print('Train using of 75% of data')
model_1_75_file = train_method1(train_75_file, val_file, MODEL_1_75_DIRECTORY)

print('Train using of 100% of data')
model_1_100_file = train_method1(train_100_file, val_file, MODEL_1_100_DIRECTORY)

"""## Testing Method 1 Code
Your test code should be a stand alone code that must take `test_file`, `model_file` and `output_dir` as input. You could have other things as also input, but these three are must. You would load both files, and generate output based on inputs. Then you will `print` / `display`/ `plot` all performance metrics, and save the output file in the `output_dir`  
"""

from tables.tests.test_suite import test
def test_method1(test_file, model_file, output_dir):
  """
    take test_file, model_file and output_dir as input.
    It loads model and test of the examples in the test_file.
    It prints different evaluation metrics, and saves the output in output directory

    ADD Other arguments, if needed

  Args:
      test_file: test file name
      model_file: model file name
      output_dir: Output Directory
      

  
  """

  test_df = load_csv_file(test_file)
  
  test_label = test_df['label']

  model = load_model1(model_file) 

  test_dataset = prepare_dataset1(test_df)
  
  test_pred_labels = model1_predictions(model, test_dataset)

  test_df['out_label']  = test_pred_labels

  test_f1_score = compute_performance(test_label, test_pred_labels, action='test')

  out_file = os.path.join(output_dir, 'output_test.csv')

  print('Saving model output to', out_file)
  test_df.to_csv(out_file)

print('Testing using model trained on 25% data')
test_method1(test_file, model_1_25_file, MODEL_1_25_DIRECTORY)

print('Testing using model trained on 50% data')
test_method1(test_file, model_1_50_file, MODEL_1_50_DIRECTORY)

print('Testing using model trained on 75% data')
test_method1(test_file, model_1_75_file, MODEL_1_75_DIRECTORY)

print('Testing using model trained on 100% data')
test_method1(test_file, model_1_100_file, MODEL_1_100_DIRECTORY)

"""**Let's generate a performance comparison report of validation and testing for all models**"""

dataset_sizes = ['25%', '50%', '75%', '100%']

test_df = load_csv_file(test_file)
test_dataset = prepare_dataset1(test_df)
test_label = test_df['label']

validation_df = load_csv_file(val_file)
validation_dataset = prepare_dataset1(validation_df)
validation_label = validation_df['label']

models = [model_1_25_file, model_1_50_file, model_1_75_file, model_1_100_file]
validation_scores = []
testing_scores = []

for model in models:
  validation_pred_label = model1_predictions(load_model1(model), validation_dataset)
  validation_scores.append(compute_performance(validation_label, validation_pred_label, action = 'comparison'))

  testing_pred_label = model1_predictions(load_model1(model), test_dataset)
  testing_scores.append(compute_performance(test_label, testing_pred_label, action = 'comparison'))

plt.plot(dataset_sizes, validation_scores, label="Validation Accuracy")
plt.plot(dataset_sizes, testing_scores, label="Testing Accuracy")

plt.xlabel("Dataset Size")
plt.ylabel("F1 Score")
plt.title("FastText Classification Performance")
plt.legend()
plt.show()

"""## Method 1 End

# Method 2 Start

**Let's create a function to map labels to float values**  
This function simply returns 1 for OFF and 0 for NOT
"""

def label_to_float(label):
  if label == 'OFF':
     return 1
  return 0

"""**Let's create a function to map float values to labels**  
This function simply returns 1 for OFF and 0 for NOT
"""

def float_to_label(value):
  if value == 1:
     return 'OFF'
  return 'NOT'

"""**Let's create a function to prepare data set for Roberta classification**  
As part of the processing, the tweet is also cleaned up by removing extra spaces and special characters, and also removing english stopwords.
"""

def prepare_dataset2(data_file, action = 'test'):
  # Create a working copy of the data file so the original remains untouched
  data = data_file.copy()
  data['tweet'] = data['tweet'].apply(cleanup_text) # Cleanup text
  data['label'] = data['label'].apply(label_to_float) # Convert labels to their float equivalent

  tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
  input_ids = []
  attention_masks = []
  encoded_tweets = []

  for tweet in data['tweet']:
    encoded_tweet = tokenizer.encode_plus(tweet, 
                                         add_special_tokens=True, 
                                         max_length=64, 
                                         padding='max_length', 
                                         truncation=True, 
                                         return_attention_mask=True, 
                                         return_tensors='pt'
                    )
    encoded_tweets.append(encoded_tweet)
    input_ids.append(encoded_tweet['input_ids'])
    attention_masks.append(encoded_tweet['attention_mask'])
  
  if action == 'train':
    # Convert the lists into tensors
    input_ids = torch.cat(input_ids, dim = 0)
    attention_masks = torch.cat(attention_masks, dim = 0)
    values = torch.tensor(data['label'].values)

    dataset = torch.utils.data.TensorDataset(input_ids, attention_masks, values)

    return dataset, encoded_tweets
  else:
    # Not for training a model just return encoded tweets
    return encoded_tweets

"""**Let's create a function to train the RoBERTA model**  
This function accepts the prepared dataset and trains a RoBERTA model on the specified device
"""

def train_model2(dataset, torch_device):
  print('Let\'s start training RoBERTA  model')
  
  model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)
  model.to(torch_device)

  train_dataloader = torch.utils.data.DataLoader(dataset, batch_size=10, shuffle=True)
  optimizer = AdamW(model.parameters(), lr=2e-5)

  for epoch in range(2):
    model.train()
    train_loss = 0
    for batch in train_dataloader:
        batch = tuple(t.to(torch_device) for t in batch)
        input_ids, attention_mask, labels = batch
        optimizer.zero_grad()
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs[0]
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    print('Epoch {} train loss: {:.2f}'.format(epoch+1, train_loss/len(train_dataloader)))
  
  return model

"""**Let's create a function to save model in GDrive**  
This function accepts the model to be saved and the directory in Google Drive where it should be saved to. It returns the path to the folder where model is saved
"""

def save_model2(model, model_dir):
  # save the model to disk
  model_folder = os.path.join(model_dir, 'roberta_model')
  model.save_pretrained(model_folder)
  print('Saved model to ', model_folder)

  return os.path.join(model_folder, 'pytorch_model.bin')

"""**Let's create a function to load a saved model from GDrive**  
This function accepts the path of a saved RoBERTA model and loads it. It returns the loaded model
"""

def load_model2(model_file, torch_device):
  # Load model from disk
  model_weights = torch.load(model_file, map_location=torch_device)
  model = RobertaForSequenceClassification.from_pretrained('roberta-base', 
                                                          num_labels=2, 
                                                          state_dict=model_weights
                                           )
  print('Loaded model from ', model_file)

  return model

"""**Let's create a function to execute RoBERTA predictions on a dataset**  
This function accepts the RoBERTA model to use for the predictions and the dataset to be predicted.
"""

def model2_predictions(model, encoded_tweets, torch_device):
  predicted_labels = []
  with torch.no_grad():
    for encoded_tweet in encoded_tweets:
      input_ids = encoded_tweet['input_ids']
      attention_mask = encoded_tweet['attention_mask']
      input_ids, attention_mask = input_ids.to(torch_device), attention_mask.to(torch_device)

      outputs = model(input_ids, attention_mask=attention_mask)
      logits = outputs[0]
      logits = logits.detach().cpu().numpy()

      predicted_label = np.argmax(logits)
      predicted_labels.append(float_to_label(predicted_label))
  
  return predicted_labels

"""## Training Method 2 Code
Your test code should be a stand alone code that must take `train_file`, `val_file`,  and `model_dir` as input. You could have other things as also input, but these three are must. You would load both files, and train using the `train_file` and validating using the `val_file`. You will `print` / `display`/ `plot` all performance metrics, loss(if available) and save the output model in the `model_dir`.

Note that at the testing time, you need to use the same pre-processing and model. So, it would be good that you make those as seperate function/pipeline whichever it the best suited for your method. Don't copy-paste same code twice, make it a fucntion/class whichever is best. 
"""

def train_method2(train_file, val_file, model_dir):
  """
    Takes train_file, val_file and model_dir as input.
    It trained on the train_file datapoints, and validate on the val_file datapoints.
    While training and validating, it print different evaluataion metrics and losses, wheverever necessary.
    After finishing the training, it saved the best model in the model_dir.

    ADD Other arguments, if needed.

  Args:
      train_file: Train file name
      val_file: Validation file name
      model_dir: Model output Directory
      

  
  """

  train_df = load_csv_file(train_file)
  val_df = load_csv_file(val_file)

  train_label = train_df['label']
  val_label = val_df['label']
  
  train_dataset, train_encoded_tweets = prepare_dataset2(train_df, action ='train') 
  val_encoded_tweets = prepare_dataset2(val_df, action = 'valid')
  
  torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  model = train_model2(train_dataset, torch_device)
  
  model_file = save_model2(model, model_dir)

  train_pred_labels = model2_predictions(model, train_encoded_tweets, torch_device)
  val_pred_labels = model2_predictions(model, val_encoded_tweets, torch_device)
  
  print('Train Split')
  train_f1_score = compute_performance(train_label, train_pred_labels, action='train')

  print('Validation Split')
  val_f1_score = compute_performance(val_label, val_pred_labels, action='valid')

  return model_file

print('Train using of 25% of data')
model_2_25_file = train_method2(train_25_file, val_file, MODEL_2_25_DIRECTORY)

print('Train using of 50% of data')
model_2_50_file = train_method2(train_50_file, val_file, MODEL_2_50_DIRECTORY)

print('Train using of 75% of data')
model_2_75_file = train_method2(train_75_file, val_file, MODEL_2_75_DIRECTORY)

print('Train using of 100% of data')
model_2_100_file = train_method2(train_100_file, val_file, MODEL_2_100_DIRECTORY)

"""## Testing Method 2 Code
Your test code should be a stand alone code that must take `test_file`, `model_file` and `output_dir` as input. You could have other things as also input, but these three are must. You would load both files, and generate output based on inputs. Then you will `print` / `display`/ `plot` all performance metrics, and save the output file in the `output_dir`  
"""

def test_method2(test_file, model_file, output_dir):
  """
    take test_file, model_file and output_dir as input.
    It loads model and test of the examples in the test_file.
    It prints different evaluation metrics, and saves the output in output directory

    ADD Other arguments, if needed

  Args:
      test_file: test file name
      model_file: model file name
      output_dir: Output Directory
      

  
  """
  # torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  torch_device = torch.device("cpu")

  test_df = load_csv_file(test_file)

  test_label = test_df['label']

  model = load_model2(model_file, torch_device) 

  test_dataset = prepare_dataset2(test_df)
  
  test_pred_labels = model2_predictions(model, test_dataset, torch_device)

  test_df['out_label']  = test_pred_labels

  test_f1_score = compute_performance(test_label, test_pred_labels, action='test')

  out_file = os.path.join(output_dir, 'output_test.csv')

  print('Saving model output to', out_file)
  test_df.to_csv(out_file)

print('Testing using model trained on 25% data')
test_method2(test_file, model_2_25_file, MODEL_2_25_DIRECTORY)

print('Testing using model trained on 50% data')
test_method2(test_file, model_2_50_file, MODEL_2_50_DIRECTORY)

print('Testing using model trained on 75% data')
test_method2(test_file, model_2_75_file, MODEL_2_75_DIRECTORY)

print('Testing using model trained on 100% data')
test_method2(test_file, model_2_100_file, MODEL_2_100_DIRECTORY)

"""**Let's generate a performance comparison report of validation and testing for all models**"""

torch_device = torch.device("cpu")
dataset_sizes = ['25%', '50%', '75%', '100%']

test_df = load_csv_file(test_file)
test_dataset = prepare_dataset2(test_df)
test_label = test_df['label']

validation_df = load_csv_file(val_file)
validation_dataset = prepare_dataset2(validation_df)
validation_label = validation_df['label']

models = [model_2_25_file, model_2_50_file, model_2_75_file, model_2_100_file]
validation_scores = []
testing_scores = []

for model in models:
  validation_pred_label = model2_predictions(load_model2(model, torch_device), validation_dataset, torch_device)
  validation_scores.append(compute_performance(validation_label, validation_pred_label, action = 'comparison'))

  testing_pred_label = model2_predictions(load_model2(model, torch_device), test_dataset, torch_device)
  testing_scores.append(compute_performance(test_label, testing_pred_label, action = 'comparison'))

plt.plot(dataset_sizes, validation_scores, label = "Validation Accuracy")
plt.plot(dataset_sizes, testing_scores, label = "Testing Accuracy")

plt.xlabel("Dataset Size")
plt.ylabel("F1 Score")
plt.title("RoBERTA Classification Performance")
plt.legend()
plt.show()

"""## Method 2 End

# Other Method/model Start
"""

# your code

"""##Other Method/model End"""