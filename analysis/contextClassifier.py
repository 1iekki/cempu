
class ContextClassifier:
    def __init__():
        pass    

if __name__ == "__main__":

    import pandas as pd
    import numpy as np
    import pickle
    import random
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.neural_network import MLPClassifier

    # Load data
    with open("outputs/classifier_data.pkl", "rb") as f:
        data = pickle.load(f)

        with open("outputs/contaminated_data.pkl", "rb") as f1:
            new_data = pickle.load(f1)
            data = np.vstack([data, new_data])

    print(len(data))
    column_names = [
        "task", "meta", "env", "vocab", "litq", "backch", "neg", "topic", "keyword",
        "prev_sim", "prev_task", "prev_meta", "prev_env", "prev_vocab", "prev_litq", "prev_backch", "prev_neg", "prev_topic", "prev_keyword",
        "next_sim", "next_task", "next_meta", "next_env", "next_vocab", "next_litq", "next_backch", "next_neg", "next_topic", "next_keyword",
        "topic_label"
    ]

    data = np.array(data)
    topics = data[:, -1]

    total = len(topics)
    count_0 = np.sum(topics == 0)
    count_1 = np.sum(topics == 1)

    print(f"Percentage of off-topic (0): {count_0/total*100:.2f}%")
    print(f"Percentage of on-topic (1): {count_1/total*100:.2f}%")

    X = data[:, :-1]
    y = data[:, -1].astype(int)

    # Define classifiers to test
    classifiers = {
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "HistGBT": HistGradientBoostingClassifier(max_iter=100, random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        "SVM": SVC(kernel='rbf', class_weight='balanced', probability=True, random_state=42),
        "MLP": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }

    # Loop over classifiers
    for name, clf in classifiers.items():
        accs = []
        f1_macros = []
        f1_weighteds = []

        for i in range(100):
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=random.randint(0, 1000), stratify=y
            )

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            clf.fit(X_train_scaled, y_train)
            y_pred = clf.predict(X_test_scaled)

            accs.append(accuracy_score(y_test, y_pred))
            f1_macros.append(f1_score(y_test, y_pred, average='macro'))
            f1_weighteds.append(f1_score(y_test, y_pred, average='weighted'))

        print(f"\nClassifier: {name}")
        # overall accuracy
        print(f"Average accuracy: {np.mean(accs):.4f} ± {np.std(accs):.4f}")
        # handling minority class
        print(f"Macro F1: {np.mean(f1_macros):.4f} ± {np.std(f1_macros):.4f}")
        # overall performance
        print(f"Weighted F1: {np.mean(f1_weighteds):.4f} ± {np.std(f1_weighteds):.4f}")