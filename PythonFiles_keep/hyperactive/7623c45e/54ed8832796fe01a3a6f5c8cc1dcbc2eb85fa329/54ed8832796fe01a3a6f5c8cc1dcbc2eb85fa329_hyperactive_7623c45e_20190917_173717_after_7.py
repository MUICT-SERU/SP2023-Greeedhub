from sklearn.model_selection import cross_val_score
from catboost import CatBoostClassifier
from sklearn.datasets import load_breast_cancer
from hyperactive import Hyperactive

data = load_breast_cancer()
X, y = data.data, data.target


def model(para, X_train, y_train):
    model = CatBoostClassifier(depth=para["depth"], learning_rate=para["learning_rate"])
    scores = cross_val_score(model, X_train, y_train, cv=3)

    return scores.mean(), model


# this defines the model and hyperparameter search space
search_config = {
    model: {"depth": range(2, 22), "learning_rate": [1e-3, 1e-2, 1e-1, 0.5, 1.0]}
}


opt = Hyperactive(search_config, n_iter=100, n_jobs=2)

# search best hyperparameter for given data
opt.fit(X, y)
