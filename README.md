# quantlab-data-pull

QuantLab 数据拉取辅助流水线：用 GitHub Actions runner 的海外 IP 拉取 A 股日线数据（baostock），分批产出 CSV artifacts，本地下载合并。

## 用法

```
gh workflow run pull.yml -f batch_start=0 -f batch_end=250
gh run watch
gh run download <run-id>
```

## 说明

- 每批 250 只（约 15-20 分钟/批），5200 只 = 21 批
- 单登录+顺序查询（gentle 模式），避免触发服务端封禁
- 产物为公共行情数据（OHLCV+成交额，前复权），无敏感信息
