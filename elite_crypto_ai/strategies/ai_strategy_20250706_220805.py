import pandas as pd

class Strategy:
    def generate_signals(self, data: pd.DataFrame) -> list[str]:
        # Placeholder for signals
        signals = []

        # Iterate over data
        for i in range(len(data)):
            # Example logic for generating signals
            if data['close'].iloc[i] > data['open'].iloc[i]:
                signals.append('buy')
            elif data['close'].iloc[i] < data['open'].iloc[i]:
                signals.append('sell')
            else:
                signals.append('hold')

        # Ensure that the length of signals always matches len(data)
        if len(signals) != len(data):
            signals = ['hold'] * len(data)

        return signals