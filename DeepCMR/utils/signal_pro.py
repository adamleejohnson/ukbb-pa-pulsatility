# Adam L. Johnson, M.D. (aljohnson@mgh.harvard.edu)
# Cardiovascular Research Center, Division of Cardiology
# Massachusetts General Hospital

from os import remove
import numpy as np
import pandas as pd
from pandas.core.indexes import numeric


def hampel_filter(input_series: np.ndarray, window_size: int, n_sigmas=3):
    """
    Apply a Hampel filter to array data.

    Parameters
    ----------
    input_series : np.ndarray
        Input array-like data
    window_size : int
        Window size
    n_sigmas : int, optional
        Multiple of sigma for cutoff, by default 3

    Returns
    -------
    [type]
        [description]
    """

    # scale factor for Gaussian distribution
    k = 1.4826

    input_series = pd.Series(input_series)
    new_series = input_series.copy().to_numpy()

    # helper lambda function
    def REMOVE_CENTER(x): return np.delete(np.array(x), int(np.floor((len(x) - 1)/2)))

    def MEDIAN_NO_CENTER(x): return np.median(REMOVE_CENTER(x))

    def MAD_NO_CENTER(x):
        x = REMOVE_CENTER(x)
        return np.median(np.abs(x - np.median(x)))

    rolling_median = input_series.rolling(window=2*window_size, center=True).apply(MEDIAN_NO_CENTER)
    rolling_mad = k * input_series.rolling(window=2*window_size+1, center=True).apply(MAD_NO_CENTER)

    diff = np.abs(input_series - rolling_median)
    threshold = n_sigmas * rolling_mad

    indices = list(np.argwhere(np.array(diff > threshold)).flatten())
    new_series[indices] = rolling_median[indices]

    return new_series, indices, rolling_median, threshold


def hampel_filter_wraparound(input_series: np.ndarray, window_size: int, n_sigmas=3):

    # pad the input series on the left and right with a copy
    sz = np.array(input_series).size
    wa_array = np.tile(input_series, 3)

    wa_result, wa_indices, wa_median, wa_thresh = hampel_filter(
        wa_array, window_size=window_size, n_sigmas=n_sigmas)

    # trim the result
    wa_result_trim = wa_result[sz:2*sz]
    wa_indices_trim = [i - sz for i in wa_indices if i >= sz and i < 2*sz]
    wa_median_trim = wa_median[sz:2*sz]
    wa_thresh_trim = wa_thresh[sz:2*sz]

    return wa_result_trim, wa_indices_trim, wa_median_trim, wa_thresh_trim


def hampel_filter_wraparound_for(input_series: np.ndarray, window_size: int, n_sigmas=3, min_value=-np.Inf):

    k = 1.4826
    def nanmad(x): return np.nanmedian(np.abs(x - np.nanmedian(x)))

    input_series = np.array(input_series)
    sz = input_series.size
    output_series = input_series.copy()
    output_series[output_series <= min_value] = np.nan
    ind = []
    medians = np.empty(sz)
    threshs = np.empty(sz)

    for i in range(0, sz):
        output_series = np.tile(output_series, 3)  # wraparound
        win = output_series.copy()[sz + i - window_size: sz + i + window_size + 1]  # create a window
        win[window_size] = np.nan  # ignore the center value in the window
        output_series = output_series[sz:2*sz]  # undo wraparound
        medians[i] = np.nanmedian(win)  # calculate median
        threshs[i] = n_sigmas * k * nanmad(win)  # calculate threshold

        if np.abs(output_series[i] - medians[i]) > threshs[i] or np.isnan(output_series[i]):
            ind += [i]
            output_series[i] = medians[i]

    return output_series, ind, np.array(medians), np.array(threshs)


def hampel_filter_wraparound_for_recursive(input_series: np.ndarray, window_size: int, n_sigmas=3, min_value=-np.Inf):

    num_replacements = 1
    series = input_series
    ind = []
    upper_max = np.repeat(-np.Inf, len(series))
    lower_min = np.repeat(np.Inf, len(series))

    while (num_replacements > 0):
        series, r_ind, m, t = hampel_filter_wraparound_for(
            series, window_size=window_size, n_sigmas=n_sigmas, min_value=min_value)
        num_replacements = len(r_ind)

        ind.extend(r_ind)
        upper_max = np.maximum(upper_max, m + t)
        lower_min = np.minimum(lower_min, m - t)

    ind = np.unique(ind)
    computed_median = 0.5*(upper_max + lower_min)
    computed_thresh = 0.5*(upper_max - lower_min)

    return series, ind, computed_median, computed_thresh


df = np.array([1, 2, 3, 4, 5, 6, 7, 8, 1, 1000, 99, 1, 100, 6, 7, 8])
areas = [1.3096262857025434, 1.3707807088558739, 1.4752934075913606, 1.541738506999513, 1.6107313784864647, 1.6626911174171761, 1.6690002866104405, 0.7744833542858461, -np.Inf, -np.Inf, -np.Inf, -np.Inf, -np.Inf, -np.Inf, -np.Inf, -np.Inf, -np.Inf, 1.6563418897385174, 1.6690002866104405, 1.637048686803838, 1.6435212013094558, 1.5629407146501164, 1.5053708628286384, 1.4363779913416872, 1.48289800697658, 1.4521263483098263, 1.4442831708488004,
         0.6254477751253582, 1.5345700175209007, 1.5768298268107837, 1.5559231419914699, 1.5273497695474136, 1.5345700175209007, 1.4904452126119627, 1.4442831708488004, 1.4676305348457914, 1.4442831708488004, 1.3707807088558739, 1.3450282127534592, 1.3362945327847047, 1.3362945327847047, 1.3185949556853036, 1.2635351785022761, 1.2635351785022761, 1.2540564345477325, 1.2540564345477325, 1.2822273115144287, 1.2822273115144287, 1.3096262857025434, 1.3096262857025434]
hampel_filter_wraparound_for(areas, 3, 3)
