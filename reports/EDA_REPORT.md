# UNSW-NB15 Exploratory Data Analysis

## Dataset overview

- Training file: `UNSW_NB15_training-set.csv` — 175,341 rows × 45 columns.
- Testing file: `UNSW_NB15_testing-set.csv` — 82,332 rows × 45 columns.
- Train/test schema columns match: True.
- Columns with differing dtypes: none.
- Shared `id` values across provided splits: 82,332. `id` ranges are 1–175,341 in train and 1–82,332 in test; values are unique within each file, but the row numbering restarts in the test file, so the cross-file ID overlap is not a record-overlap test.

- Test rows exactly matching a training row after dropping `id` (all other columns, including labels): 4,247.

## Data quality

| Check | Training | Testing |
|---|---:|---:|
| Rows | 175,341 | 82,332 |
| Columns | 45 | 45 |
| Duplicate Rows (Excluding Id) | 67,601 | 26,387 |
| Missing Cells | 0 | 0 |
| Infinite Numeric Cells | 0 | 0 |

## Binary target balance

| Label | Meaning | Train count | Train % | Test count | Test % |
|---:|---|---:|---:|---:|---:|
| 0 | Normal | 56,000 | 31.94% | 37,000 | 44.94% |
| 1 | Attack | 119,341 | 68.06% | 45,332 | 55.06% |

## Feature inspection

### Categorical feature top values

- `proto`: tcp (79,946), udp (63,283), unas (12,084), arp (2,859), ospf (2,595), sctp (1,150), any (300), gre (225)
- `service`: - (94,168), dns (47,294), http (18,724), smtp (5,058), ftp-data (3,995), ftp (3,428), ssh (1,302), pop3 (1,105)
- `state`: INT (82,275), FIN (77,825), CON (13,152), REQ (1,991), RST (83), ECO (12), PAR (1), URN (1)

### Numeric predictor summary

```text
              dur       spkts       dpkts        sbytes        dbytes         rate        sttl        dttl         sload         dload       sloss       dloss      sinpkt      dinpkt         sjit        djit        swin         stcpb         dtcpb        dwin      tcprtt      synack      ackdat       smean       dmean  trans_depth  response_body_len  ct_srv_src  ct_state_ttl  ct_dst_ltm  ct_src_dport_ltm  ct_dst_sport_ltm  ct_dst_src_ltm  is_ftp_login  ct_ftp_cmd  ct_flw_http_mthd  ct_src_ltm  ct_srv_dst  is_sm_ips_ports
count  175341.000  175341.000  175341.000  1.753410e+05  1.753410e+05   175341.000  175341.000  175341.000  1.753410e+05  1.753410e+05  175341.000  175341.000  175341.000  175341.000   175341.000  175341.000  175341.000  1.753410e+05  1.753410e+05  175341.000  175341.000  175341.000  175341.000  175341.000  175341.000   175341.000         175341.000  175341.000    175341.000  175341.000        175341.000        175341.000      175341.000    175341.000  175341.000        175341.000  175341.000  175341.000       175341.000
mean        1.359      20.299      18.970  8.844844e+03  1.492892e+04    95406.187     179.547      79.610  7.345403e+07  6.712056e+05       4.953       6.948     985.977      88.216     4976.254     604.354     116.257  9.692504e+08  9.688770e+08     115.014       0.041       0.021       0.020     136.752     124.173        0.106           2144.292       9.306         1.304       6.194             5.384             4.206           8.730         0.015       0.015             0.133       6.956       9.101            0.016
std         6.480     136.888     110.258  1.747656e+05  1.436542e+05   165400.978     102.940     110.507  1.883574e+08  2.421312e+06      66.005      52.733    7242.246     987.093    44965.847    4061.043     127.001  1.355264e+09  1.354000e+09     126.887       0.079       0.043       0.041     204.677     258.317        0.777          54207.967      10.704         0.954       8.052             8.047             5.784          10.956         0.126       0.126             0.701       8.321      10.757            0.125
min         0.000       1.000       0.000  2.800000e+01  0.000000e+00        0.000       0.000       0.000  0.000000e+00  0.000000e+00       0.000       0.000       0.000       0.000        0.000       0.000       0.000  0.000000e+00  0.000000e+00       0.000       0.000       0.000       0.000      28.000       0.000        0.000              0.000       1.000         0.000       1.000             1.000             1.000           1.000         0.000       0.000             0.000       1.000       1.000            0.000
1%          0.000       1.000       0.000  4.600000e+01  0.000000e+00        0.000       0.000       0.000  0.000000e+00  0.000000e+00       0.000       0.000       0.001       0.000        0.000       0.000       0.000  0.000000e+00  0.000000e+00       0.000       0.000       0.000       0.000      45.000       0.000        0.000              0.000       1.000         0.000       1.000             1.000             1.000           1.000         0.000       0.000             0.000       1.000       1.000            0.000
50%         0.002       2.000       2.000  4.300000e+02  1.640000e+02     3225.807     254.000      29.000  8.796748e+05  1.447023e+03       0.000       0.000       0.280       0.006        0.000       0.000       0.000  0.000000e+00  0.000000e+00       0.000       0.000       0.000       0.000      73.000      44.000        0.000              0.000       5.000         1.000       2.000             1.000             1.000           3.000         0.000       0.000             0.000       3.000       4.000            0.000
99%        45.353     234.000     400.000  7.412540e+04  4.743678e+05  1000000.003     254.000     252.000  8.000000e+08  1.465589e+07      38.000     178.600   60000.656     441.653    28834.229    9466.019     255.000  4.201221e+09  4.198113e+09     255.000       0.277       0.156       0.145    1137.000    1252.000        1.000           3924.000      41.000         6.000      34.000            34.000            18.000          41.000         1.000       1.000             1.000      34.000      41.000            1.000
max        60.000    9616.000   10974.000  1.296523e+07  1.465555e+07  1000000.003     255.000     254.000  5.988000e+09  2.242273e+07    4803.000    5484.000   84371.496   56716.824  1460480.016  289388.270     255.000  4.294959e+09  4.294882e+09     255.000       2.519       2.100       1.521    1504.000    1458.000      172.000        6558056.000      63.000         6.000      51.000            51.000            46.000          65.000         4.000       4.000            30.000      60.000      62.000            1.000
```

