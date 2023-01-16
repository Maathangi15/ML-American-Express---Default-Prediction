# -*- coding: utf-8 -*-
"""mini-project-180071P.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-cjsclzMCge4-8fs42pjSgMZl14MqZVL

# **Import packages**
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import gc

import warnings
warnings.filterwarnings("ignore")

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OrdinalEncoder
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from xgboost import XGBClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import GradientBoostingClassifier
!pip3 install catboost
from catboost import CatBoostClassifier
from sklearn.ensemble import VotingClassifier

"""# **Read Input Files**"""

train_dataset_ = pd.read_feather('/kaggle/input/amexfeather/train_data.ftr')
# Keep the latest statement features for each customer
train_dataset = train_dataset_.groupby('customer_ID').tail(1).set_index('customer_ID', drop=True).sort_index()
del train_dataset_
gc.collect()

"""# **Feature Engineering**

**Categorical features**
"""

categorical_columns = ['B_30', 'B_38', 'D_114', 'D_116', 'D_117', 'D_120', 'D_126', 'D_63', 'D_64', 'D_66', 'D_68']
print(f'Total number of categorical features: {len(categorical_columns)}')

"""**Numerical features**"""

numerical_columns = [col for col in train_dataset.columns if col not in categorical_cols + ["target"]]
print(f'Total number of continuos features: {len(numerical_columns)}')

"""**1. Imputation**"""

NaN_Val = np.array(train_dataset.isnull().sum())
NaN_prec = np.array((train_dataset.isnull().sum() * 100 / len(train_dataset)).round(2))
NaN_Col = pd.DataFrame([np.array(list(train_dataset.columns)).T,NaN_Val.T,NaN_prec.T,np.array(list(train_dataset.dtypes)).T], index=['Features','Num of Missing values','Percentage','DataType']
).transpose()
pd.set_option('display.max_rows', None)

"""**Remove columns if there are > 80% of missing values as they will affect to create outliers**"""

train_dataset = train_dataset.drop(['S_2','D_66','D_42','D_49','D_73','D_76','R_9','B_29','D_87','D_88','D_106','R_26','D_108','D_110','D_111','B_39','B_42','D_132','D_134','D_135','D_136','D_137','D_138','D_142'], axis=1)

"""**Fill Null values**"""

selected_col = np.array(['P_2','S_3','B_2','D_41','D_43','B_3','D_44','D_45','D_46','D_48','D_50','D_53','S_7','D_56','S_9','B_6','B_8','D_52','P_3','D_54','D_55','B_13','D_59','D_61','B_15','D_62','B_16','B_17','D_77','B_19','B_20','D_69','B_22','D_70','D_72','D_74','R_7','B_25','B_26','D_78','D_79','D_80','B_27','D_81','R_12','D_82','D_105','S_27','D_83','R_14','D_84','D_86','R_20','B_33','D_89','D_91','S_22','S_23','S_24','S_25','S_26','D_102','D_103','D_104','D_107','B_37','R_27','D_109','D_112','B_40','D_113','D_115','D_118','D_119','D_121','D_122','D_123','D_124','D_125','D_128','D_129','B_41','D_130','D_131','D_133','D_139','D_140','D_141','D_143','D_144','D_145'])

for col in selected_col:
    train_dataset[col] = train_dataset[col].fillna(train_dataset[col].median())

selcted_col2 = np.array(['D_68','B_30','B_38','D_64','D_114','D_116','D_117','D_120','D_126'])

for col2 in selcted_col2:
    train_dataset[col2] =  train_dataset[col2].fillna(train_dataset[col2].mode()[0])

train_dataset.shape
train_dataset.head()

"""**2. Test Dataset**"""

test_dataset_ = pd.read_feather('/kaggle/input/amexfeather/test_data.ftr')
# Keep the latest statement features for each customer
test_dataset = test_dataset_.groupby('customer_ID').tail(1).set_index('customer_ID', drop=True).sort_index()

del test_dataset_
gc.collect()

NaN_Val2 = np.array(test_dataset.isnull().sum())
NaN_prec2 = np.array((test_dataset.isnull().sum() * 100 / len(test_dataset)).round(2))
NaN_Col2 = pd.DataFrame([np.array(list(test_dataset.columns)).T,NaN_Val2.T,NaN_prec2.T,np.array(list(test_dataset.dtypes)).T], index=['Features','Num of Missing values','Percentage','DataType']
).transpose()
pd.set_option('display.max_rows', None)

NaN_Col2

test_dataset = test_dataset.drop(['S_2','D_42','D_49','D_66','D_73','D_76','R_9','B_29','D_87','D_88','D_106','R_26','D_108','D_110','D_111','B_39','B_42','D_132','D_134','D_135','D_136','D_137','D_138','D_142'], axis=1)

selected_column = np.array(['P_2','S_3','B_2','D_41','D_43','B_3','D_44','D_45','D_46','D_48','D_50','D_53','S_7','D_56','S_9','S_12','S_17','B_6','B_8','D_52','P_3','D_54','D_55','B_13','D_59','D_61','B_15','D_62','B_16','B_17','D_77','B_19','B_20','D_69','B_22','D_70','D_72','D_74','R_7','B_25','B_26','D_78','D_79','D_80','B_27','D_81','R_12','D_82','D_105','S_27','D_83','R_14','D_84','D_86','R_20','B_33','D_89','D_91','S_22','S_23','S_24','S_25','S_26','D_102','D_103','D_104','D_107','B_37','R_27','D_109','D_112','B_40','D_113','D_115','D_118','D_119','D_121','D_122','D_123','D_124','D_125','D_128','D_129','B_41','D_130','D_131','D_133','D_139','D_140','D_141','D_143','D_144','D_145'])

