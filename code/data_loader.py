# code/data_loader.py

import base64
from pathlib import Path

import pandas as pd


class DataLoader:
    def __init__(self, dataset_path="../dataset"):
        self.dataset_path = Path(dataset_path)

        try:
            self.claims = pd.read_csv(
                self.dataset_path / "claims.csv"
            )

            self.user_history = (
                pd.read_csv(
                    self.dataset_path / "user_history.csv"
                )
                .set_index("user_id")
                .to_dict("index")
            )

            self.evidence = pd.read_csv(
                self.dataset_path / "evidence_requirements.csv"
            )

        except Exception as e:
            raise RuntimeError(
                f"Failed loading dataset files: {e}"
            )

    def get_claims(self):
        return self.claims.to_dict("records")

    def get_user_history(self, user_id):
        return self.user_history.get(user_id)

    def get_evidence_rules(self):
        return self.evidence

    def load_images_as_base64(self, image_paths_str):
        images = []

        for image_path in image_paths_str.split(";"):

            image_path = image_path.strip()

            try:
                full_path = self.dataset_path / image_path

                with open(full_path, "rb") as f:
                    encoded = base64.b64encode(
                        f.read()
                    ).decode("utf-8")

                ext = Path(image_path).suffix.lower()

                if ext in [".jpg", ".jpeg"]:
                    media_type = "image/jpeg"
                elif ext == ".png":
                    media_type = "image/png"
                else:
                    media_type = "application/octet-stream"

                images.append(
                    {
                        "image_id": Path(image_path).stem,
                        "base64": encoded,
                        "media_type": media_type,
                        "path": image_path,
                    }
                )

            except Exception as e:
                print(
                    f"Failed loading image {image_path}: {e}"
                )

        return images