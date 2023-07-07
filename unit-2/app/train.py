import pickle
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

x, y = make_classification(
    n_samples=100, 
    n_features=3, 
    n_informative=2, 
    n_classes=2, 
    n_redundant=0, 
    n_repeated=0,
)

lr = LogisticRegression()
lr.fit(x,y)
print("Training complete!")

with open('model.pickle', 'wb') as f:
    pickle.dump(lr, f)