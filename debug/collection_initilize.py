import fino_filing as ff

storage = ff.LocalStorage(base_dir="debug/.store")
catalog = ff.Catalog(db_file_path="debug/.store/fino_catalog.db")
collection = ff.Collection(catalog=catalog, storage=storage)
