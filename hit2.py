import numpy as np
from scipy.io.wavfile import write

# 音效參數
sample_rate = 44100  # 取樣率
duration = 0.2  # 時長（秒）
frequency = 600  # 頻率（Hz）

# 生成正弦波
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * frequency * t)

# 保存為 WAV 檔案
write("hit2.wav", sample_rate, (audio * 32767).astype(np.int16))
print("生成 hit2.wav 完成！")
