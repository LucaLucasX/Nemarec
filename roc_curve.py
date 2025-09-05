import torch
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc, average_precision_score, precision_recall_curve, plot_precision_recall_curve
from os.path import exists, join
from os import mkdir

predictionLog = "prediction.pt"
prediction_Taitan = "prediction_taitan.pt"
prediction_log = torch.load(prediction_Taitan)
prediction_log.update(torch.load(predictionLog))
classes = prediction_log["classes"]
save_folder = "roc_curves"
if not exists(save_folder):
    mkdir(save_folder)


def ROC_AUC_CAL(predictions, labels, which_class):
    actuals = []
    probabilities = []
    predictionBin = predictions.argmax(dim=1, keepdim=True)
    actuals.extend(labels.view_as(predictionBin) == which_class)
    probabilities.extend(np.exp(predictions[:, which_class]))
    return [i.item() for i in actuals], [i.item() for i in probabilities]


def performance_measure(predictions, label, networkName):
    fpr = {}
    tpr = {}
    threshold = {}
    roc_auc = {}
    fnr = {}
    EER_FPR = {}
    EER_FNR = {}
    plt.rcParams["font.family"] = "Times New Roman"
    plt.figure(figsize=(16, 9),
               dpi=150)

    lines = ['-', '--', '-.', ':']
    marks = ['x', '|', '2']
    print(label)

    for i in range(19):
        fpr[i], tpr[i], threshold[i] = roc_curve(label, predictions[:, i], pos_label=i)

        roc_auc[i] = auc(fpr[i], tpr[i])
        print("AUC: {testAUC}".format(testAUC=roc_auc[i]))
        fnr[i] = 1 - tpr[i]
        EER_FPR[i] = fpr[i][np.nanargmin(np.absolute((fnr[i] - fpr[i])))]
        EER_FNR[i] = fnr[i][np.nanargmin(np.absolute((fnr[i] - fpr[i])))]

        print("EER_FPR: {E_FPR}".format(E_FPR=EER_FPR[i]))
        print("EER_FNR: {E_FNR}".format(E_FNR=EER_FNR[i]))

        lw = 2

        plt.plot(fpr[i], tpr[i], linestyle=lines[i%len(lines)], marker=marks[i%len(marks)],
                 lw=lw, label='{} (area = %0.2f)'.format(classes[i]) % roc_auc[i])

    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('False Positive Rate', fontsize=24)
    plt.ylabel('True Positive Rate', fontsize=24)
    plt.title('Receiver Operating Characteristic (ROC) of {}'.format(networkName), fontsize=24)
    plt.legend(loc="lower right", fontsize=16, ncol=2)
    plt.savefig(join(save_folder, "{}_roc.png".format(networkName)))
    # plt.show()


includeModel = [
    "alexnet",
    "vgg16",
    "vgg19",
    "resnet34",
    "resnet50",
    "resnet101",
    "densenet121",
    "inception_v3",
    "xception",
]


for modelName in includeModel:
    key = modelName
    if key == "densenet121" or key == "inception_v3" or key == "xception":
        key += "_data_expansion_2x"

    performance_measure(prediction_log[key]["predictions"],
                        prediction_log[key]["labels"], modelName)
