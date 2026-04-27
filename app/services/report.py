def export_books_report(books: dict) -> str:
    import pandas as pd

    df = pd.DataFrame(books.values())
    return df.to_csv(index=False)
