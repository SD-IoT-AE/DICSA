import torch
from torch.utils.data import DataLoader, TensorDataset
from controller.modules.tsce.model import TSCEModel
from controller.modules.tsce.dataset import SequenceBuilder
from data.loaders.cic_iot_loader import CICIoTLoader
from controller.utils.config_loader import ConfigLoader


def train():

    config = ConfigLoader()

    # Load dataset
    loader = CICIoTLoader(config.get("datasets", "cic_iot_2023", "path"))
    X, y = loader.get_features_labels()

    # Build sequences
    seq_builder = SequenceBuilder(config.get("tsce", "sequence", "window_size"))
    X_seq, y_seq = seq_builder.build_sequences(X, y)

    X_tensor = torch.tensor(X_seq, dtype=torch.float32)
    y_tensor = torch.tensor(y_seq, dtype=torch.long)

    dataset = TensorDataset(X_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=config.get("tsce", "training", "batch_size"), shuffle=True)

    model = TSCEModel(
        input_dim=config.get("tsce", "model", "input_dim"),
        hidden_dim1=config.get("tsce", "model", "hidden_dim_1"),
        hidden_dim2=config.get("tsce", "model", "hidden_dim_2"),
        num_classes=config.get("tsce", "model", "num_classes"),
        dropout=config.get("tsce", "training", "dropout")
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=config.get("tsce", "training", "learning_rate"))
    loss_fn = torch.nn.CrossEntropyLoss()

    for epoch in range(config.get("tsce", "training", "epochs")):
        total_loss = 0

        for X_batch, y_batch in dataloader:
            out, _ = model(X_batch)
            loss = loss_fn(out, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch}: Loss = {total_loss:.4f}")

    torch.save(model.state_dict(), "models/bilstm_attention.pt")


if __name__ == "__main__":
    train()