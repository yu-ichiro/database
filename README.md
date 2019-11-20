# データベースアクセスライブラリ
Unpluggedで使っているデータベースアクセス用ライブラリ
model/以下を変えれば他のプロジェクトでも代用できそう

## 他のプロジェクトから使う時は
db_config.sample.iniをdb_config.iniにコピーして接続の設定を書く
requirements.txtをpip installしておく

## 自分のデータベースに接続する場合

まずMySQLの中にutf8mb4でデータベースを作成し、その設定を元にdb_config.iniを作成。
次にこのプロジェクト直下(`database/`)で以下を実行
```bash
export PYTHONPATH=$(pwd);cd migration;alembic revision --autogenerate -m "update"&&alembic upgrade head;rm alembic/versions/*.py;cd ..
```
