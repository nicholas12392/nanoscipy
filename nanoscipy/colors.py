import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import json


__fd__ = os.path.dirname(__file__)  # get file directory to access preset files


def osc_line(points, tt='sin', lin=1, gauge=0.5, freq=4, min_shift=0.1):
    """
    Creates an oscillator line with given parameters.
    :param points: The amount of points there should be on the line.
    :param tt: The trigonometry type. Can be 'sin' or 'cos'. Default is 'sin'.
    :param lin: The linearity. Default is 1.
    :param gauge: Maximum amplitude span of the oscillator. Default is 0.5.
    :param freq: The frequency of the oscillator. Default is 4.
    :param min_shift: A minimum shift of the oscillator baseline. Default is 0.1.
    :return: A numpy array with the oscillator line points.
    """
    lrange = np.linspace(0, 1, points)  # create the amount of desired points
    y1, y2 = 0, lin
    lr = ((y1 - y2) / -1, 1 - lin)  # find slope
    lin_values = lr[0] * lrange + lr[1]  # define linear values

    # find trigonometric values
    if tt == 'sin':
        trig_values = gauge / 2 * np.sin(lrange * freq * np.pi) + 0.5
    elif tt == 'cos':
        trig_values = gauge / 2 * np.cos(lrange * freq * np.pi) + gauge / 2
    else:
        raise ValueError('tt must be sin/cos')

    # adjust baseline values and return the oscillator line points
    func_max = 1 + max(trig_values)
    func_min = min(lin_values + trig_values)
    return (lin_values + trig_values - func_min + min_shift) / (func_max - func_min + min_shift)


def color_generator(n, tt=('sin', 'sin', 'sin'), lin=(1, 1, 1), gauge=(0.5, 0.5, 0.5), freq=(4, 4, 4), random=False,
                    rf=10, boldness=0.1, rb=0.4, cdict=False):
    """
    Generates an array of colors from an RGB spectrum through the oscillator line function.
    :param n: Number of colors to generate.
    :param tt: The trigonometry type for the R, G, and B channels. Can be 'sin' or 'cos'. Default is ('sin', 'sin', 'sin').
    :param lin: Linearity for the R, G, and B channels. Default is (1, 1, 1).
    :param gauge: Maximum amplitude span of the oscillator for the R, G, and B channels. Default is (0.5, 0.5, 0.5).
    :param freq: Frequency of the oscillator for the R, G, and B channels. Default is (4, 4, 4).
    :param random: If True the color spectra are generated randomly. Default is False.
    :param rf: Upper frequency limit for the R, G, and B channels. Default is 10.
    :param boldness: Introduces a minimim baseline for the R, G, and B channels. A higher value streamlines the color
    spectrum, such that a more easily pleasing spectrum is obtained. A lower value makes the colors in the spectrum
    more easily distinguishable. Default is 0.1.
    :param rb: The boldness limit for the R, G, and B channels. Default is 0.4.
    :param cdict: If True a dictionary with the function parameters is generated in addition to the colors from the
    generated spectrum. Default is False.
    :return: A numpy array with the color spectrum points in the form ((R,G,B), ...). If cdict is True a the output
    will instead be ((R,G,B), ...), dict.
    """
    if random:
        rm = np.random.rand(4, 3)

        def sin_cos(value):
            if value > 0.5:
                return 'sin'
            else:
                return 'cos'

        tt, lin, gauge, freq = [sin_cos(i) for i in rm[0]], rm[1], rm[2], rm[3] * rf
        boldness = np.random.rand(1)[0] * rb

        if not cdict:
            print('Generating colors with random (r, g, b) values:\n'
                  f'Trigonometry: ({tt[0]}, {tt[1]}, {tt[2]})\n'
                  f'Linearity: ({lin[0]}, {lin[1]}, {lin[2]})\n'
                  f'Gauge: ({gauge[0]}, {gauge[1]}, {gauge[2]})\n'
                  f'Frequency: ({freq[0]}, {freq[1]}, {freq[2]})\n',
                  f'Boldness: {boldness}\n')
        output_dict = {'tt': tt, 'lin': lin.tolist(), 'gauge': gauge.tolist(), 'freq': freq.tolist(),
                       'boldness': boldness}
    else:
        output_dict = {'tt': tt, 'lin': lin, 'gauge': gauge, 'freq': freq, 'boldness': boldness}

    r_channel = osc_line(n, tt=tt[0], lin=lin[0], gauge=gauge[0], freq=freq[0], min_shift=boldness)
    g_channel = osc_line(n, tt=tt[1], lin=lin[1], gauge=gauge[1], freq=freq[1], min_shift=boldness)
    b_channel = osc_line(n, tt=tt[2], lin=lin[2], gauge=gauge[2], freq=freq[2], min_shift=boldness)

    if cdict:
        return tuple(zip(r_channel, g_channel, b_channel)), output_dict
    else:
        return tuple(zip(r_channel, g_channel, b_channel))


