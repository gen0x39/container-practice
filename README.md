# コンテナ研修最終課題


#
### 起動コマンド
```bash
$ uvicorn "filename":app --reload
$ uvicorn main:app --reload
```

### dummy data
Fake Store API
https://fakestoreapi.com/products

# loadmap
notionに記載...

# Tasks


- [] 基本
 2つ以上のアプリケーションが連携するようなHTTPサーバを動かすこと
例えば、クラスタ外からアクセスできるサービスAと、サービスAから呼び出されるサービスBのようなイメージです
アプリケーションの要件はどのようなものでも構いません、Vibe Codingや生成AI活用について学んでいると思うので、一から作ってみるのが良いでしょう
 アプリケーションはGitHub Actionsによって自動テストおよび静的解析が動いていること
 github.comにパブリックリポジトリを一つ作ってください
github.comのセットアップができていない人は、してもらって大丈夫です(SSH鍵を生成してアカウントに登録する, gh auth login 使う)
 コンテナイメージのビルドおよびプッシュもActionsでやってみましょう
ghcr.ioにコンテナイメージをプッシュする(やり方は調べる)
 KubernetesクラスタへのデプロイはArgoCDによって行われ、 kubectl apply を叩かないこと
 これらアプリケーションが更新されたときのデプロイフローを検討して、できるだけ自動化してみましょう
と言われても抽象的なので、具体的には以下について考えてみると良いでしょう　
アプリケーションが更新されたときに、Deploymentに紐づく各Podが再起動するにはどのような仕組みが必要でしょうか?
https://kubernetes.io/ja/docs/concepts/workloads/controllers/deployment/#updating-a-deployment を読みながら考えてみましょう
