# Redactions in this release

Literal strings identifying the recording device, the camera or the home network were replaced in the released copies only. No registered file (pre-registration, `.sha256`, hashed sample or clip list) was altered; the build aborts if a rule would touch one. Values the counter reads are not affected, which the reproduction check in README.md demonstrates.

| file | replaced | SHA256 original | SHA256 released |
|---|---|---|---|
| `01_Measurement/analysis/ablation/baseline.cell.json` | device measurement root x2; host name x1 | `4c1145d1073c84529c1cd66c8b67733609cdc04c4e29061d486e08acd585a871` | `31de0f24370ae6007057a8b114e8ecb7049449e369f63567c2420a426065387c` |
| `01_Measurement/analysis/ablation/gate_on.cell.json` | device measurement root x2; host name x1 | `96ecb856694f7a2aaa057e48592fd782cb6702c8b243f7eaf871b482810fb0d9` | `0fd9e958650a210b2d01220f726b44f429f2834465576952f706577d6be3612e` |
| `01_Measurement/analysis/ablation/only_FallChecker.cell.json` | device measurement root x2; host name x1 | `da2a3e7aebbe2339e42148006b8f617e41b4dedb49bc662b3de3f45f27107c9a` | `39f0011de93515f0da2b0ed8072c60d633e8f2c449db504d3c82e0fcdde8a33a` |
| `01_Measurement/analysis/ablation/only_HelmetChecker.cell.json` | device measurement root x2; host name x1 | `343ec55736fab1fe37df211f10b518c075c6aff819e7b96562263accf9542fd1` | `f47a41a78e920fd5ad8ecbfd17540fec93ef5162f6d0461317eb6bc1c7a2fec7` |
| `01_Measurement/analysis/ablation/only_IntrusionChecker.cell.json` | device measurement root x2; host name x1 | `f6c50ae22da5bc4b586da66d762eddac59abb0a12757f2791298f2b31b66983a` | `ef876ba6b61e95b8d50daba6e13cfd03f939e2de082668aa250bef4d6985635a` |
| `01_Measurement/analysis/ablation/only_RunningChecker_with_std.cell.json` | device measurement root x2; host name x1 | `b5f1e1c42554628c4c10fa45199a46986bb6d0ed9de995c53f14cd684a1a5a03` | `393b04d01f29ab917dc291c2734ec6710455e6ec5cf23ac4f7e7ed3580b015f2` |
| `01_Measurement/analysis/ablation/only_SmokeFireChecker.cell.json` | device measurement root x2; host name x1 | `5f339b732c1db3916e23b11283cfdfcc56c4863c2208d54006a8efb0c9ac3dc2` | `b8a32e52a2aad94aae10fb3356b1cb7b571c8798c16d57ccaf489b40102ae954` |
| `01_Measurement/analysis/tier0/manifest_rows_closed.csv` | camera LAN address x175 | `b67ae5ba028979d2acb7d72fda489758787c3e2da4adafac9629ba0aba3e7a6f` | `c99a49c1442f37e5c78864f8b49209ae23eb7a8889a006604fc4b9c1b00fd5e1` |
| `01_Measurement/runs/d5s_allocated/pass_params.json` | device measurement root x2 | `1d675576ce38ab70df2f0f579b5bea75c26bf1554ec254d391bd935a5c9a60b1` | `92f84749111dbfe31e33ee0bfe11ff491fd70dfb0d5f571fd2cdcf9266ab5e5f` |
| `01_Measurement/scripts/count_everything.py` | device home directory x1 | `58dc004e2781ad510d7d1effd0ad39f7bb18927f46759e0447fd2779aff25220` | `8a7faaa8d10d936eac9a3d3176bedaccbd525ce61243829e7efc2e6f50db0816` |
| `01_Measurement/scripts/draw_sweep_samples.py` | device measurement root x1 | `17331e9e527e75a62586577fbdc71b3083c01c186bc33c680c81873b8883097c` | `fdf5bdea099836f17be740df68a3748f5f2821054190f4334e87cb2fe8c2987c` |
| `ledger/CLAIM_LEDGER.md` | device measurement root x1; device VPN address x1 | `b49388230e601cb51da1e19d02386f5b6501151ec38306d55f24bdef35511274` | `2b34914cf14a2e13c135eab67646639da84c6f0aaf90a9450a1a716204f412a1` |
