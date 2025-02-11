# Apply ReLU to feature extraction
class ReLu:

    @staticmethod
    def apply(tensor):
        binary_numbers = [1 if num > 0.5 else 0 for num in tensor]
        return binary_numbers