for column in selected_column:
    test_dataset[column] = test_dataset[column].fillna(test_dataset[column].median())

selected_column2 = np.array(['D_68','B_30','B_38','D_114','D_116','D_117','D_120','D_126'])

for column2 in selected_column2:
    test_dataset[column2] =  test_dataset[column2].fillna(test_dataset[column2].mode()[0])

"""**3. Categerical encoding**"""

ordinal_encoder = OrdinalEncoder()
categorical_columns.remove('D_66')

train_dataset[categorical_columns] = ordinal_encoder.fit_transform(train_dataset[categorical_columns])
test_dataset[categorical_columns] = ordinal_encoder.transform(test_dataset[categorical_columns])

numerical_columns = [col for col in train_dataset.columns if col not in ["target"]]

X = train_dataset[numerical_columns]
y = train_dataset['target']

"""**Train Test Split**"""

x_train,x_test,y_train,y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

"""# **Modelling machine learning approaches**

**1. Lightgbm**
"""

d_train = lgb.Dataset(x_train, label=y_train, categorical_feature = categorical_cols)

params = {'objective': 'binary','n_estimators': 1400,'metric': 'binary_logloss','boosting': 'gbdt','num_leaves': 90,'reg_lambda' : 50,'colsample_bytree': 0.19,'learning_rate': 0.03,'min_child_samples': 2400,'max_bins': 511,'seed': 42,'verbose': -1}

# trained model with 100 iterations
model = lgb.train(params, d_train, 100)

valid_predict = model.predict(x_test)
valid_classes = np.where(valid_predict>0.5,1,0)

confusion_matrix(y_test,valid_classes)

predictions = model.predict(test_dataset[num_columns])

sample_dataset = pd.read_csv('/kaggle/input/amex-default-prediction/sample_submission.csv')
output = pd.DataFrame({'customer_ID': sample_dataset.customer_ID, 'prediction': predictions})
output.to_csv('submission_2.csv', index=False)

"""**2. Random Forest Classifier**"""

rf_model = RandomForestClassifier()
rf_model.fit(x_train, y_train)
predictions_2= rf_model.predict_proba(test_dataset[num_columns])

sample_dataset = pd.read_csv('/kaggle/input/amex-default-prediction/sample_submission.csv')
output = pd.DataFrame({'customer_ID': sample_dataset.customer_ID, 'prediction': predictions_2[:,1]})
output.to_csv('submission_5.csv', index=False)

"""**Naive Byes Classifier**"""

gnb = GaussianNB()
gnb.fit(x_train, y_train)
predictions_3= gnb.predict_proba(test_dataset[num_columns])

sample_dataset = pd.read_csv('/kaggle/input/amex-default-prediction/sample_submission.csv')
output = pd.DataFrame({'customer_ID': sample_dataset.customer_ID, 'prediction': predictions_3[:, 1]})
output.to_csv('submission_6.csv', index=False)

"""**4. SVM**"""

clf = svm.SVC()
clf.fit(x_train, y_train)
predictions_4= clf.predict_proba(test_dataset[num_columns])

sample_dataset = pd.read_csv('/kaggle/input/amex-default-prediction/sample_submission.csv')
output = pd.DataFrame({'customer_ID': sample_dataset.customer_ID, 'prediction': predictions_4[:, 1]})
output.to_csv('submission_7.csv', index=False)

"""**5. Xgboost**"""

model = XGBClassifier()
model.fit(x_train, y_train)
predictions_5= model.predict_proba(test_dataset[num_columns])

sample_dataset = pd.read_csv('/kaggle/input/amex-default-prediction/sample_submission.csv')
output = pd.DataFrame({'customer_ID': sample_dataset.customer_ID, 'prediction': predictions_5[:, 1]})
output.to_csv('submission_3.csv', index=False)

"""**6. Adaboost**"""

adb = AdaBoostClassifier(n_estimators=100, random_state=6)
adb.fit(x_train, y_train)
predictions_6= adb.predict_proba(test_dataset[num_columns])

sample_dataset = pd.read_csv('/kaggle/input/amex-default-prediction/sample_submission.csv')
output = pd.DataFrame({'customer_ID': sample_dataset.customer_ID, 'prediction': predictions_6[:, 1]})
output.to_csv('submission_4.csv', index=False)

"""**7. Voting Classifier**"""

model_1 = CatBoostClassifier()
model_2 = GradientBoostingClassifier()
model_3 = HistGradientBoostingClassifier(max_iter=100)
model_h = VotingClassifier(estimators=[('cb', model_1), ('xgb', model_2), ('gbc', model_3)], voting='soft')
model_h.fit(x_train, y_train)
predictions_9 = model_h.predict_proba(test_dataset[num_columns])

sample_dataset = pd.read_csv('/kaggle/input/amex-default-prediction/sample_submission.csv')
output = pd.DataFrame({'customer_ID': sample_dataset.customer_ID, 'prediction': predictions_9[:, 1]})
output.to_csv('submission_8.csv', index=False)