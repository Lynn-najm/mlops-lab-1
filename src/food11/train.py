import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights


mlflow.set_tracking_uri("http://127.0.0.1:5001")
mlflow.set_experiment("food11")


def get_data_loaders(dataset_type, batch_size):
    if dataset_type == "mini":
        data_dir = Path("data/food11_processed_mini")
    else:
        data_dir = Path("data/food11_processed")

    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])

    train_dataset = datasets.ImageFolder(
        data_dir / "training",
        transform=transform
    )

    val_dataset = datasets.ImageFolder(
        data_dir / "validation",
        transform=transform
    )

    test_dataset = datasets.ImageFolder(
        data_dir / "evaluation",
        transform=transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    return train_loader, val_loader, test_loader


def evaluate(model, loader, loss_fn, device):
    model.eval()

    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = loss_fn(outputs, labels)

            total_loss += loss.item()

            predictions = outputs.argmax(dim=1)

            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    average_loss = total_loss / len(loader)
    accuracy = correct / total

    return average_loss, accuracy


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        choices=["mini", "full"],
        default="mini"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.001
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32
    )

    args = parser.parse_args()

    if torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print("Using device:", device)

    train_loader, val_loader, test_loader = get_data_loaders(
        args.dataset,
        args.batch_size
    )

    weights = ResNet18_Weights.DEFAULT
    model = resnet18(weights=weights)

    model.fc = nn.Linear(
        model.fc.in_features,
        11
    )

    model = model.to(device)

    loss_fn = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr
    )

    with mlflow.start_run():

        mlflow.log_param("dataset", args.dataset)
        mlflow.log_param("epochs", args.epochs)
        mlflow.log_param("learning_rate", args.lr)
        mlflow.log_param("batch_size", args.batch_size)
        mlflow.log_param("device", str(device))

        for epoch in range(args.epochs):

            model.train()

            total_train_loss = 0

            for images, labels in train_loader:
                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(images)

                loss = loss_fn(outputs, labels)

                loss.backward()

                optimizer.step()

                total_train_loss += loss.item()

            train_loss = total_train_loss / len(train_loader)

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                loss_fn,
                device
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Accuracy: {val_accuracy:.4f}"
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch
            )

        test_loss, test_accuracy = evaluate(
            model,
            test_loader,
            loss_fn,
            device
        )

        print("Test Accuracy:", test_accuracy)

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy
        )

        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle"
        )


if __name__ == "__main__":
    main()