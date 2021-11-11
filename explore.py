# %%
"""A work in progress."""
from IPython.display import display
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from datetime import datetime
import warnings
from typing import Dict, List, Tuple

warnings.filterwarnings('ignore')
sns.set_style('darkgrid')

# LOAD SCRAPED DATASETS
# ============================ #
SCRAPES_PATH = 'data/scrapes/'
rarran = pd.read_json(SCRAPES_PATH + 'rarran.json')
regis = pd.read_json(SCRAPES_PATH + 'regis.json')

CHANNEL_DICT = {
    'rarran': rarran,
    'regis': regis
}

# FUNCTION DEFINITIONS
# ============================ #


def to_datetime(data: pd.DataFrame, colname: str) -> pd.DataFrame:
    """Transform a dataframe column from str to datetime."""
    data[colname + "_dt"] = data[colname].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%d'))
    data[colname + "_dt"] = pd.to_datetime(data[colname + "_dt"])

    return data


def create_time_components(df: pd.DataFrame, colname: str) -> pd.DataFrame:
    """Breaks down datetime column into several modular time components."""
    ser_count = df[colname].value_counts()
    ser_count = ser_count.sort_index(ascending=True)

    df_count = ser_count.to_frame()
    df_count.index = pd.to_datetime(df_count.index)
    df_count = df_count.sort_index(ascending=True)

    df_count['year'] = df_count.index.year
    df_count['month'] = df_count.index.month
    df_count['day_of_week'] = df_count.index.weekday
    df_count['week_number'] = df_count.index.week
    df_count['quarter'] = df_count.index.quarter
    df_count['day_of_month'] = df_count.index.day

    return df_count


def try_convert_date(obj: datetime) -> datetime.date:
    """Convert datetime object to date."""
    try:
        return obj.date()
    except AttributeError:
        return obj


def create_monthly_ts(df: pd.DataFrame, colname: str) -> pd.DataFrame:
    """Turn a daily time series into a monthly aggregate."""
    monthly = df.groupby(['year', 'month']).agg(
        {
            colname: 'sum'
        })

    return monthly


def flatten_multi_level_index(df: pd.DataFrame) -> List:
    """Take a multi level index and flatten it."""
    out_index = []
    for i in df.index:
        out_index.append(str(i[1])+'-'+str(i[0]))

    return out_index


def get_channel_name(data: pd.DataFrame, channel: str) -> pd.DataFrame:
    """Populate column with a string representing the channel's name."""
    data['channel'] = channel

    return data


def sec_to_min(data: pd.DataFrame) -> pd.DataFrame:
    """Turns a column with values in seconds, to minutes."""
    data['duration_m'] = data.duration.apply(lambda x: round(x / 60, 2))

    return data


def remove_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Remove very specific columns."""
    data = data.drop(
        [
            'upload_date',
            'channel_id',
            'duration',
            'scrape_date',
            'upload_date'
        ],
        axis=1)

    return data


def rename_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Rename very specific columns."""
    data = data.rename(
        {
            'upload_date_dt': 'upload_date',
            'duration_m': 'duration'
        },
        axis=1)

    return data


def float_to_int(data: pd.DataFrame) -> pd.DataFrame:
    """Turn specific columns from float to integers."""
    data['duration'] = data['duration'].astype(int)
    data['dislikes'] = data['dislikes'].astype(int)

    return data


def basic_wrangling(data: pd.DataFrame) -> pd.DataFrame:
    """Perform specific basic data wrangling on a dataframe."""
    data = sec_to_min(data)
    data = to_datetime(data, 'upload_date')
    data = remove_columns(data)
    data = rename_columns(data)
    data = float_to_int(data)

    return data


def plot_line(
    df: pd.DataFrame,
    channel_name: str,
    y_label: str,
    x_label='index',
    close_plot=True,
    marker=False
):
    """Draw a Seaborn line plot with specific settings."""
    rcParams['figure.figsize'] = 24, 12
    sns.set(style='darkgrid')

    if x_label == 'index':
        if marker is True:
            ax = sns.lineplot(
                data=df,
                y=df[y_label],
                x=df.index,
                marker='o',
                label=f'Date of {y_label}'
            )
        else:
            ax = sns.lineplot(
                data=df,
                y=df[y_label],
                x=df.index,
                label=f'Date of {y_label}'
            )
    else:
        if marker is True:
            ax = sns.lineplot(
                data=df,
                y=df[y_label],
                x=df[x_label],
                marker='o',
                label=f'Date of {y_label}'
            )
        else:
            ax = sns.lineplot(
                data=df,
                y=df[y_label],
                x=df[x_label],
                label=f'Date of {y_label}'
            )

    ax.set_title(f'{channel_name} Line Plot: {y_label}', fontsize=24)
    ax.set_xlabel('Date')
    ax.set_ylabel('Count')
    plt.xticks(rotation=90)
    plt.show()
    if close_plot:
        plt.clf()


