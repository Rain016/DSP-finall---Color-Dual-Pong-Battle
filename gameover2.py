import numpy as np
from scipy.io.wavfile import write

# 音效參數
sample_rate = 44100
duration = 1.0
frequencies = [400, 300, 200]  # 遞減音高

# 生成音效
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = sum(0.5 * np.sin(2 * np.pi * f * t) for f in frequencies)

# 保存為 WAV 檔案
write("game_over2.wav", sample_rate, (audio * 32767).astype(np.int16))
print("生成 game_over.wav 完成！")
