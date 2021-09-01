import os
from flask import Flask, url_for, render_template, request
import csv
import math
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap
from sklearn import neighbors, datasets
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

@app.route('/')

def render_home():

    return render_template('home.html')

@app.route('/')

def render_main():

    return render_template('home.html')

@app.route('/diagnosis')

def render_diagnosis():

    return render_template('diagnosis.html')

# User goes to diagnosis.html and submits form, render_diagnosis result gets the input and applies it to script and sends out results, diagnosis_result.html displays.
@app.route('/diagnosis-result')
def render_diagnosis_result():
    try:

        #Creates a dictionary of inputs
        inputString = ""
        i = 1
        inputDict = {}
        inputTemplate = pd.read_csv('input/template.csv')
        for col in inputTemplate.columns:
          inputDict[col] = [request.args['symptom' + str(i)]]
          if request.args['symptom' + str(i)] == '1':
            inputString += col.replace("_", " ") + " "
          i += 1

        p, w, a = diagnosis(inputDict)





        return render_template('diagnosis_result.html', disease = p, warning = w, advice = a, input = inputString)

    except ValueError:

        return "Sorry: something went wrong."  

def diagnosis(dictionaryOfInput):
  # Read csv files
  diseaseData = pd.read_csv("dataset.csv")
  weightsData = pd.read_csv("Symptom-severity.csv")
  symptom_Desc = pd.read_csv("symptom_Description.csv")
  symptom_pre = pd.read_csv("symptom_precaution.csv")

  # Format data
  def formatDF(csv=diseaseData):
    cols = [i for i in csv.iloc[:,1:].columns]

    moveSymp = pd.melt(csv.reset_index() ,id_vars = ['index'], value_vars = cols )
    moveSymp['add1'] = 1

    # Flips all possible x input to become the features
    flipped = pd.pivot_table(moveSymp, values = 'add1', index = 'index', columns = 'value')
    # 1 denotes existence of that symptom in a specific disease; 0 denotes that the disease does not have the symptom
    flipped.insert(0,'Disease',csv['Disease'])
    flipped = flipped.fillna(0)
    flipped.to_csv(path_or_buf='test/raw.csv', index=False)


    return flipped

  flipped = formatDF()
  x = flipped.drop('Disease', axis='columns')
  y = flipped['Disease']


  # Split test and train
  xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.20, random_state = 0)

  DF = pd.DataFrame(xTrain)
  DF.to_csv(path_or_buf='test/xTrain.csv', index=False)

  DF = pd.DataFrame(xTest)
  DF.to_csv(path_or_buf='test/xTest.csv', index=False)

  # Save output set

  DF = pd.DataFrame(yTrain)
  DF.to_csv(path_or_buf='test/yTrain.csv', index=False)

  DF = pd.DataFrame(yTest)
  DF.to_csv(path_or_buf='test/yTest.csv', index=False)

  # Begin classification

  clf = RandomForestClassifier(criterion = 'entropy')
  clf.fit(xTrain, yTrain)
  predictThis = clf.predict(xTest)

  #Useful metrics

  # print(classification_report(yTest.values, predictThis))
  # print(clf.score(xTest,yTest))

  # Predict with user input

  inputDF = pd.DataFrame(data=dictionaryOfInput)
  prediction = clf.predict(inputDF)
  warning = ""
  advice = ""

  #Explain disease and recommend course of action

  arrayDesc, arrayPre = symptom_Desc.to_numpy(), symptom_pre.to_numpy()
  for i in range(41):
    if arrayDesc[i][0].replace(" ", "").lower() == prediction[0].replace(" ", "").lower():
      warning = arrayDesc[i][1]
      for x in range(1,5):
        advice += arrayPre[i][x] + ", "

  return prediction[0], warning, advice
  # # Useful functions
  # symptomList = []
  # weightList = []

  # with open("dataset.csv", 'r') as csvfile:
  #     csvreader = csv.reader(csvfile)
  #     for row in csvreader:
  #         symptomList.append(row)




if __name__ == "__main__":

    app.run(host='0.0.0.0')