def wrangle_all(channels: Dict) -> List:
    """Performs wrangling on a set of channels' data."""
    out = []
    for channel, data in channels.items():
        data = get_channel_name(data, channel)
        data = basic_wrangling(data)
        out.append(data)

    return out


def meta_function_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Perform several specific feature engineering tasks."""
    df['reactions'] = df['likes'] + df['dislikes']
    df['views_likes_ratio'] = df['likes'] / df['views']
    df['views_dislikes_ratio'] = df['dislikes'] / df['views']
    df['views_reactions_ratio'] = df['reactions'] / df['views']
    df['reactions_likes_ratio'] = df['likes'] / df['reactions']
    df['reactions_dislikes_ratio'] = 1 - df['reactions_likes_ratio']
    df['reactions_likes_ratio'] = df['likes'] / df['dislikes']
    df['likes_per_minute'] = df['duration'] / df["reactions"]
    df['viewtime'] = df['views'] * df["duration"]

    return df


def basic_eda(data, notebook_friendly=True) -> None:
    """Perform basic exploratory data analysis."""
    # Define separators for easy pretty text printing.
    sep1 = '\n============================='
    sep2 = '\n=============================\n'

    print(
        f"{sep1}{sep2} EDA of {data['channel'][0]}'s channel:{sep1}{sep2}")

    # If we are using an iPython kernel
    # use display instead of just printing.
    if notebook_friendly:
        print(data.shape)
        print()
        display(data.head())
        print()
        print(data.columns)
        print()
        display(data.describe())
        print()
        display(data.isna().sum())
        print()
        display(data.dtypes)
        print()
    else:
        print(data.shape)
        print()
        print(data.head())
        print()
        print(data.columns)
        print()
        print(data.describe())
        print()
        print(data.isna().sum())
        print()
        print(data.dtypes)
        print()


def eda_all(data_list: List) -> None:
    """Perform the eda for a list of dataframes."""
    # Probably exaggerated with this wrapper.
    for data in data_list:
        basic_eda(data)


def remove_outliers_iqr(data: pd.DataFrame, colname: str) -> pd.DataFrame:
    """Remove rows of outliers in a column beyond the interquartilic range."""
    y = data[colname]
    Q1 = data[colname].quantile(0.25)
    Q3 = data[colname].quantile(0.75)
    IQR = Q3 - Q1
    low_lim = Q1 - 1.5 * IQR
    high_lim = Q3 + 1.5 * IQR
    print(type(IQR))
    removed_outliers = y.between(low_lim, high_lim)
    # INVERT removed_outliers!!
    index_names = data[~removed_outliers].index
    data = data.drop(index_names)

    return data


def meta_function_eda_plotting(df: pd.DataFrame) -> None:
    """Perform EDA, remove outliers and plot histograms."""
    basic_eda(df)

    df = remove_outliers_iqr(df, 'duration')
    sns.histplot(data=df, x="duration", kde=True)
    plt.title("Histogram of Duration")
    plt.show()
    plt.clf()

    df = remove_outliers_iqr(df, 'views')
    sns.histplot(data=df, x="views", kde=True)
    plt.title("Histogram of Views")
    plt.show()
    plt.clf()

    df = remove_outliers_iqr(df, 'likes')
    sns.histplot(data=df, x="likes", kde=True)
    plt.title("Histogram of Likes")
    plt.show()
    plt.clf()

    df = remove_outliers_iqr(df, 'dislikes')
    sns.histplot(data=df, x="dislikes", kde=True)
    plt.title("Histogram of Dislikes")
    plt.show()
    plt.clf()


def calculate_channel_age(df: pd.DataFrame) -> int:
    """Calculate a channel's age in days."""
    min = df['upload_date'].min()
    max = df['upload_date'].max()
    age = max-min
    age = age.days

    return age


def calculate_totals(df: pd.DataFrame) -> Dict:
    """Calculate some summed metrics for several features."""
    channel_age = calculate_channel_age(df)
    total_videos = df.shape[0]
    total_views = sum(df['views'])
    total_reactions = sum(df['reactions'])
    total_likes = sum(df['likes'])
    total_dislikes = sum(df['dislikes'])
    total_duration = sum(df['duration'])
    total_viewtime_days = int((sum(df['viewtime']) / 60) / 24)
    total_viewtime_years = int(total_viewtime_days / 365)
    total_like_dislike_ratio = int(total_likes / total_dislikes)

    TOTALS_DICT = {
        'channel_age': channel_age,
        'total_videos': total_videos,
        'total_views': total_views,
        'total_duration': total_duration,
        'total_viewtime_days': total_viewtime_days,
        'total_viewtime_years': total_viewtime_years,
        'total_reactions': total_reactions,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
        'total_like_dislike_ratio': total_like_dislike_ratio
    }

    return TOTALS_DICT


