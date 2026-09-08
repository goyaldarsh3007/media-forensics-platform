import os
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

try:
    import kagglehub
except Exception:
    kagglehub = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "custom_ai_vs_human_model.pth"
DATASET_DIR = PROJECT_ROOT / "datasets" / "cifake"


class RealFakeDataset(Dataset):
    def __init__(self, root_dir, transform=None, limit_per_class=None):
        self.transform = transform
        self.samples = []

        label_map = {
            "REAL": 0,
            "FAKE": 1,
        }

        for class_name, label in label_map.items():
            class_dir = Path(root_dir) / class_name
            if not class_dir.exists():
                continue

            files = []
            for ext in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
                files.extend(sorted(class_dir.glob(f"*{ext}")))
                files.extend(sorted(class_dir.glob(f"*{ext.upper()}")))

            if limit_per_class is not None:
                files = files[:limit_per_class]

            for image_path in files:
                self.samples.append((str(image_path), float(label)))

        if not self.samples:
            raise FileNotFoundError(f"No labeled CIFAKE images found in {root_dir}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        image_path, label = self.samples[idx]
        image = Image.open(image_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, torch.tensor(label, dtype=torch.float32)


class CustomAIImageClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)


def build_transform():
    return transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
    ])


def find_cifake_dataset(root_dir: Path | None = None):
    search_roots = []
    if root_dir is not None:
        search_roots.append(Path(root_dir))
    search_roots.extend([
        DATASET_DIR,
        PROJECT_ROOT / "cifake",
        PROJECT_ROOT / "dataset",
        Path.home() / ".cache" / "kagglehub",
    ])

    for base in search_roots:
        if not base.exists():
            continue

        for candidate in base.rglob("train"):
            if (candidate / "REAL").exists() and (candidate / "FAKE").exists():
                return candidate.parent

        for candidate in base.rglob("test"):
            if (candidate / "REAL").exists() and (candidate / "FAKE").exists():
                return candidate.parent

    return None


def ensure_cifake_dataset(root_dir: Path | None = None):
    dataset_root = find_cifake_dataset(root_dir)
    if dataset_root is not None:
        return dataset_root

    if kagglehub is None:
        raise RuntimeError("kagglehub is not installed. Install it with pip install kagglehub.")

    downloaded = kagglehub.dataset_download("birdy654/cifake-real-and-ai-generated-synthetic-images")
    dataset_root = Path(downloaded)
    if (dataset_root / "train" / "REAL").exists() and (dataset_root / "train" / "FAKE").exists():
        return dataset_root

    raise FileNotFoundError("CIFAKE dataset was not downloaded correctly.")


def train_custom_model(dataset_root: Path | None = None, output_path: Path = MODEL_PATH, epochs: int = 2, batch_size: int = 32, learning_rate: float = 1e-3, max_samples_per_class: int | None = 2000):
    dataset_root = Path(ensure_cifake_dataset(dataset_root))
    train_root = dataset_root / "train"
    val_root = dataset_root / "test"

    if not train_root.exists() or not val_root.exists():
        raise FileNotFoundError(f"Expected CIFAKE dataset folders under {dataset_root}, but train/test were not found.")

    train_dataset = RealFakeDataset(train_root, transform=build_transform(), limit_per_class=max_samples_per_class)
    val_dataset = RealFakeDataset(val_root, transform=build_transform(), limit_per_class=max_samples_per_class)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = CustomAIImageClassifier()
    criterion = nn.BCELoss()
    optimizer = Adam(model.parameters(), lr=learning_rate)

    best_val_loss = float("inf")
    for _ in range(epochs):
        model.train()
        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images).squeeze(1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

        model.eval()
        total_val_loss = 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                outputs = model(images).squeeze(1)
                total_val_loss += criterion(outputs, labels).item()

        avg_val_loss = total_val_loss / max(len(val_loader), 1)
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            output_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), output_path)

    return output_path


def ensure_model_exists(model_path: Path = MODEL_PATH):
    if model_path.exists():
        return model_path
    return train_custom_model(DATASET_DIR, model_path)


def predict_ai_probability(image_path: str | os.PathLike, model_path: Path = MODEL_PATH):
    if not Path(model_path).exists():
        ensure_model_exists(model_path)

    model = CustomAIImageClassifier()
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    image = Image.open(image_path).convert("RGB")
    tensor = build_transform()(image).unsqueeze(0)
    with torch.no_grad():
        probability = model(tensor).item()

    return float(min(1.0, max(0.0, probability)))


if __name__ == "__main__":
    ensure_model_exists()
    print(f"Training finished. Model ready at {MODEL_PATH}")
