import numpy as np
import os
import logging
import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend for servers
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score,
)
from src.model_utils import predict_proba


def generate_evaluation_reports_and_plots(df, model, tokenizer, device, config):
    """
    Generates evaluation reports and plots, saving them to the specified output directory.

    Parameters:
        df (pd.DataFrame): DataFrame containing the data and predictions.
        model: The trained model.
        tokenizer: The tokenizer used for the model.
        device: The device ('cpu' or 'cuda') on which to run the model.
        config (dict): Configuration dictionary.

    Returns:
        None
    """
    try:
        logging.info("Generating evaluation reports and plots...")

        # Get true labels
        true_labels = df["yo2"]

        # Get predicted probabilities
        logging.info("Calculating predicted probabilities...")
        df["predicted_proba"] = predict_proba(
            texts=df["full_text"].tolist(),
            model=model,
            tokenizer=tokenizer,
            device=device,
            config=config,
        )

        # Convert predicted probabilities to binary labels (threshold of 0.5)
        df["predicted_yo2"] = (df["predicted_proba"] >= 0.5).astype(int)

        # Get binary predicted labels
        predicted_labels = df["predicted_yo2"]

        # Ensure the evaluation output directory exists
        output_dir = config["evaluation"]["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        # Generate and save confusion matrix
        plot_confusion_matrix(true_labels, predicted_labels, output_dir)

        # Generate and save classification report
        generate_classification_report(true_labels, predicted_labels, output_dir)

        # Generate and save ROC curve
        plot_roc_curve(true_labels, df["predicted_proba"], output_dir)

        # Generate and save Precision-Recall curve
        plot_precision_recall_curve(true_labels, df["predicted_proba"], output_dir)

        logging.info("Evaluation reports and plots generated successfully.")

    except Exception as e:
        logging.error(f"Failed to generate evaluation reports and plots: {e}")


def plot_confusion_matrix(true_labels, predicted_labels, output_dir):
    try:
        unique_labels = np.unique(np.concatenate([true_labels, predicted_labels]))
        if len(unique_labels) == 1:
            cm = confusion_matrix(
                true_labels, predicted_labels, labels=[unique_labels[0]]
            )
            disp = ConfusionMatrixDisplay(
                confusion_matrix=cm, display_labels=[str(unique_labels[0])]
            )
        else:
            cm = confusion_matrix(true_labels, predicted_labels)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)

        disp.plot(cmap=plt.cm.Blues)
        plt.title("Confusion Matrix")
        plot_path = os.path.join(output_dir, "confusion_matrix.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Confusion matrix saved to {plot_path}.")
    except Exception as e:
        logging.error(f"Failed to generate confusion matrix: {e}")


def generate_classification_report(true_labels, predicted_labels, output_dir):
    try:
        unique_labels = np.unique(np.concatenate([true_labels, predicted_labels]))
        if len(unique_labels) == 1:
            report = classification_report(
                true_labels,
                predicted_labels,
                labels=[unique_labels[0]],
                target_names=[str(unique_labels[0])],
            )
        else:
            report = classification_report(true_labels, predicted_labels)

        report_file = os.path.join(output_dir, "classification_report.txt")
        with open(report_file, "w") as f:
            f.write(report)
        logging.info(f"Classification report saved to {report_file}.")
    except Exception as e:
        logging.error(f"Failed to generate classification report: {e}")


def plot_roc_curve(true_labels, predicted_probabilities, output_dir):
    try:
        fpr, tpr, _ = roc_curve(true_labels, predicted_probabilities)
        roc_auc = auc(fpr, tpr)
        plt.figure()
        plt.plot(
            fpr,
            tpr,
            color="darkorange",
            lw=2,
            label=f"ROC Curve (AUC = {roc_auc:0.2f})",
        )
        plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("Receiver Operating Characteristic")
        plt.legend(loc="lower right")
        plot_path = os.path.join(output_dir, "roc_curve.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"ROC curve saved to {plot_path}.")
    except Exception as e:
        logging.error(f"Failed to generate ROC curve: {e}")


def plot_precision_recall_curve(true_labels, predicted_probabilities, output_dir):
    try:
        precision, recall, _ = precision_recall_curve(
            true_labels, predicted_probabilities
        )
        avg_precision = average_precision_score(true_labels, predicted_probabilities)
        plt.figure()
        plt.plot(
            recall,
            precision,
            color="b",
            lw=2,
            label=f"Avg Precision = {avg_precision:0.2f}",
        )
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision-Recall Curve")
        plt.legend(loc="lower left")
        plot_path = os.path.join(output_dir, "precision_recall_curve.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Precision-Recall curve saved to {plot_path}.")
    except Exception as e:
        logging.error(f"Failed to generate Precision-Recall curve: {e}")
