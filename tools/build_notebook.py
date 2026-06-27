#!/usr/bin/env python3
"""Build the reproducible Colab notebook from reviewed source cells."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Proyecto_Final_Equipo19.ipynb"


def markdown(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": dedent(source).strip().splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(source).strip().splitlines(keepends=True),
    }


cells = [
    markdown(
        """
        # Proyecto Final - Conditional Imitation Learning - Equipo 19

        Entrenamiento reproducible para los comandos **STRAIGHT (0)**,
        **LEFT (1)** y **RIGHT (2)**. La division entrenamiento/validacion se
        realiza antes del aumento para impedir fuga entre una imagen y su reflejo.
        """
    ),
    code(
        """
        # Primera celda de codigo requerida por la actividad: clonar el dataset desde GitHub.
        import os, sys
        from pathlib import Path

        IN_COLAB = "google.colab" in sys.modules
        REPO_URL = "https://github.com/xak47d/proyecto-final-cil-equipo19.git"
        if IN_COLAB:
            PROJECT_ROOT = Path("/content/proyecto-final-cil-equipo19")
            if not PROJECT_ROOT.exists():
                !git clone https://github.com/xak47d/proyecto-final-cil-equipo19.git /content/proyecto-final-cil-equipo19
            !pip install -q -r /content/proyecto-final-cil-equipo19/requirements_colab.txt
        else:
            PROJECT_ROOT = Path.cwd()

        print("Proyecto:", PROJECT_ROOT)
        """
    ),
    markdown(
        """
        ## 1. Configuracion reproducible

        Se fijan semillas y se centralizan dimensiones, lote y rutas. El
        preprocesamiento se replica exactamente en el controlador de Webots.
        """
    ),
    code(
        """
        import json, math, random, shutil
        from collections import Counter
        from pathlib import Path

        import cv2
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        import tensorflow as tf
        from sklearn.model_selection import train_test_split
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
        from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten, Dropout, Concatenate
        from tensorflow.keras.models import Model
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.utils import Sequence, to_categorical

        SEED = 19
        random.seed(SEED)
        np.random.seed(SEED)
        tf.random.set_seed(SEED)

        IMG_H, IMG_W = 80, 160
        BATCH_SIZE = 32
        EPOCHS = 12
        COMMANDS = {0: "STRAIGHT", 1: "LEFT", 2: "RIGHT"}

        RAW_DIR = PROJECT_ROOT / "dataset"
        RAW_IMAGES = RAW_DIR / "images"
        RAW_CSV = RAW_DIR / "driving_log.csv"
        AUG_DIR = PROJECT_ROOT / "dataset_augmented"
        AUG_IMAGES = AUG_DIR / "images"
        AUG_CSV = AUG_DIR / "driving_log_augmented.csv"
        FIGURES = PROJECT_ROOT / "docs" / "figures"
        MODEL_DIR = PROJECT_ROOT / "controllers" / "cil_autonomous_driver"
        FIGURES.mkdir(parents=True, exist_ok=True)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        """
    ),
    markdown(
        """
        ## 2. Auditoria del dataset original

        Se valida el esquema, los tres comandos permitidos y la correspondencia
        uno-a-uno entre registros e imagenes antes de entrenar.
        """
    ),
    code(
        """
        raw_df = pd.read_csv(RAW_CSV)
        assert list(raw_df.columns) == ["image", "steering_angle", "command"]
        assert set(raw_df["command"].unique()) == set(COMMANDS)
        assert raw_df["image"].is_unique
        missing = [name for name in raw_df["image"] if not (RAW_IMAGES / name).exists()]
        assert not missing, f"Imagenes faltantes: {missing[:5]}"

        raw_df["source_id"] = raw_df["image"].map(lambda name: Path(name).stem)
        print("Registros originales:", len(raw_df))
        print(raw_df["command"].map(COMMANDS).value_counts())
        display(raw_df.head())

        counts = raw_df["command"].map(COMMANDS).value_counts().reindex(COMMANDS.values())
        ax = counts.plot(kind="bar", color=["#2E74B5", "#70AD47", "#ED7D31"])
        ax.set_title("Distribucion original por comando")
        ax.set_ylabel("Imagenes")
        ax.set_xlabel("")
        plt.tight_layout()
        plt.savefig(FIGURES / "command_distribution_original.png", dpi=180)
        plt.show()
        """
    ),
    markdown(
        """
        ## 3. Division por fuente y aumento

        La division estratificada ocurre sobre las imagenes originales. Solo
        despues se crean reflejos; LEFT y RIGHT se intercambian al reflejar.
        Para equilibrar STRAIGHT se agregan dos variantes de brillo.
        """
    ),
    code(
        """
        train_raw, val_raw = train_test_split(
            raw_df,
            test_size=0.20,
            random_state=SEED,
            stratify=raw_df["command"],
        )
        train_sources = set(train_raw["source_id"])
        val_sources = set(val_raw["source_id"])
        assert train_sources.isdisjoint(val_sources)

        expected_signature = {
            "seed": SEED,
            "raw_records": len(raw_df),
            "train_sources": len(train_raw),
            "validation_sources": len(val_raw),
            "commands": COMMANDS,
        }
        signature_path = AUG_DIR / "augmentation_signature.json"
        rebuild = True
        if signature_path.exists() and AUG_CSV.exists():
            rebuild = json.loads(signature_path.read_text()) != expected_signature

        if rebuild:
            if AUG_DIR.exists():
                shutil.rmtree(AUG_DIR)
            AUG_IMAGES.mkdir(parents=True, exist_ok=True)
            augmented_rows = []

            def save_variant(row, split, variant, image, steering, command):
                output_name = f"{split}_{variant}_{row.image}"
                ok = cv2.imwrite(str(AUG_IMAGES / output_name), image)
                if not ok:
                    raise IOError(f"No se pudo escribir {output_name}")
                augmented_rows.append({
                    "image": output_name,
                    "steering_angle": float(steering),
                    "command": int(command),
                    "source_id": row.source_id,
                    "split": split,
                    "variant": variant,
                })

            for row in train_raw.itertuples(index=False):
                image = cv2.imread(str(RAW_IMAGES / row.image))
                save_variant(row, "train", "original", image, row.steering_angle, row.command)
                flipped_command = 2 if row.command == 1 else 1 if row.command == 2 else 0
                save_variant(row, "train", "flip", cv2.flip(image, 1), -row.steering_angle, flipped_command)
                if row.command == 0:
                    darker = cv2.convertScaleAbs(image, alpha=0.75, beta=0)
                    brighter_flip = cv2.convertScaleAbs(cv2.flip(image, 1), alpha=1.20, beta=0)
                    save_variant(row, "train", "dark", darker, row.steering_angle, 0)
                    save_variant(row, "train", "bright_flip", brighter_flip, -row.steering_angle, 0)

            for row in val_raw.itertuples(index=False):
                image = cv2.imread(str(RAW_IMAGES / row.image))
                save_variant(row, "validation", "original", image, row.steering_angle, row.command)

            augmented_df = pd.DataFrame(augmented_rows)
            AUG_DIR.mkdir(parents=True, exist_ok=True)
            augmented_df.to_csv(AUG_CSV, index=False)
            signature_path.write_text(json.dumps(expected_signature, indent=2))
        else:
            augmented_df = pd.read_csv(AUG_CSV)

        train_df = augmented_df.query("split == 'train'").reset_index(drop=True)
        val_df = augmented_df.query("split == 'validation'").reset_index(drop=True)
        assert set(train_df.source_id).isdisjoint(set(val_df.source_id))
        assert len(augmented_df) > 10_000
        print("Muestras finales:", len(augmented_df))
        print("Entrenamiento:", len(train_df), "Validacion:", len(val_df))
        print(train_df["command"].map(COMMANDS).value_counts())
        """
    ),
    markdown(
        """
        ## 4. Generador y preprocesamiento

        La camara se recorta 25% desde arriba para reducir cielo/edificios,
        cambia a RGB, redimensiona a 160x80 y normaliza a [0, 1].
        """
    ),
    code(
        """
        def preprocess_image(path):
            image = cv2.imread(str(path))
            if image is None:
                raise FileNotFoundError(path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image[int(image.shape[0] * 0.25):, :, :]
            image = cv2.resize(image, (IMG_W, IMG_H), interpolation=cv2.INTER_AREA)
            return image.astype(np.float32) / 255.0

        class CILSequence(Sequence):
            def __init__(self, dataframe, shuffle=True, **kwargs):
                super().__init__(**kwargs)
                self.df = dataframe.reset_index(drop=True)
                self.shuffle = shuffle
                self.indexes = np.arange(len(self.df))
                self.on_epoch_end()

            def __len__(self):
                return int(np.ceil(len(self.df) / BATCH_SIZE))

            def __getitem__(self, index):
                ids = self.indexes[index * BATCH_SIZE:(index + 1) * BATCH_SIZE]
                batch = self.df.iloc[ids]
                images = np.stack([preprocess_image(AUG_IMAGES / name) for name in batch.image])
                commands = to_categorical(batch.command.astype(int), num_classes=3)
                steering = batch.steering_angle.to_numpy(dtype=np.float32)
                return (images, commands), steering

            def on_epoch_end(self):
                if self.shuffle:
                    np.random.shuffle(self.indexes)

        train_gen = CILSequence(train_df, shuffle=True)
        val_gen = CILSequence(val_df, shuffle=False)
        sample_inputs, sample_targets = train_gen[0]
        print(sample_inputs[0].shape, sample_inputs[1].shape, sample_targets.shape)
        """
    ),
    markdown(
        """
        ## 5. CNN condicionada

        La rama visual comparte cinco capas convolucionales. El comando one-hot
        se concatena antes de las capas densas para condicionar el angulo.
        """
    ),
    code(
        """
        image_input = Input(shape=(IMG_H, IMG_W, 3), name="image_input")
        x = Conv2D(24, 5, strides=2, activation="relu")(image_input)
        x = Conv2D(36, 5, strides=2, activation="relu")(x)
        x = Conv2D(48, 5, strides=2, activation="relu")(x)
        x = Conv2D(64, 3, activation="relu")(x)
        x = Conv2D(64, 3, activation="relu")(x)
        x = Flatten()(x)

        command_input = Input(shape=(3,), name="command_input")
        x = Concatenate()([x, command_input])
        x = Dense(100, activation="relu")(x)
        x = Dropout(0.30)(x)
        x = Dense(50, activation="relu")(x)
        x = Dense(10, activation="relu")(x)
        steering_output = Dense(1, name="steering_output")(x)

        model = Model([image_input, command_input], steering_output, name="CIL_Equipo19")
        model.compile(optimizer=Adam(1e-4), loss="mse", metrics=["mae"])
        model.summary()
        """
    ),
    markdown("## 6. Entrenamiento con callbacks"),
    code(
        """
        checkpoint = MODEL_DIR / "cil_model_best.h5"
        callbacks = [
            EarlyStopping(monitor="val_mae", patience=3, restore_best_weights=True, mode="min"),
            ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6),
            ModelCheckpoint(checkpoint, monitor="val_mae", save_best_only=True, mode="min"),
        ]
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=EPOCHS,
            callbacks=callbacks,
            verbose=1,
        )
        """
    ),
    markdown("## 7. Curvas y evaluacion por comando"),
    code(
        """
        history_df = pd.DataFrame(history.history)
        history_df.to_csv(FIGURES / "training_history.csv", index=False)
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].plot(history_df.loss, label="train")
        axes[0].plot(history_df.val_loss, label="validation")
        axes[0].set_title("MSE")
        axes[0].set_xlabel("Epoca")
        axes[0].legend()
        axes[1].plot(history_df.mae, label="train")
        axes[1].plot(history_df.val_mae, label="validation")
        axes[1].axhline(0.05, color="red", linestyle="--", label="objetivo 0.05")
        axes[1].set_title("MAE (rad)")
        axes[1].set_xlabel("Epoca")
        axes[1].legend()
        plt.tight_layout()
        plt.savefig(FIGURES / "training_curves.png", dpi=180)
        plt.show()

        predictions = model.predict(val_gen, verbose=0).reshape(-1)
        actual = val_df.steering_angle.to_numpy(dtype=np.float32)
        evaluation = []
        for command, name in COMMANDS.items():
            mask = val_df.command.to_numpy() == command
            evaluation.append({
                "command": name,
                "samples": int(mask.sum()),
                "mae_rad": float(np.mean(np.abs(predictions[mask] - actual[mask]))),
            })
        metrics = {
            "validation_mae_rad": float(np.mean(np.abs(predictions - actual))),
            "validation_mse": float(np.mean(np.square(predictions - actual))),
            "per_command": evaluation,
            "augmented_samples": int(len(augmented_df)),
            "train_samples": int(len(train_df)),
            "validation_samples": int(len(val_df)),
            "source_overlap": 0,
        }
        print(json.dumps(metrics, indent=2))
        display(pd.DataFrame(evaluation))
        """
    ),
    markdown("## 8. Exportacion para Webots"),
    code(
        """
        final_model = MODEL_DIR / "cil_model.h5"
        model.save(final_model)
        metadata = {
            "image_height": IMG_H,
            "image_width": IMG_W,
            "channels": 3,
            "crop_top_ratio": 0.25,
            "normalization": "uint8/255.0",
            "commands": {str(key): value for key, value in COMMANDS.items()},
            "seed": SEED,
            "validation_mae_target_rad": 0.05,
        }
        (MODEL_DIR / "model_metadata.json").write_text(json.dumps(metadata, indent=2))
        (MODEL_DIR / "training_metrics.json").write_text(json.dumps(metrics, indent=2))
        print("Modelo:", final_model)
        print("MAE validacion:", metrics["validation_mae_rad"])
        assert metrics["validation_mae_rad"] <= 0.05, "El modelo no alcanza el objetivo MAE"
        """
    ),
    markdown(
        """
        ## Conclusion

        El artefacto exportado conserva tres comandos verificables y un
        preprocesamiento documentado. La validacion final se realiza en World 2
        mediante las rutas recta, derecha e izquierda y el arbitro de seguridad.
        """
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": [], "gpuType": "T4"},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(OUTPUT)
