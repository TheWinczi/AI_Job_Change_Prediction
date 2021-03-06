import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA, KernelPCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from .utilities import drop_columns


def process_native_data(df: pd.DataFrame):
    """
    Process native data. Process all columns in DataFrame to
    allow machine learning.

    Parameters
    ----------
    df : DataFrame
        DataFrame of all needed data.

    Returns
    -------
    proc_data
        Processed DataFrame with data ready to machine learning.
    """
    processed_df = process_all_labels(df.copy())
    return processed_df


def process_all_labels(df: pd.DataFrame):
    """
    Process all labels (columns values) in DataFrame to allow
    machine learning

    Parameters
    ----------
    df : DataFrame
        DataFrame of all needed data.

    Returns
    -------
    proc_data
        Processed DataFrame with data ready to machine learning.
    """
    dummies_cols = ["gender", "relevent_experience", "enrolled_university",
                    "major_discipline", "company_size"]
    df = process_dummies_columns(df, dummies_cols)

    encoded_cols = ["city", "city_development_index", "experience", "company_type",
                    "education_level", "last_new_job", "training_hours"]
    df = encode_labels(df, encoded_cols)

    insignificant_cols = ["enrollee_id"]
    df = drop_columns(df, insignificant_cols)

    return df


def process_dummies_columns(df: pd.DataFrame, columns: list[str]):
    """
    Process DataFrame columns using dummies/one_hot_encoding.

    Parameters
    ----------
    df : DataFrame
        DataFrame with columns to process.

    columns : list[str]
        List of columns labels to process.

    Returns
    -------
    df
        DataFrame with processed columns.
    """
    processed_cols = pd.get_dummies(df[columns], drop_first=True)
    for col in processed_cols.columns:
        df[col] = processed_cols[col]
    df = df.drop(columns, axis=1)
    return df


def encode_labels(df: pd.DataFrame, columns: list[str]):
    """
    Using LabelEncoder encode all values in columns into numeric unique values.

    Parameters
    ----------
    df : DataFrame
        DataFrame with columns to encode.

    columns : list[str]
        List of columns labels to encode.

    Returns
    -------
    df
        DataFrame with encoded columns values.
    """
    le = LabelEncoder()
    for column in columns:
        df[column] = le.fit_transform(df[column].values)
    return df


def process_relevent_exp(df: pd.DataFrame):
    """
    Process DataFrame "relevent_experience" column using created mapping dict.

    Parameters
    ----------
    df : DataFrame
        DataFrame with column to process.

    Returns
    -------
    df
        Processed "relevent_experience" column as DataFrame.
    """
    exp_mapping = {"No relevent experience": 0,
                   "Has relevent experience": 1}
    exp = df["relevent_experience"]
    df["relevent_experience"] = exp.map(exp_mapping)
    return df["relevent_experience"]


def process_enrolled_university(df: pd.DataFrame):
    """
    Process DataFrame "enrolled_university" column using created mapping dict.

    Parameters
    ----------
    df : DataFrame
        DataFrame with column to process.

    Returns
    -------
    df
        Processed "enrolled_university" column as DataFrame.
    """
    university_mapping = {"None": 0,
                          "no_enrollment": 1,
                          "Part time course": 2,
                          "Full time course": 3}
    values = df["enrolled_university"]
    df["enrolled_university"] = values.map(university_mapping)
    return df["enrolled_university"]


def process_education_level(df: pd.DataFrame):
    """
    Process DataFrame "education_level" column using created mapping dict.

    Parameters
    ----------
    df : DataFrame
        DataFrame with column to process.

    Returns
    -------
    df
        Processed "education_level" column as DataFrame.
    """
    education_mapping = {"None": 0,
                         "Primary School": 1,
                         "High School": 2,
                         "Masters": 3,
                         "Graduate": 4,
                         "Phd": 5}
    values = df["education_level"]
    df["education_level"] = values.map(education_mapping)
    return df["education_level"]


def prepare_train_test_data(df: pd.DataFrame, reductioner: str = None):
    """
    Prepare tran and test sets ready to machine learning.

    Parameters
    ----------
    df : DataFrame
        DataFrame with train/test data.

    reductioner : str {default: None}
        Dimensionality reduction algorithm.
        Can be one of listed: ["LDA", "PCA"]. Could be None.

    Returns
    -------
    (X_train, y_train, X_test, y_test)
        Tuple of split data.
    """
    no_target_cols = list(filter(lambda x: x != "target", df.columns))

    X = df[no_target_cols].values
    y = df["target"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)

    pipe = make_pipeline(StandardScaler())
    pipe.fit(X_train)
    X_train = pipe.transform(X_train)
    X_test = pipe.transform(X_test)

    if reductioner == "pca":
        pca = PCA(n_components=5)
        X_train = pca.fit_transform(X_train)
        X_test = pca.transform(X_test)
    elif reductioner == "lda":
        lda = LDA(n_components=1)
        lda.fit(X_train, y_train)
        X_train = lda.transform(X_train)
        X_test = lda.transform(X_test)

    return X_train, y_train, X_test, y_test