### Strongest numeric correlations

| Feature 1 | Feature 2 | Correlation |
|---|---|---:|
| is_ftp_login | ct_ftp_cmd | 1.000 |
| dbytes | dloss | 0.997 |
| sbytes | sloss | 0.996 |
| swin | dwin | 0.990 |
| ct_srv_src | ct_srv_dst | 0.980 |
| dpkts | dloss | 0.979 |
| ct_dst_src_ltm | ct_srv_dst | 0.972 |
| dpkts | dbytes | 0.972 |
| spkts | sloss | 0.971 |
| ct_srv_src | ct_dst_src_ltm | 0.967 |
| spkts | sbytes | 0.964 |
| ct_dst_ltm | ct_src_dport_ltm | 0.962 |

## Modeling implications

- Use `label` as the binary target: 0 = normal and 1 = attack.
- Exclude `id`, `label`, and `attack_cat` from model features; `attack_cat` is not used in this binary task.
- Keep the provided training and testing files as separate splits for final evaluation.
- Check attack precision, attack recall, F1, and the confusion matrix alongside accuracy because class proportions differ between the supplied splits.
- Fit imputers, encoders, scaling, feature selection, and any resampling on training data only, preferably in a pipeline.
- Duplicate-row counts above ignore the `id` field, so otherwise identical flows are detected even when their row identifiers differ.
- 4,247 test rows exactly match a training row after dropping `id`; this overlap may make test metrics more optimistic for those records.
- The `id` counter restarts in the test file; exclude it as an input feature.

## Figures

| Figure | Path |
|---|---|
| Binary label counts | `reports/figures/target_distributions.png` |
| Categorical feature versus label: proto | `reports/figures/proto_by_label.png` |
| Categorical feature versus label: service | `reports/figures/service_by_label.png` |
| Categorical feature versus label: state | `reports/figures/state_by_label.png` |
| Numeric feature distributions | `reports/figures/numeric_feature_distributions.png` |
| Numeric correlation heatmap | `reports/figures/numeric_correlation_heatmap.png` |
