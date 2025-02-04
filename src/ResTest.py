import torch
from PIL import Image
from torchvision import transforms

bare_model = torch.hub.load('pytorch/vision', 'resnet152', pretrained=True)

model = torch.nn.Sequential(*list(bare_model.children())[:-1])
model.eval()

input_image = Image.open("images_shadow.JPG")
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
input_tensor = preprocess(input_image)
input_batch = input_tensor.unsqueeze(0)

if torch.cuda.is_available():
    input_batch = input_batch.to('cuda')
    model.to('cuda')

with torch.no_grad():
    output = model(input_batch)

flatten_tensor = torch.flatten(output[0])

for e in flatten_tensor:
    print(e.item())
