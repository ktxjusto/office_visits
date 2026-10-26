import logging
import re
from pathlib import Path
import pandas as pd 

from util import connect_to_db
from create_db_and_tables import ddl

folder_path = Path("./office_visits")
LOG_FILE = Path("etl.log")

log = logging.getLogger("office_visits_etl")

DATE_FORMATS = ["%Y-%m-%d", "%d-%b-%Y", "%d %B %Y"]
STANDARD_DATE = r"\d{4}-\d{2}-\d{2}"


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        filemode="w", 
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

def flag(names, raw, mask, column, reason, new=None, level=logging.WARNING):
    for idx in raw.index[mask.fillna(False).astype(bool)]:
        msg = f"[{column}] {names[idx]}: {reason} | raw={raw[idx]!r}"
        if new is not None:
            msg += f" -> {new[idx]!r}"
        log.log(level, msg)

def parse_dates(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for fmt in DATE_FORMATS:
        todo = out.isna() & s.notna()
        if not todo.any():
            break
        out[todo] = pd.to_datetime(s[todo], format=fmt, errors="coerce")
    return out


def extract() -> pd.DataFrame:
    frames = []

    if folder_path.exists() and folder_path.is_dir():
        for item in sorted(folder_path.iterdir()):
            if item.is_file() and item.suffix.lower() == ".csv":
                log.info("Reading file: %s", item.name)

                df = pd.read_csv(item, dtype=str, encoding="utf-8")
                df.columns = df.columns.str.strip().str.lower()

                frames.append(pd.DataFrame({
                    "file_name": item.name,
                    "visit_date": df["date"],
                    "visit_count": df["visit_count"],
                }))
    else:
        log.error("Folder not found: %s", folder_path)
 
    if not frames:
        log.warning("No CSV files found")
        return pd.DataFrame({
            "file_name": pd.Series(dtype="string"),
            "visit_date": pd.Series(dtype="string"),
            "visit_count": pd.Series(dtype="string"),
        })

    return pd.concat(frames, ignore_index=True)


def transform(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    names = df["file_name"]
    log.info("Transform started: %d rows", len(df))

    parts = names.str.strip().str.extract(
        r"^(?P<city>.+)_(?P<file_id>[^_]+?)(?:\.csv)?$", flags=re.IGNORECASE
    )
    flag(names, names, parts["city"].isna(), "file_name",
          "could not split into city + id; set to NULL", level=logging.ERROR)

    raw_date = df["visit_date"].astype("string").str.strip()
    date_missing = raw_date.isna() | (raw_date == "")
    raw_date = raw_date.mask(date_missing)
    standard = raw_date.str.fullmatch(STANDARD_DATE).fillna(False).astype(bool)
    parsed = parse_dates(raw_date)

    converted = ~date_missing & ~standard & parsed.notna()
    date_failed = ~date_missing & parsed.isna()

    flag(names, raw_date, date_missing, "visit_date", "missing; set to NULL")
    flag(names, raw_date, converted, "visit_date",
          "non-standard format, converted to YYYY-MM-DD",
          new=parsed.dt.strftime("%Y-%m-%d"))
    flag(names, raw_date, date_failed, "visit_date",
          "unparseable date; set to NULL", level=logging.ERROR)

    raw_count = df["visit_count"].astype("string").str.strip()
    count_missing = raw_count.isna() | (raw_count == "")
    raw_count = raw_count.mask(count_missing)

    stripped = raw_count.str.replace(r"[*,\s]", "", regex=True)
    already_clean = raw_count.str.fullmatch(r"\d+").fillna(False).astype(bool)
    cleanable = stripped.str.fullmatch(r"\d+").fillna(False).astype(bool)
    counts = pd.to_numeric(stripped.where(cleanable), errors="coerce").astype("Int64")

    cleaned = cleanable & ~already_clean
    count_failed = ~count_missing & ~cleanable

    flag(names, raw_count, count_missing, "visit_count", "missing; set to NULL")
    flag(names, raw_count, cleaned, "visit_count",
          "not a clean integer, cleaned", new=counts.astype("string"))
    flag(names, raw_count, count_failed, "visit_count",
          "not a valid count; set to NULL", level=logging.ERROR)

    out = pd.DataFrame({
        "file_id": parts["file_id"],
        "office_name": parts["city"],
        "date": parsed.dt.date,
        "visit_count": counts,
    })

    log.info(
        "Transform finished: %d rows | dates converted=%d, dates NULL=%d | "
        "counts cleaned=%d, counts NULL=%d",
        len(out), converted.sum(), (date_missing | date_failed).sum(),
        cleaned.sum(), (count_missing | count_failed).sum(),
    )
    return out 

def load(df: pd.DataFrame, table: str):
    df = df.astype(object).where(df.notna(), None)
    cols = ", ".join(df.columns)
    cur = connect_to_db()

    try:
        with cur.copy(f"COPY {table} ({cols}) FROM STDIN") as copy:
            for row in df.itertuples(index=False, name=None):
                copy.write_row(row)
        log.info("Loaded %d rows into %s", len(df), table)
    finally:
        cur.connection.close()
        log.info("Connection Closed")


def main():
    setup_logging()
    ddl()
    raw_df = extract()
    load(raw_df, "visits_raw")
    clean_df = transform(raw_df)
    load(clean_df, "visits")


if __name__ == "__main__":
    main()