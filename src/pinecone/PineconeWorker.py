import torch
from PIL import Image
from torchvision import transforms

from src.configuration.Logger import Logger as log


class PineconeWorker:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            log.info("Loading model...")
            bare_model = torch.hub.load('pytorch/vision', 'resnet152', pretrained=True)
            log.debug("Model loaded.")
            log.debug("Removing classification layer.")
            cls._model = torch.nn.Sequential(*list(bare_model.children())[:-1])
            cls._model.eval()

            log.info("Model is ready to use.")
        return cls._instance

    @staticmethod
    def process_frame(image_path):
        log.info(f"Processing image with path %{image_path}")
        input_image = Image.open(image_path)
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0)

        generator = PineconeWorker()
        print(generator)
        if torch.cuda.is_available():
            input_batch = input_batch.to('cuda')
            generator._model.to('cuda')

        with torch.no_grad():
            output = generator._model(input_batch)

        flatten_tensor = torch.flatten(output[0])
        log.debug(f"Retrieved flatten tensor from image %{flatten_tensor}")
        return flatten_tensor
