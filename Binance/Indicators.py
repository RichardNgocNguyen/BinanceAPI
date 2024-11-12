import numpy as np


# <== Calling class requires this format... "Indicator(open, high, low, close, volume)"
# WILDER, EMA, SMA, ATR, ADX, DMI, CCI, RSI, RSI Divergence, SR Levels, MACD, BOLL, Accumulation, Volume Osc
class INDICATORS:
    def __init__(self, date, opens, highs, lows, closes, volume):
        self.date = np.array(date)
        self.opens = np.array(opens)
        self.highs = np.array(highs)
        self.lows = np.array(lows)
        self.closes = np.array(closes)
        self.volumes = np.array(volume)


    def WILDER(self, array: list, period=14):
        new = [sum(array[0:period]) / period]
        for i in range(period, len(array)):
            new_v = (new[-1] * (period - 1) + array[i]) / period
            new.append(new_v)
        return np.array(new)


    def EMA(self, array=None, period=14):
        if array is None:
            array = self.closes
        ema_series = []
        sma = sum(array[0:period]) / period
        multiplier = 2.0 / (period + 1)
        ema_series.append(sma)
        for i in range(int(period), len(array)):
            ema = ((array[i]) * multiplier) + (ema_series[-1] * (1.0 - multiplier))
            ema_series.append(ema)
        return np.array(ema_series)


    def SMA(self, array=None, period=14):
        if array is None:
            array = self.closes
        sma_series = []
        for i in range(period, len(array)):
            begin = i - period
            end = i
            sma = sum(array[begin + 1:end + 1]) / period
            sma_series.append(sma)
        return np.array(sma_series)


    def ATR(self, period=14):
        true_range_series = []
        for i in range(len(self.closes)):
            true_range = max(float(self.highs[i] - self.lows[i]),
                             abs(float(self.highs[i] - self.closes[i - 1])),
                             abs(float(self.lows[i] - self.closes[i - 1])))
            true_range_series.append(true_range)
        return self.WILDER(true_range_series, period)[1:]


    def ADX(self, period=14):
        return self.DMI(period)["adx"]


    def DMI(self, period=14):
        dm_plus_series = []
        dm_minus_series = []
        di_plus_series = []
        di_minus_series = []
        dx_series = []

        for i in range(len(self.closes)):
            if i == 0:
                dm_plus_series.append(None)
                dm_minus_series.append(None)
            else:
                if (self.highs[i] - self.highs[i - 1]) > (self.lows[i - 1] - self.lows[i]):
                    dm_plus = float(self.highs[i] - self.highs[i - 1])
                    if dm_plus < 0:
                        dm_plus = 0
                else:
                    dm_plus = 0

                if (self.lows[i - 1] - self.lows[i]) > (self.highs[i] - self.highs[i - 1]):
                    dm_minus = float(self.lows[i - 1] - self.lows[i])
                    if dm_minus < 0:
                        dm_minus = 0
                else:
                    dm_minus = 0
                dm_plus_series.append(dm_plus)
                dm_minus_series.append(dm_minus)

        smoothed_dm_plus = self.WILDER(dm_plus_series[1:], period)
        smoothed_dm_minus = self.WILDER(dm_minus_series[1:], period)

        smoothed_atr = self.ATR(period)
        for j in range(len(smoothed_atr)):
            di_plus = (smoothed_dm_plus[j] / smoothed_atr[j]) * 100
            di_minus = (smoothed_dm_minus[j] / smoothed_atr[j]) * 100

            di_plus_series.append(di_plus)
            di_minus_series.append(di_minus)

            try:
                dx = (abs(di_plus - di_minus) / abs(di_plus + di_minus)) * 100
            except ZeroDivisionError:
                dx = 0

            dx_series.append(dx)

        adx_series = self.WILDER(dx_series, period)
        return {"plus": np.array(di_plus_series), "minus": np.array(di_minus_series), "adx": np.array(adx_series)}


    def CCI(self, period=20):
        hlc3 = [(self.highs[i] + self.lows[i] + self.closes[i]) / 3 for i in range(len(self.closes))]

        sma = self.SMA(hlc3, period)
        hlc3 = hlc3[period:]

        cci = []
        for i in range(period, len(sma)):
            deviation = np.mean(np.absolute(hlc3[i - period + 1:i + 1] - np.mean(hlc3[i - period + 1:i + 1])))

            calc = (hlc3[i] - sma[i]) / (0.015 * deviation)
            cci.append(calc)
        return np.array(cci)


    def RSI(self, period=14):
        pos = 0
        gain = 0
        loss = 0
        output = []
        for i in range(1, period + 1):
            change = self.closes[i] - self.closes[i - 1]
            if change >= 0:
                gain += abs(change)
            elif change < 0:
                loss += abs(change)
            pos = i
        avg_gain = gain / period
        avg_loss = loss / period
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        if np.isnan(rsi):
            rsi = 0.0
        output.append(rsi)
        for j in range(pos + 1, len(self.closes)):
            change = self.closes[j] - self.closes[j - 1]
            if change >= 0:
                avg_gain = ((avg_gain * (period - 1)) + abs(change)) / period
                avg_loss = ((avg_loss * (period - 1)) + 0) / period
            elif change < 0:
                avg_gain = ((avg_gain * (period - 1)) + 0) / period
                avg_loss = ((avg_loss * (period - 1)) + abs(change)) / period
            rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
            if np.isnan(rsi):
                rsi = 0.0
            output.append(rsi)
        return output


    def RSI_DIVERGENCE(self, inspect_left=5, inspect_right=5, lookback_range=60, period=14, verbose=False):
        divergence = {}
        hidden_divergence = {}
        index_of_highs = []
        index_of_lows = []

        rsi_series = self.RSI()
        for i in range(inspect_left, len(rsi_series) - inspect_right):
            left_max = max(rsi_series[i - inspect_left:i])
            right_max = max(rsi_series[i + 1: inspect_right + i + 1])
            if rsi_series[i] > left_max and rsi_series[i] > right_max:
                index_of_highs.append(i)

            left_min = min(rsi_series[i - inspect_left:i])
            right_min = min(rsi_series[i + 1: inspect_right + i + 1])
            if rsi_series[i] < left_min and rsi_series[i] < right_min:
                index_of_lows.append(i)

        # Bullish
        for l in range(len(index_of_lows) - 1):
            left = index_of_lows[l]
            right = index_of_lows[l + 1]
            if right - left <= lookback_range:
                if rsi_series[left] < rsi_series[right] and \
                        self.lows[left + period] > self.lows[right + period]:
                    divergence[right] = 1

                    if verbose is True:
                        print("\nBull Divergence")
                        print(self.date[period + left], self.date[period + right])
                        print(left, right)
                        print(rsi_series[left], rsi_series[right], self.lows[left + period], self.lows[right + period])

                elif rsi_series[left] > rsi_series[right] and \
                        self.lows[left + period] < self.lows[right + period]:
                    hidden_divergence[right] = 1

                    if verbose is True:
                        print("\nBull Hidden Divergence")
                        print(self.date[period + left], self.date[period + right])
                        print(left, right)
                        print(rsi_series[left], rsi_series[right], self.lows[left + period], self.lows[right + period])

        # Bearish
        for h in range(len(index_of_highs) - 1):
            left = index_of_highs[h]
            right = index_of_highs[h + 1]
            if right - left <= lookback_range:
                if rsi_series[left] > rsi_series[right] and \
                        self.highs[left + period] < self.highs[right + period]:
                    divergence[right] = -1

                    if verbose is True:
                        print("\nBear Divergence")
                        print(self.date[period + left], self.date[period + right])
                        print(left, right)
                        print(rsi_series[left], rsi_series[right], self.highs[left + period],
                              self.highs[right + period])

                elif rsi_series[left] < rsi_series[right] and \
                        self.highs[left + period] > self.highs[right + period]:
                    hidden_divergence[right] = -1

                    if verbose is True:
                        print("\nBear Hidden Divergence")
                        print(self.date[period + left], self.date[period + right])
                        print(left, right)
                        print(rsi_series[left], rsi_series[right], self.highs[left + period],
                              self.highs[right + period])

        d = [divergence[index] if index in divergence else 0 for index in range(len(rsi_series))]
        hd = [hidden_divergence[index] if index in hidden_divergence else 0 for index in range(len(rsi_series))]
        return {"divergence": np.array(d), "hidden_divergence": np.array(hd)}


    def SR_Levels(self, left=15, right=15):
        resistence = []
        current_resistence = 0
        for i in range(left, len(self.highs) - right):
            left_max = max(self.highs[i - left: i])
            right_max = max(self.highs[i + 1 : i + right + 1])
            if self.highs[i] > left_max and self.highs[i] > right_max:
                current_resistence = self.highs[i]
            resistence.append(current_resistence)

        support = []
        current_support = 0
        for i in range(left, len(self.lows) - right):
            left_min = min(self.lows[i - left: i])
            right_min = min(self.lows[i + 1 : i + right + 1])
            if self.lows[i] < left_min and self.lows[i] < right_min:
                current_support = self.lows[i]
            support.append(current_support)
        return {"support":support, "resistence":resistence}


    def MACD(self, short_length=12, long_length=26, signal_length=9):
        fast_ema = self.EMA(self.closes, short_length)[long_length - short_length:]
        slow_ema = self.EMA(self.closes, long_length)
        ma_cd_series = fast_ema - slow_ema
        signal_line = self.EMA(ma_cd_series, signal_length)
        output = ma_cd_series[signal_length - 1:] - signal_line
        return {"histogram":output, "macd": ma_cd_series[signal_length - 1:], "signal": signal_line}


    def BOLL(self, period=20, std=2):
        price = self.closes

        middle_band = self.SMA(self.closes, period)

        standard_deviation = []
        for k in range(period, len(price)):
            left = k - period + 1
            right = k + 1
            subset = price[left:right]
            subset_avg = sum(subset) / period
            summation = 0
            for l in range(len(subset)):
                summation += (subset[l] - subset_avg) ** 2
            deviation = (summation / period) ** .5
            standard_deviation.append(deviation)

        upper_band = []
        lower_band = []
        for m in range(len(standard_deviation)):
            upper = middle_band[m] + standard_deviation[m] * std
            upper_band.append(upper)
            lower = middle_band[m] - standard_deviation[m] * std
            lower_band.append(lower)
        return {"lower band": np.array(lower_band), "middle band": np.array(middle_band), "upper band": np.array(upper_band)}


    def ACCUMULATION_DISTRIBUTION(self):
        A_D = []
        MFV = 0
        for i in range(len(self.closes)):
            money_flow = ((self.closes[i] - self.lows[i]) - (self.highs[i] - self.closes[i])) / (
                    self.highs[i] - self.lows[i])
            money_flow *= self.volumes[i]
            if np.isnan(money_flow):
                money_flow = 0.0
            MFV += money_flow
            A_D.append(MFV)
        return np.array(A_D)


    def VOLUME_OSC(self, short_length=5, long_length=10):
        fast_ema = self.EMA(self.volumes, period=short_length)[long_length - short_length:]
        slow_ema = self.EMA(self.volumes, period=long_length)
        vol_osc = 100 * (fast_ema - slow_ema) / slow_ema
        return vol_osc
    

    def FAIR_VALUE_GAP(self):
        recent = []
        value_gap = []
        for i in range(1, len(self.closes) - 1):
            if self.closes[i] - self.opens[i] > 0 and (self.highs[i-1] < self.lows[i+1]) and ((self.lows[i+1] - self.highs[i-1]) / self.lows[i+1]) > 0.00:
                mark = f"Positive {self.lows[i+1]} {self.highs[i-1]} {i+1}"
                value_gap.append(mark)

            elif self.closes[i] - self.opens[i] < 0 and (self.lows[i-1] > self.highs[i+1]) and ((self.lows[i-1] - self.highs[i+1]) / self.highs[i+1]) > 0.00:
                mark = f"Negative {self.lows[i-1]} {self.highs[i+1]} {i+1}"
                value_gap.append(mark)

        bars_since = -1 
        for j in range(len(self.closes)):
            temp = []
            for k in range(len(value_gap)):
                sign, top, bottom, position = value_gap[k].split(" ")
                if sign == "Positive" and self.lows[j] <= float(top) and j > int(position):
                    recent.append(value_gap[k])
                    bars_since = -1
                    continue
                elif sign == "Negative" and self.highs[j] >= float(bottom) and j > int(position):
                    recent.append(value_gap[k])
                    bars_since = -1
                    continue
                else:
                    temp.append(value_gap[k])
            value_gap = temp
            bars_since += 1

        return {"fair value gap": value_gap, "last mitigated": [recent[-1], bars_since]}