def color_presets(n, preset=-1):
    """
    Gives n amount of colors from a chosen color preset.
    :param n: The number of colors to generate.
    :param preset: The preset from which the colors are generated. If preset is -1, a figure with all different presets
    is generated instead. Default is -1.
    :return: A numpy array with the color spectrum points in the form ((R,G,B), ...).
    """

    with open(rf'{__fd__}\__presets__\colors.json', 'r') as f:
        presets = json.load(f)

    if preset == -1:
        colors = list(presets.keys())
        sets = len(colors)

        swatch_width = 300
        spot_width = 300 // n
        spot_height = 20

        plt.figure(dpi=200)
        for i, k in enumerate(colors):
            for s, c in enumerate(color_generator(n, **presets[k])):
                rect = mpl.patches.Rectangle((s * spot_width, i * spot_height), spot_width, spot_height, lw=0, facecolor=c, fill=True)
                plt.gca().add_patch(rect)
                plt.gca().axis('off')
            plt.text(-5, i * spot_height + 5, k, ha='right', fontsize=6)
        plt.yticks([])
        plt.xticks([])
        plt.xlim(-40, swatch_width + 0.5)
        plt.ylim(-0.5, sets * spot_height + 0.5)
        plt.tight_layout()
        plt.show()
    else:
        return color_generator(n, **presets[preset])


class RandomColors:
    """
    A random color preset generator.
    """
    def __init__(self):
        self.cdict = None

    def generate(self, sets=20, n=20, max_frequency=10, max_boldness=0.4):
        """
        Generate random color preset.
        :param sets: The number of presets to generate.
        :param n: The number of colors to generate in each preset.
        :param max_frequency: Upper frequency limit for the R, G, and B channels. Default is 10.
        :param max_boldness: The boldness variation lower limit for the R, G, and B channels. Default is 0.4.
        :return: Creates a figure with the generated colors and defines the color parameter dictionary as self.cdict.
        """
        y_scaler = 1 + sets * 0.5
        x_scaler = 1 + n * 0.34
        set_steps = np.linspace(0, n, n + 1)
        plt.figure(dpi=200)

        swatch_width = 300
        spot_width = 300 // n
        spot_height = 20

        color_dict = {}
        for i in range(sets):
            color_set, dict_set = color_generator(n, random=True, rf=max_frequency, rb=max_boldness, cdict=True)
            color_dict[i] = dict_set
            for s, c in enumerate(color_set):
                rect = mpl.patches.Rectangle((s * spot_width, i * spot_height), spot_width, spot_height, lw=0,
                                             facecolor=c, fill=True)
                plt.gca().add_patch(rect)
                plt.gca().axis('off')
            plt.text(-5, i * spot_height + 5, i, ha='right', fontsize=6)

        self.cdict = color_dict
        plt.yticks([])
        plt.xticks([])
        plt.xlim(-10, swatch_width + 0.5)
        plt.ylim(-0.5, sets * spot_height + 0.5)
        plt.tight_layout()
        plt.show()

    def save(self, indexes, names, overwrite=False):
        """Method that saves one or more generated colors according to the selected indexes and passed names.
        :param indexes: A list of indexes to save. This can be just an int.
        :param names: A list of names to save. This can be just a str.
        :param overwrite: Regular behavior is False, in which case a color cannot be saved if the provided name already
        exists. Setting this to True will permit overwriting of existing colors in the colors.json file."""
        
        with open(rf'{__fd__}\__presets__\colors.json', 'r') as f:  # load current color preset dict
            preset = json.load(f)

        if isinstance(indexes, int) and isinstance(names, str):  # convert single saves to tuples
            indexes = (indexes, )
            names = (names,)

        for i, n in zip(indexes, names):  # save selected colors 
            if n in preset and overwrite is False:
                raise KeyError(f'Preset name {n} already exists. Set overwrite=True to bypass.')
            else:
                preset[n] = self.cdict[i]

        with open(rf'{__fd__}\__presets__\colors.json', 'w') as f:  # write new json file
            f.write(json.dumps(preset, indent=4))
            f.truncate()


def GRAY2RGB(img, rgb_col):
    """
    Converts a grayscale image from OpenCV into an RGB image with the specified RGB color. Effectively, the script
    replaces the grayscale gradient with an RGB gradient.
    :param img: grayscale image from OpenCV
    :param rgb_col: desired RGB color in shape (r, g, b) or hex as '#HEXCODE'
    :return: Recolored image
    """

    # check for hex color
    if isinstance(rgb_col, str):
        if rgb_col[0] == '#':
            rgb_col = rgb_col.lstrip('#')
        rgb_col = tuple(int(rgb_col[i:i + 2], 16) for i in (0, 2, 4))

    # check for grayscale
    if isinstance(img[0][0], np.ndarray):  # if image is in RGB/BGR format convert it
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    rgb_rel = np.array(rgb_col) / 255  # set relative RGB color
    bgr_rel = np.flip(rgb_rel)  # flip to native BGR for opencv

    RGB_INT_map = dict(zip(range(256), [np.uint8(bgr_rel * i) for i in range(256)]))
    RGB_shape = np.array([RGB_INT_map.get(i) for i in range(256)])  # define indexer for matrix transform
    RGB_matrix = RGB_shape[img]  # transform the input matrix with the RGB values

    return RGB_matrix