def calculate_averages(df: pd.DataFrame, totals_dict: Dict) -> Dict:
    """Calculate some averaged metrics for several features."""
    average_videos_per_day = totals_dict['total_videos'] / \
        totals_dict['channel_age']
    average_videos_per_week = totals_dict['total_videos'] / \
        (totals_dict['channel_age'] / 7)
    average_duration = df['duration'].mean()
    average_views_per_video = df['views'].mean()
    average_like_per_video = df['likes'].mean()
    average_dislike_per_video = df['dislikes'].mean()
    average_reactions_per_video = df['reactions'].mean()

    AVERAGES_DICT = {
        'average_videos_per_day': int(average_videos_per_day),
        'average_videos_per_week': int(average_videos_per_week),
        'average_duration': int(average_duration),
        'average_views_per_video': int(average_views_per_video),
        'average_like_per_video': int(average_like_per_video),
        'average_dislike_per_video': int(average_dislike_per_video),
        'average_reactions_per_video': int(average_reactions_per_video)
    }

    return AVERAGES_DICT


def meta_function_calculate_statistics(df: pd.DataFrame) -> Dict:
    """Calculates summed and averaged statistics for a dataframe."""
    totals_dict = calculate_totals(df)
    averages_dict = calculate_averages(df, totals_dict)
    statistics = dict(totals_dict, **averages_dict)

    return statistics


def prepare_ts_data(df: pd.DataFrame) -> Tuple:
    """Prepares a dataframe for monthly time series analysis."""
    df = create_time_components(df, 'upload_date')
    mon = create_monthly_ts(df, 'upload_date')
    idx = flatten_multi_level_index(mon)
    mon['idx'] = idx

    return df, mon


def to_datetime_hs(data: pd.DataFrame, colname: str) -> pd.DataFrame:
    """Prepares a dataframe for monthly time series analysis."""
    data[colname + "_dt"] = data[colname].apply(
        lambda x: datetime.strptime(x, '%B %d, %Y'))
    data[colname + "_dt"] = pd.to_datetime(data[colname + "_dt"])

    return data


def plot_vertical_lines(
    xcoords: List,
    names: List,
    dates: List,
    colors: List
) -> plt:
    """Plots vertical lines at coordinates on the x axis."""
    for i in range(0, len(xcoords)):
        for j in range(0, len(xcoords[i])):
            plt.axvline(
                x=xcoords[i][j],
                label=f'{names[i][j]} :  {dates[i][j]}',
                color=colors[i],
                linewidth=2,
                linestyle=':'
                )
    plt.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.3),
        ncol=3,
        fancybox=True,
        shadow=True
        )
    plt.show()
    plt.clf()


# %%
# Testing functions
# ============================#
data_list = wrangle_all(CHANNEL_DICT)

rarran, regis = data_list[0], data_list[1]
channel_list = rarran, regis

for channel in channel_list:
    meta_function_feature_engineering(channel)

for channel in channel_list:
    meta_function_eda_plotting(channel)

rarran_stats = meta_function_calculate_statistics(rarran)
regis_stats = meta_function_calculate_statistics(regis)
print(rarran_stats)
print()
print(regis_stats)

# %%
# (WIP) Time series analysis
# ============================#
regis, regis_mon = prepare_ts_data(regis)
rarran, rarran_mon = prepare_ts_data(rarran)

plot_line(
    df=regis_mon,
    channel_name='Regis',
    y_label='upload_date',
    x_label='idx',
    marker=True
)

plot_line(
    df=rarran_mon,
    channel_name='Rarran',
    y_label='upload_date',
    x_label='idx',
    marker=True
)

# Data on Hearthstone key moments in history
hs = pd.read_csv(
    'data/external/hearthstone_content_dates.csv',
    encoding='utf-8',
    sep=';'
    )

# A small mistake on my side when
# I saved this ^^
hs = hs.drop(columns=[
    'Unnamed: 5', 'Unnamed: 6',
    'Unnamed: 7', 'Unnamed: 8'
])

hs = to_datetime_hs(hs, 'release_date')

cols_to_drop = [
    'release_date',
    'removal_date',
    'year'
]

hs = hs.drop(columns=cols_to_drop)
hs = hs.rename({'release_date_dt': 'release_date'}, axis=1)

# Slice dataframe into different sets to explore
core = hs[hs.release_type == 'Core']
adventure = hs[hs.release_type == 'Adventure']
expansion = hs[hs.release_type == 'Expansion']
miniset = hs[hs.release_type == 'Miniset']

# x coordinates for the lines
x_core = np.array(core.release_date)
x_adventure = np.array(adventure.release_date)
x_expansion = np.array(expansion.release_date)
x_miniset = np.array(miniset.release_date)

name_core = np.array(core.set_name)
name_adventure = np.array(adventure.set_name)
name_expansion = np.array(expansion.set_name)
name_miniset = np.array(miniset.set_name)

date_core = np.array(core.release_date)
date_adventure = np.array(adventure.release_date)
date_expansion = np.array(expansion.release_date)
date_miniset = np.array(miniset.release_date)

xcoords = [x_core, x_adventure, x_expansion, x_miniset]
names = [name_core, name_adventure, name_expansion, name_miniset]
dates = [date_core, date_adventure, date_expansion, date_miniset]
colors = ['darkgreen', 'red', 'blue', 'gold']

# %%
