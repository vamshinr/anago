"""
Custom callbacks.
"""
import numpy as np
from keras.callbacks import Callback
from seqeval.metrics import f1_score, classification_report

class F1score(Callback):

    def __init__(self, seq, train_seq, preprocessor=None):
        super(F1score, self).__init__()
        self.seq = seq
        self.train_seq = train_seq
        self.p = preprocessor

    def get_lengths(self, y_true):
        lengths = []
        for y in np.argmax(y_true, -1):
            try:
                i = list(y).index(0)
            except ValueError:
                i = len(y)
            lengths.append(i)

        return lengths

    def on_epoch_end(self, epoch, logs={}):
        label_true = []
        label_pred = []
        for i in range(len(self.seq)):
            x_true, y_true = self.seq[i]
            lengths = self.get_lengths(y_true)
            y_pred = self.model.predict_on_batch(x_true)

            y_true = self.p.inverse_transform(y_true, lengths)
            y_pred = self.p.inverse_transform(y_pred, lengths)

            label_true.extend(y_true)
            label_pred.extend(y_pred)

        valid_score = f1_score(label_true, label_pred)
        print(' - f1-valid: {:04.2f}'.format(valid_score * 100))
        print('validation report :', classification_report(label_true, label_pred))

        label_true = []
        label_pred = []
        for i in range(len(self.train_seq)):
            x_true, y_true = self.train_seq[i]
            lengths = self.get_lengths(y_true)
            y_pred = self.model.predict_on_batch(x_true)

            y_true = self.p.inverse_transform(y_true, lengths)
            y_pred = self.p.inverse_transform(y_pred, lengths)

            label_true.extend(y_true)
            label_pred.extend(y_pred)

        train_score = f1_score(label_true, label_pred)
        print(' - f1-train: {:04.2f}'.format(train_score * 100))
        print('train report :', classification_report(label_true, label_pred))
        logs['f1'] = {"epoch":epoch,"dev_score":valid_score,"train_score":train_score}
