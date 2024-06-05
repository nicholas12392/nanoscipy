import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pyperclip


def __mplRemSpine__():
    """
    Removes all spines from mpl figures.
    :return:
    """
    mpl.rcParams['axes.spines.left'] = False
    mpl.rcParams['axes.spines.bottom'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False


def __mplRepSpine__():
    """
    Resets all spines from mpl figures.
    :return:
    """
    mpl.rcParams['axes.spines.left'] = True
    mpl.rcParams['axes.spines.bottom'] = True
    mpl.rcParams['axes.spines.right'] = True
    mpl.rcParams['axes.spines.top'] = True


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
    r_channel = osc_line(n, tt=tt[0], lin=lin[0], gauge=gauge[0], freq=freq[0], min_shift=boldness)
    g_channel = osc_line(n, tt=tt[1], lin=lin[1], gauge=gauge[1], freq=freq[1], min_shift=boldness)
    b_channel = osc_line(n, tt=tt[2], lin=lin[2], gauge=gauge[2], freq=freq[2], min_shift=boldness)

    output_dict = {'tt': tt, 'lin': lin, 'gauge': gauge, 'freq': freq, 'boldness': boldness}

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
    preset_dict = {'pastel_forest': color_generator(n, tt=('cos', 'sin', 'cos'), lin=(0.8424486727909565, 0.5965113120235963, 0.4659955642361818), gauge=(0.882211564812874, 0.9253309416385721, 0.3036444769691671), freq=(5.750995730778884, 6.626577331779604, 6.203001591343849), boldness=0.1),
                   'fall': color_generator(n, tt=('sin', 'sin', 'sin'), lin=(0.18459375683008084, 0.3644435376188807, 0.3151963613200892), gauge=(0.4233901826104187, 0.7780608048565588, 0.6501426980934245), freq=(7.694825738418649, 6.792908639099856, 2.1887401834339792), boldness=0.1),
                   'mycelium': color_generator(n, tt=('cos', 'sin', 'cos'), lin=(0.6965489283947568, 0.5379827559622246, 0.590836450237111), gauge=(0.7918072802783239, 0.17971631299104796, 0.8966163328893566), freq=(4.269129623605497, 9.545287354973631, 8.794565626097985), boldness=0.1),
                   'warm_beach': color_generator(n, tt=('cos', 'cos', 'sin'), lin=(0.012806280424325744, 0.3466180632687774, 0.6212518740059257), gauge=(0.8007970933068582, 0.4249831969103427, 0.04851597767602456), freq=(0.6277798254706779, 9.960295720197983, 3.544131421584238), boldness=0.1),
                   'painters_brush': color_generator(n, tt=('sin', 'sin', 'sin'), lin=(0.308444204233711, 0.1686395008677387, 0.5045269085103439), gauge=(0.7832268449526734, 0.15321523671430537, 0.6997354945173151), freq=(3.601922407161031, 4.235517807890995, 2.633870423116117), boldness=0.1),
                   'pink_blaze': color_generator(n, tt=('sin', 'sin', 'cos'), lin=(0.06348407962139713, 0.4207833694511711, 0.6015882017152983), gauge=(0.2700065340016534, 0.5042995435308218, 0.19213248003391548), freq=(4.707628225803258, 5.639046078387889, 1.805579633573785), boldness=0.0779072482266158),
                   'dark_pastel': color_generator(n, tt=('sin', 'sin', 'cos'), lin=(0.7018153726790896, 0.96008686470481, 0.5864881417088937), gauge=(0.5516719671793261, 0.7721820322562742, 0.7193955254736332), freq=(6.474776313288961, 1.1558432381353423, 6.251098583075184), boldness=0.13352839290158403),
                   'vintage': color_generator(n, tt=('cos', 'cos', 'cos'), lin=(0.8035508585339293, 0.5873955975579723, 0.7482733479968617), gauge=(0.8015566008393893, 0.5400803448283856, 0.6335742811492808), freq=(7.3632055787553865, 7.145036435926109, 4.438139747879446), boldness=0.2606686299418291),
                   'hot_water': color_generator(n, tt=('cos', 'sin', 'cos'), lin=(0.44023339086436697, 0.6826077476622177, 0.8151964340431196), gauge=(0.964310085921032, 0.03363390164302549, 0.05820185742552919), freq=(1.6869935359246035, 6.4898918399576635, 2.528053789285085), boldness=0.24499811682720143),
                   'police': color_generator(n, tt=('sin', 'cos', 'cos'), lin=(0.9794863485076006, 0.8193879961586231, 0.20015141136867098), gauge=(0.5504134382860503, 0.8350677728447133, 0.6183616272835573), freq=(0.7621938947739482, 1.4957892796174477, 1.3912969250620155), boldness=0.3074139743447318),
                   'pink_grape': color_generator(n, tt=('sin', 'cos', 'sin'), lin=(0.3202119000366527, 0.7400821821381202, 0.8332050160269396), gauge=(0.15021149717292037, 0.7854109324016265, 0.1579630349476494), freq=(0.06283516041174497, 2.1424367216186813, 5.921271603253864), boldness=0.384526363229755),
                   'fantasy_forest': color_generator(n, tt=('cos', 'sin', 'cos'), lin=(0.49522418361049325, 0.635784505879416, 0.34797711586511326), gauge=(0.7530206294253756, 0.21782154169020151, 0.545906936800918), freq=(4.0281981178039725, 4.654727646396184, 0.713978250187276), boldness=0.30926659994739913),
                   'burning_water': color_generator(n, tt=('sin', 'sin', 'sin'), lin=(0.08953571190149634, 0.3323885738839526, 0.862954174596466), gauge=(0.6754565955895888, 0.20136545824984842, 0.022987750413096752), freq=(1.9259167144725398, 1.4620085342383549, 5.062564558031064), boldness=0.015093079918601449),
                   'blue_theater': color_generator(n, tt=('cos', 'sin', 'sin'), lin=(0.7464340752598755, 0.6457268765669827, 0.026847944615820074), gauge=(0.4468275348401235, 0.3015608962219799, 0.1682188935849046), freq=(2.26502767141025, 0.6733549105511583, 0.5957448535619292), boldness=0.35906288957994326),
                   'goth': color_generator(n, tt=('sin', 'cos', 'cos'), lin=(0.9206341186119508, 0.6213095212095684, 0.26573096699929977), gauge=(0.5115897830301739, 0.04975872892656552, 0.008563454145327887), freq=(0.7357750762442106, 1.3523458181514203, 9.91834949122228), boldness=0.07168752127718263),
                   'light_viridis' : color_generator(n, tt=('cos', 'sin', 'sin'), lin=(0.51048783, 0.60206757, 0.02177498), gauge=(0.75502318, 0.53687847, 0.62156673), freq=(1.6531279 , 0.41777519, 1.88061117), boldness=0.293572114072021),
                   'minecraft_plateu' : color_generator(n, tt=('sin', 'sin', 'cos'), gauge=(0.3482193222319738, 0.7807282960145357, 0.8659499190812215), freq=(3.4114823924121787, 3.3979283028298846, 2.9507456014157696), boldness=0.10886965582355904),
                   'miami_beach' : color_generator(n, tt=('sin', 'cos', 'cos'), gauge=(0.9213698992001396, 0.11599579595640752, 0.8024428061750865), freq=(3.791223318556148, 3.9425382019437736, 1.930325349188513), boldness=0.24084336244319482),
                   'pastel_noir' : color_generator(n, tt=('sin', 'cos', 'cos'), gauge=(0.10276984448452353, 0.01912191661348417, 0.08762323110502379), freq=(2.6192098272468067, 6.442753666188262, 1.6434438167539223), boldness=0.32464771148566574),
                   'deep_ocean' : color_generator(n, tt=('cos', 'cos', 'cos'), gauge=(0.2746121412897611, 0.03496786047575706, 0.9951985012809467), freq=(1.3816533198839587, 6.692048750846249, 0.11822168881117201), boldness=0.03369004588471469),
                   'city_beach' : color_generator(n, tt=('sin', 'sin', 'cos'), gauge=(0.8918550366801142, 0.41580951801223676, 0.29248583155548946), freq=(1.0402099443232449, 0.2246159414508775, 2.559138470734512), boldness=0.2708554937457763),
                   'violet_noir' : color_generator(n, tt=('cos', 'sin', 'cos'), gauge=(0.07322078748825278, 0.8405562840884604, 0.01909145530320555), freq=(1.8689628615956388, 0.0643192709196172, 0.480615609629802), boldness=0.14875334070866622),
                   'pastel_forest' : color_generator(n, tt=('cos', 'sin', 'cos'), gauge=(0.1954425231716893, 0.8676882943755347, 0.4906173235768789), freq=(2.7534537333276403, 0.4198966507569548, 0.7448260209469884), boldness=0.05471211374810168),
                   'basic_crayons' : color_generator(n, tt=('cos', 'sin', 'cos'), gauge=(0.42115607489354057, 0.7368289142627524, 0.7058170922090591), freq=(2.5971501887546276, 2.4802281642151813, 1.1770163494297763), boldness=0.042744553287281675),
                   'violet_pastels' : color_generator(n, tt=('sin', 'cos', 'sin'), gauge=(0.8794436602862163, 0.08333404920727361, 0.7103508729828856), freq=(0.5827587762866908, 2.8282578156664773, 0.7792788039728), boldness=0.09115863669956206),
                   'beach_noir' : color_generator(n, tt=('cos', 'sin', 'cos'), gauge=(0.7744332343303063, 0.07359103350208862, 0.7657616064796195), freq=(2.2338502240854172, 2.891743120720559, 0.8413652993698586), boldness=0.4777811299932795)
                   }
    if preset == -1:
        colors = list(preset_dict.keys())
        sets = len(colors)
        y_scaler = 1 + sets * 0.5
        x_scaler = 1 + n * 0.34
        block_ys = np.linspace(0, n, n + 1)
        plt.figure(figsize=(1 * x_scaler, 1 * y_scaler), dpi=300)
        for i, k in zip(range(sets), colors):
            for by, c in zip(block_ys, preset_dict[k]):
                plt.plot(by, i, c=c, marker='s', ms=24)
        plt.yticks(ticks=range(len(colors)), labels=colors)
        plt.xticks([])
        plt.xlim(-0.5, n + 0.5)
        plt.ylim(-0.5, sets + 0.5)
        plt.tight_layout()
        __mplRemSpine__()
        plt.show()
        __mplRepSpine__()
    else:
        return preset_dict[preset]


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
        plt.figure(figsize=(1 * x_scaler, 1 * y_scaler), dpi=300)

        color_dict = {}
        for i in range(1, sets + 1):
            color_set, dict_set = color_generator(n, random=True, rf=max_frequency, rb=max_boldness, cdict=True)
            color_dict[i] = dict_set
            for by, c in zip(set_steps, color_set):
                plt.plot(by, i, c=c, marker='s', ms=24)

        self.cdict = color_dict
        plt.yticks(range(1, sets + 1))
        plt.xticks([])
        plt.xlim(-0.5, n + 0.5)
        plt.ylim(-0.5, sets + 0.5)
        # plt.legend(frameon=False)
        plt.tight_layout()
        __mplRemSpine__()
        plt.show()
        __mplRepSpine__()

    def __func_clip__(self, index):
        icd = self.cdict[index]
        tt, gauge, freq, boldness = tuple(icd['tt']), tuple(icd['gauge']), tuple(icd['freq']), icd['boldness']
        copy_string = f'color_generator(n, tt={tt}, gauge={gauge}, freq={freq}, boldness={boldness})'
        pyperclip.copy(copy_string)
        print('Copied color generator preset to clipboard:')
        print(copy_string)

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
