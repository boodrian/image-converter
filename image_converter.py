import os
import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QHBoxLayout, QSpinBox, QPushButton,
    QFileDialog, QMainWindow, QWidget, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt


from PIL import Image

# Configurazione del logging
LOG_FILENAME = "image_converter_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler()
    ]
)

class ImageConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.output_format = "PNG"
        self.resize_width = None
        self.resize_height = None
        self.compression_quality = 85  # Default JPEG quality
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Image Converter")
        self.setGeometry(100, 100, 400, 400)

        # Layout principale
        layout = QVBoxLayout()

        # Etichetta
        self.label = QLabel("Benvenuto nell'Image Converter!")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        # Pulsante per selezionare immagini
        select_btn = QPushButton("Seleziona Immagini")
        select_btn.clicked.connect(self.select_images)
        layout.addWidget(select_btn)

        # Selezione del formato di output
        format_label = QLabel("Seleziona formato di output:")
        layout.addWidget(format_label)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "BMP", "GIF", "TIFF"])
        layout.addWidget(self.format_combo)

        # Impostazioni per ridimensionamento
        resize_label = QLabel("Opzionale: Inserisci larghezza e altezza (lascia vuoto per mantenere le dimensioni originali):")
        layout.addWidget(resize_label)

        resize_layout = QHBoxLayout()

        self.width_input = QSpinBox()
        self.width_input.setRange(0, 10000) # Intervallo per la larghezza (0 = lascia invariato)
        self.width_input.setValue(0) # Valore predefinito
        self.width_input.setPrefix("Larghezza: ")
        resize_layout.addWidget(self.width_input)

        self.height_input = QSpinBox()
        self.height_input.setRange(0, 10000) # Intervallo per l'altezza (0 = lascia invariato)
        self.height_input.setValue(0) # Valore predefinito
        self.height_input.setPrefix("Altezza: ")
        resize_layout.addWidget(self.height_input)

        layout.addLayout(resize_layout)

        # Impostazioni di compressione
        quality_label = QLabel("Qualità di compressione (solo per JPEG):")
        layout.addWidget(quality_label)
        self.quality_input = QSpinBox()
        self.quality_input.setRange(10, 100)
        self.quality_input.setValue(85)
        layout.addWidget(self.quality_input)

        # Pulsante per convertire immagini
        convert_btn = QPushButton("Converti Immagini")
        convert_btn.clicked.connect(self.convert_images)
        layout.addWidget(convert_btn)

        # Widget principale
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_images(self):
        logging.debug("Selezione immagini avviata...")
        file_dialog = QFileDialog(self)
        files, _ = file_dialog.getOpenFileNames(
            caption="Seleziona Immagini",
            filter="Image files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"
        )
        if files:
            self.image_paths = files
            self.label.setText(f"{len(files)} immagini selezionate.")
            logging.info(f"Immagini selezionate: {files}")
        else:
            logging.warning("Nessuna immagine selezionata.")

    def convert_images(self):
        if not self.image_paths:
            QMessageBox.warning(self, "Errore", "Nessuna immagine selezionata!")
            logging.error("Tentativo di conversione senza immagini selezionate.")
            return

        self.output_format = self.format_combo.currentText()
        self.resize_width = self.width_input.value() if self.width_input.value() > 0 else None
        self.resize_height = self.height_input.value() if self.height_input.value() > 0 else None
        self.compression_quality = self.quality_input.value()

        for image_path in self.image_paths:
            try:
                logging.debug(f"Inizio conversione per: {image_path}")
                img = Image.open(image_path)
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_dir = os.path.join(os.path.dirname(image_path), "output_converted")
                os.makedirs(output_dir, exist_ok=True)  # Creazione directory di output

                output_path = os.path.join(output_dir, f"{base_name}.{self.output_format.lower()}")
                logging.debug(f"Percorso di salvataggio generato: {output_path}")

                # Ridimensionamento
                if self.resize_width or self.resize_height:
                    new_width = self.resize_width or img.width
                    new_height = self.resize_height or img.height
                    logging.debug(f"Ridimensionamento a: {new_width}x{new_height}")
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    logging.debug("Ridimensionamento non applicato: larghezza e altezza lasciate vuote.")

                # Salvataggio immagine
                if self.output_format == "JPEG":
                    logging.debug(f"Salvataggio immagine come JPEG con qualità {self.compression_quality}")
                    img.save(output_path, self.output_format, quality=self.compression_quality, optimize=True)
                else:
                    logging.debug(f"Salvataggio immagine come {self.output_format}")
                    img.save(output_path, self.output_format)

                logging.info(f"Immagine convertita con successo: {output_path}")

            except Exception as e:
                logging.error(f"Errore durante la conversione di {image_path}: {e}", exc_info=True)
                QMessageBox.critical(self, "Errore", f"Errore durante la conversione di {image_path}: {e}")

        QMessageBox.information(self, "Conversione Completata", "Tutte le immagini sono state convertite!")
        self.label.setText("Conversione completata con successo.")
        logging.debug("Conversione completata con successo.")

# Avvio dell'applicazione
def main():
    try:
        app = QApplication(sys.argv)
        window = ImageConverterApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Errore critico durante l'esecuzione dell'app: {e}", exc_info=True)

if __name__ == "__main__":
    main()
